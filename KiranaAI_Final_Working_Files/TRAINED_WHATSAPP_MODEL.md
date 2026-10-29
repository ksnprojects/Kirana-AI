# Trained WhatsApp language-recognition model

The application includes a **trained character n-gram TF-IDF + logistic regression product-family classifier** in `models/whatsapp_family_classifier.joblib`. Run `python train_whatsapp_model.py` to reproduce training. This is a trained classifier, **not Gemini fine-tuning**, and it is distinct from the existing reorder-prediction model.

## What the 300-message upload contributes

The uploaded file has 300 records but only 145 distinct message texts. Its source labels use an incompatible 20-product catalog. The training script conservatively extracts product spelling variants only when the source label corresponds to a family in the application's authoritative 40-SKU catalog. Unavailable source product families (such as Amul milk and Dettol soap) are **not** mapped to unrelated products. The model is trained on compatible extracted aliases together with the original catalog aliases and reviewed Hinglish aliases. See `models/whatsapp_training_report.json` for exact training counts. Training on the full 300 raw messages as if they were valid 40-SKU order labels would be misleading.

## Inference and safety

The classifier is loaded by `core/catalog_matcher.py` and is used only as a **conservative fallback** when exact and fuzzy alias matching do not already resolve a product. It must agree with a sufficiently similar catalog alias; otherwise the system asks for clarification or marks the product unknown. It does not invent pack sizes, units, prices or SKUs. The existing Gemini option and offline parser, order validation, reorder model and all Streamlit UI modules are unchanged.

## Evaluation and limitations

Synthetic data and repeated variants are not a credible independent accuracy benchmark. Automated regression tests check functionality and safety, but **do not establish a percentage improvement in extraction accuracy**. A robust performance claim requires manually relabelled, genuinely held-out messages from the 40-SKU catalog, grouped to avoid duplicate/near-duplicate leakage. The model artifact is bundled for deployment; retraining is not required to launch the app.

## Deploy

From the extracted `KiranaAI_Final_Working_Files` folder:

```
py -3.12 -m pip install -r requirements.txt
py -3.12 -m streamlit run app.py
```

Optional training: `py -3.12 train_whatsapp_model.py`.
