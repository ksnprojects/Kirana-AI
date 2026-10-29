"""Language normalization regression cases grounded in supplemental message examples."""
import unittest
from pathlib import Path
import sys, types
if 'streamlit' not in sys.modules:
    try:
        import streamlit
    except ImportError:
        stub = types.ModuleType('streamlit')
        stub.cache_resource = lambda f: f
        sys.modules['streamlit'] = stub
import pandas as pd
from core.catalog_matcher import CatalogMatcher
from core.llm_service import LLMService

class TypoAliasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.matcher = CatalogMatcher(pd.read_csv(root/'data/product_catalog.csv'), pd.read_csv(root/'data/product_catalog_processed.csv'))
        cls.llm = LLMService(cls.matcher)

    def test_observed_aliases_keep_family_ambiguity(self):
        for alias, family in [('maggie','MAG'),('surf exel','SUR'),('tata namk','TSL'),('fortun tel','FOR'),('goodday','BRI'),('colgate paste','COL')]:
            with self.subTest(alias=alias):
                r = self.matcher.match_product(alias,2,'pack')
                self.assertEqual(r.status,'ambiguous')
                self.assertTrue(r.candidate_skus)
                self.assertTrue(all(x['sku'].startswith(family) for x in r.candidate_skus))

    def test_observed_aliases_with_pack_size(self):
        for mention,sku in [('maggie 70g','MAG001'),('surf exel 500g','SUR001'),('tata namk 1kg','TSL002'),('fortun tel 1l','FOR001'),('goodday 60g','BRI001')]:
            with self.subTest(mention=mention):
                r = self.matcher.match_product(mention,4,'pack')
                self.assertEqual((r.status,r.sku),('matched',sku))

    def test_source_bulk_units_not_silently_converted(self):
        r=self.matcher.match_product('surf exel',3,'dabba')
        self.assertEqual(r.status,'ambiguous')
        r=self.matcher.match_product('surf exel 500g',3,'dabba')
        self.assertEqual(r.status,'needs_clarification')

    def test_not_mapped_to_wrong_product(self):
        for mention in ['amul dudh','dettol soap','nes cafe','kurkure','harpik']:
            with self.subTest(mention=mention):
                self.assertEqual(self.matcher.match_product(mention,3,'pack').status,'unknown_product')

    def test_original_40sku_unchanged(self):
        self.assertEqual(len(self.matcher.sku_lookup),40)
        self.assertEqual(self.matcher.match_product('maggi 70g',4,'pack').sku,'MAG001')

if __name__ == '__main__': unittest.main()
