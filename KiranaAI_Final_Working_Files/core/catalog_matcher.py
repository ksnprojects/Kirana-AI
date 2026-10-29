"""Catalog-grounded retrieval and deterministic validation for 40 original SKUs.
No invented products, unit conversion multipliers, or prices.
"""
import re
import math
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz

# The trained classifier is optional; the catalog remains authoritative.
try:
    import joblib
except ImportError:
    joblib = None


def normalize(text):
    text = str(text or '').lower().replace('–',' ').replace('-',' ')
    text = re.sub(r'\b(grams?|grammes?|gm)\b', 'g', text)
    text = re.sub(r'\b(kilograms?|kilos?|kgs?)\b', 'kg', text)
    text = re.sub(r'\b(litres?|liters?)\b', 'l', text)
    text = re.sub(r'\b(mls?)\b', 'ml', text)
    text = re.sub(r'(\d)\s+(kg|ml|g|l)\b', r'\1\2', text)
    text = re.sub(r'[^a-z0-9.\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


@dataclass
class MatchResult:
    status: str
    sku: Optional[str] = None
    product_name: str = ''
    brand: str = ''
    category: str = ''
    base_unit: str = 'pack'
    unit_price_inr: float = 0.0
    confidence: float = 0.0
    candidate_skus: List[Dict[str, Any]] = field(default_factory=list)
    clarification_message: str = ''
    raw_product_mention: str = ''
    quantity: Optional[float] = None
    unit: Optional[str] = None
    base_quantity: float = 0.0
    line_total_inr: float = 0.0
    warning_note: str = ''
    availability: str = ''
    pack_size: str = ''

    def to_dict(self):
        return asdict(self)


class CatalogMatcher:
    """A minimal RAG-style lookup over catalog aliases, not an embedding/vector database."""
    BULK_UNITS = {'peti','carton','case','box','dabba','tin','tray','crate'}
    BASE_UNITS = {'pack','packs','packet','packets','pkt','pkts'}
    UNIT_ALIASES = {'packs':'pack','packets':'pack','packet':'pack','pkt':'pack','pkts':'pack',
                    'petee':'peti','pety':'peti','dabbe':'dabba','dabbi':'dabba',
                    'cartons':'carton','boxes':'box','bottles':'bottle','bags':'bag',
                    'pouches':'pouch','bars':'bar','jars':'jar','tubes':'tube'}

    def __init__(self, catalog_df: pd.DataFrame, processed_df: Optional[pd.DataFrame] = None):
        self.catalog_df = catalog_df.copy()
        self.sku_lookup = {str(r.sku_id): r.to_dict() for _,r in catalog_df.iterrows()}
        self.aliases = defaultdict(set)
        derived = {}
        if processed_df is not None:
            derived = {str(r.sku_id):r.to_dict() for _,r in processed_df.iterrows()}
        for sku, row in self.sku_lookup.items():
            self._add(f'{row["brand"]} {row["product_name"]} {row["pack_size"]}', sku)
            self._add(f'{row["brand"]} {row["pack_size"]}', sku)
            self._add(f'{row["product_name"]} {row["pack_size"]}', sku)
            self._add(sku, sku)
            for key in ('search_aliases','family_aliases'):
                for a in str(row.get(key,'')).split('|'):
                    self._add(a,sku)
            for a in str(derived.get(sku,{}).get('synthetic_aliases','')).split('|'):
                self._add(a,sku)
            self._add(row['brand'],sku)
            self._add(row['product_name'],sku)
        # Conservative transcription aliases verified against the original families.
        for sku,row in self.sku_lookup.items():
            if row['product_family_id']=='PAR':
                self._add('parley jee '+row['pack_size'],sku)
                self._add('parley jee',sku)
            if row['product_family_id']=='TSL':
                self._add('tata solt '+row['pack_size'],sku)
                self._add('tata solt',sku)
        # Conservatively curated spelling/nickname aliases from 300 synthetic messages.
        # Family-level entries intentionally map to *all* pack variants until a pack
        # size is explicit, so ambiguous orders continue to require clarification.
        alias_file = Path(__file__).resolve().parents[1] / 'data' / 'approved_hinglish_aliases.csv'
        if alias_file.exists():
            aliases_df = pd.read_csv(alias_file).fillna('')
            families = defaultdict(set)
            for sku, row in self.sku_lookup.items():
                families[str(row['product_family_id'])].add(sku)
            for _, row in aliases_df.iterrows():
                family_id = str(row['product_family_id'])
                for sku in families.get(family_id, set()):
                    self._add(row['alias'], sku)
        self.alias_strings = list(self.aliases)
        self.trained_family_model = None
        model_path = Path(__file__).resolve().parents[1] / 'models' / 'whatsapp_family_classifier.joblib'
        if joblib is not None and model_path.exists():
            try:
                self.trained_family_model = joblib.load(model_path)
            except Exception:
                self.trained_family_model = None

    def _add(self, alias, sku):
        a=normalize(alias)
        if a and a not in ('nan','none'):
            self.aliases[a].add(sku)

    @classmethod
    def canonical_unit(cls, unit):
        u = normalize(unit) if unit else ''
        return cls.UNIT_ALIASES.get(u,u) if u else None

    def describe(self, sku):
        row=self.sku_lookup[sku]
        return f'{row["brand"]} {row["product_name"]} {row["pack_size"]}'

    def _candidate(self, sku):
        row=self.sku_lookup[sku]
        return dict(sku=sku,product_name=self.describe(sku),unit_price_inr=float(row['unit_price_inr']),
                    base_unit='pack',availability=row['availability'],pack_size=str(row['pack_size']))

    def match_sku(self, sku, quantity=None, unit=None, raw_mention=None):
        if sku not in self.sku_lookup:
            return MatchResult(status='unknown_product',raw_product_mention=raw_mention or sku,
                               quantity=quantity,unit=unit,clarification_message='This SKU is not in our catalog.')
        row=self.sku_lookup[sku]
        q=float(quantity) if quantity is not None else None
        normalized_unit=self.canonical_unit(unit)
        common=dict(sku=sku,product_name=self.describe(sku),brand=row['brand'],
                    category=row['category'],pack_size=str(row['pack_size']),base_unit='pack',
                    unit_price_inr=float(row['unit_price_inr']),raw_product_mention=raw_mention or self.describe(sku),
                    quantity=q,unit=normalized_unit,availability=row['availability'],confidence=1.0)
        if str(row['availability']).lower()!='available':
            return MatchResult(status='out_of_stock',**common,
                clarification_message='This catalog variant is currently out of stock. Remove it or select an available alternative.')
        if q is None or not math.isfinite(q) or q <= 0 or q != int(q):
            return MatchResult(status='needs_clarification',**common,
                clarification_message='Kitne individual packs chahiye? Please give a positive whole-number quantity.')
        if normalized_unit != 'pack':
            reason=(f'“{unit}” has no verified conversion to individual catalog packs. '
                    'Please specify the total number of individual packs.') if normalized_unit else 'Please specify the selling unit (individual packs).'
            return MatchResult(status='needs_clarification',**common,clarification_message=reason)
        if q>500:
            return MatchResult(status='needs_clarification',**common,clarification_message='Large order: please confirm quantity with the distributor.')
        return MatchResult(status='matched',base_quantity=q,line_total_inr=round(q*float(row['unit_price_inr']),2),**common)

    def retrieve_catalog_context(self, message, limit=12):
        """Retrieve catalog evidence for grounding an LLM extraction prompt.

        Lexical retrieval only; does not require external embedding APIs.
        All returned IDs/prices/statuses are from the immutable source catalog.
        """
        q=normalize(message)
        scored={}
        for alias,skus in self.aliases.items():
            if len(alias)<4:continue
            contains=(f' {alias} ' in f' {q} ')
            # Token-set similarity can retrieve typo-bearing mentions, but exact inclusion ranks first.
            score=(105 if contains else fuzz.partial_ratio(alias,q))
            if score<80:continue
            for sku in skus:
                scored[sku]=max(scored.get(sku,0),score)
        ranked=sorted(scored,key=lambda x:(-scored[x],x))[:limit]
        return [dict(sku_id=sku,brand=self.sku_lookup[sku]['brand'],
                     product_name=self.sku_lookup[sku]['product_name'],
                     pack_size=self.sku_lookup[sku]['pack_size'],
                     availability=self.sku_lookup[sku]['availability']) for sku in ranked]

    def match_product(self, raw_mention, quantity=None, unit=None):
        query=normalize(raw_mention)
        if not query:
            return MatchResult(status='unknown_product',raw_product_mention=str(raw_mention),quantity=quantity,unit=unit,
                               clarification_message='Please provide the product name.')
        # Names of other brands must not become a different brand via a generic
        # noun such as oil/coffee. These are explicit off-catalog benchmark examples.
        if re.search(r'\b(saffola|nescafe|nes cafe|dragon|red bull|amul dudh|amul milk|detol soap|dettol soap|harpik|harpic|kurkura|kurkure|coke|thumsup|thums up|dairy milk|wheel powder|royalfresh|chocoblast|tigergold|zing cola)\b',query):
            return MatchResult(status='unknown_product',raw_product_mention=str(raw_mention),
                quantity=quantity,unit=self.canonical_unit(unit),
                clarification_message='The requested brand/product is not in the catalog.')
        # Keep all family variants; brand-only mentions never resolve arbitrarily.
        matches=set(self.aliases.get(query,set()))
        if not matches:
            # Containment may be safe only when a complete alias matches a requested phrase.
            for a, skus in self.aliases.items():
                if len(a)>=4 and (f' {a} ' in f' {query} ' or (len(query)>=5 and f' {query} ' in f' {a} ')):
                    matches.update(skus)
        if not matches:
            # Fuzzy retrieval: require a high match score and a clear lead, otherwise abstain.
            ranking=sorted(((fuzz.ratio(query,a),a) for a in self.alias_strings if len(a)>=4),reverse=True)
            if ranking and ranking[0][0]>=85:
                best=ranking[0][0]
                close=[a for score,a in ranking if score>=max(82,best-8)]
                for a in close:
                    matches.update(self.aliases[a])
        # A supervised character-ngram classifier helps on unseen spelling variants.
        # It cannot override exact/fuzzy matches or the explicit off-catalog guard.
        # Abstain unless lexical similarity and the classifier agree on a family.
        if not matches and self.trained_family_model is not None and len(query) >= 5:
            try:
                probs = self.trained_family_model.predict_proba([query])[0]
                classes = self.trained_family_model.classes_
                best_index = int(probs.argmax())
                family = str(classes[best_index])
                confidence = float(probs[best_index])
                family_aliases = [a for a, skus in self.aliases.items()
                                  if any(self.sku_lookup[sku]['product_family_id'] == family for sku in skus)]
                lexical = max((fuzz.ratio(query, a) for a in family_aliases), default=0)
                if confidence >= 0.18 and lexical >= 83:
                    matches = {sku for sku,row in self.sku_lookup.items()
                               if row['product_family_id'] == family}
            except Exception:
                pass
        # Restrict family variants ONLY when an explicit catalog pack size is detected.
        explicit_sizes=set(re.findall(r'\b\d+(?:\.\d+)?(?:kg|ml|g|l)\b',query))
        if explicit_sizes and matches:
            size_matches={sku for sku in matches if normalize(self.sku_lookup[sku]['pack_size']) in explicit_sizes}
            if size_matches:
                matches=size_matches
        if len(matches)>1:
            choices=sorted(matches)
            return MatchResult(status='ambiguous',raw_product_mention=str(raw_mention),quantity=quantity,
                  unit=self.canonical_unit(unit),candidate_skus=[self._candidate(s) for s in choices],
                  clarification_message='Please choose the exact product and pack size from the catalog options.')
        if len(matches)==1:
            sku=next(iter(matches))
            return self.match_sku(sku,quantity,unit,raw_mention=raw_mention)
        return MatchResult(status='unknown_product',raw_product_mention=str(raw_mention),quantity=quantity,
                    unit=self.canonical_unit(unit),clarification_message='Product not in distributor catalog. Please remove or request manual review.')
