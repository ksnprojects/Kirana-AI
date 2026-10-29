# Hinglish language enhancement (300 supplemental messages)

## Scope

- Preserves the original authoritative 40-SKU catalog, all 30 stores, the reorder model, Streamlit UI, and Gemini integration.
- Adds **curated product-family aliases** in `data/approved_hinglish_aliases.csv`, incorporated into catalog matching and Gemini catalog retrieval.
- The 300 supplemental rows have incompatible 20-SKU source labels, so we **do not treat these as trusted SKU training labels**. Their typo evidence was used to curate aliases, but product identity still comes only from the 40-SKU catalog.
- This is vocabulary/lexical retrieval enhancement, **not neural model fine-tuning or retraining of Gemini**. Gemini weights are unchanged.
- No bulk-unit conversion is inferred; peti/dabba etc still need an explicit individual pack count. Missing pack sizes remain ambiguous.
- Off-catalog examples like Dettol soap, Amul milk, Nescafe and Coke are deliberately not mapped to similarly named available catalog products.

## Evaluation caveat

There are 300 supplemental records but many repeat or paraphrase the same templates. For a trustworthy estimate of out-of-sample benefit, create manually reviewed 40-SKU ground truth and group identical/near-duplicate messages before splitting. No unsupported improvement percentage is claimed.

## Verify

From the extracted project folder run `python -m unittest discover -s tests -v`. The `test_hinglish_aliases.py` cases check conservative matches and refusal to invent variants. The dashboard UI is unchanged.
