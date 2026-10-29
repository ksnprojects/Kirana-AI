# Supplementary WhatsApp dataset integration

## Scope

This package imports all 300 rows from the uploaded `kirana_ai_synthetic_dataset.zip / whatsapp_orders.csv` while preserving the application's **40-SKU product catalog**, its existing original 40 labelled messages, and the entire Streamlit interface.

- Original labelled dataset: `data/labelled_whatsapp_messages.csv` (40 messages).
- Imported source messages: `data/supplemental_whatsapp_orders_300.csv` (300 messages; `EXT_` prefixes prevent ID collisions).
- `DataLoader.get_whatsapp_orders()` combines the two collections, exposing 340 rows to existing data consumers without editing any UI files.
- The `data/llm_evaluation_cases.csv` 40-message held-out benchmark is **not modified**. The current dashboard's fixed benchmark figures remain for that prior 40-message experiment; they are **not new 300-message Gemini scores**.

## Compatibility: important

The source dataset describes **20 different SKUs** (SKU001–SKU020), whereas this KiranaAI application has **40 original SKU IDs** (MAG001, etc.). The new data is valuable as a diverse message corpus, but its existing `ground_truth_line_items_json` **cannot be treated as equivalent 40-SKU ground truth**. It is preserved unmodified in `source_ground_truth_json` and each row is marked `evaluation_eligible=False`, `validation_status=unreviewed_external_dataset`.

Source store IDs S001–S030 were normalized to STORE001–STORE030 solely to satisfy the application namespace, **not as proof that the original stores correspond to the application stores or that their history is interchangeable**. Do not use supplemental store identity as ground truth for replenishment.

Many source messages use `peti` / `dabba` units and the original 20-SKU catalog's wholesale conversion assumptions. This application's safety policy does not assume those factors, so clarification may be required even when the source label says `matched`.

## Before making 300-message performance claims

Independently annotate the new corpus against the authoritative 40-SKU catalog, stratify by unique or near-duplicate text, and evaluate the offline parser and live Gemini separately. There are repeated message texts in the new corpus. No 300-message accuracy figure is asserted.

## No dashboard changes

No `app.py` or `ui/*.py` files were modified for this integration. Product catalog, ML features, ordering model, and demo scenarios remain unchanged.
