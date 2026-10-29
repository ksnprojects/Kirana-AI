# KiranaAI — AI-Powered Kirana Ordering Assistant (MBA Prototype)

KiranaAI is an academic, simulated order-management platform designed for a regional FMCG distributor supplying 30 kirana retail stores across 40 authoritative stock keeping units (SKUs). Developed for the **MBA Foundations of AI for Business** course, KiranaAI demonstrates how small business conversational commerce (informal WhatsApp messages) can be bridged with enterprise ERP systems via catalog-grounded AI, temporal machine learning, and human-in-the-loop guardrails.

---

## 1. Quick Start & Execution

### Prerequisites
- Python 3.10, 3.11, or 3.12 (Windows, macOS, or Linux)
- Recommended: Virtual environment (`venv`)

### Installation & Launch
```powershell
# 1. Clone or extract the project folder
cd KiranaAI_Final_Working_Files

# 2. (Optional) Create and activate a clean virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # On Linux/macOS: source .venv/bin/activate

# 3. Install required dependencies
python -m pip install -r requirements.txt

# 4. Run automated test suite (12 regression & unit tests)
python -m unittest discover -s tests -v

# 5. Launch the Streamlit application
python -m streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 2. System Architecture & AI Components

```
┌────────────────────────────────────────────────────────┐
│      Inbound Message (Hinglish / Informal English)     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│           Perimeter Guardrail & Privacy Check          │
│   (Blocks system prompt leakage & cross-store queries) │
└───────────────────────────┬────────────────────────────┘
                            │ Passed
                            ▼
┌────────────────────────────────────────────────────────┐
│               Dual-Tier Order Extraction               │
│   Tier 1: Google Gemini 3.5 Flash-Lite (When Key Present)   │
│   Tier 2: Offline Rule-Based Engine (Built-in Fallback)│
└───────────────────────────┬────────────────────────────┘
                            │ Extracted product mentions & quantities
                            ▼
┌────────────────────────────────────────────────────────┐
│           Lexical Grounding & Catalog Matcher          │
│   - RapidFuzz token matching (threshold >= 85)         │
│   - Inverted alias dictionary covering 40 SKUs         │
│   - Authoritative catalog validation gate              │
└───────────────────────────┬────────────────────────────┘
                            │ Validated SKUs & Candidate Variants
                            ▼
┌────────────────────────────────────────────────────────┐
│          Human-in-the-Loop Clarification & Draft       │
│   - Disambiguate multi-variant pack sizes              │
│   - Enforce explicit pack counts for bulk units        │
│   - Out-of-stock exclusion (BRU002, KIT002)            │
│   - Authoritative catalog price recalculation          │
└───────────────────────────┬────────────────────────────┘
                            │ Clean order draft
                            ▼
┌────────────────────────────────────────────────────────┐
│       Temporal Logistic Regression Reorder Engine      │
│   (Optional stock-out prevention nudge snapshot)       │
└───────────────────────────┬────────────────────────────┘
                            │ Order review & edit
                            ▼
┌────────────────────────────────────────────────────────┐
│         Explicit Human-in-the-Loop Confirmation        │
│   (Simulated in-session dispatch log; no real billing) │
└────────────────────────────────────────────────────────┘
```

### Retrieval & Grounding Mechanism (Verified Facts)
- **Lexical Retrieval:** The application uses **RapidFuzz Token-Ratio Matching** over an inverted dictionary of catalog aliases and product titles.
- **Lexical RAG:** For the Gemini prompt, candidate catalog entries are retrieved lexically and injected as structured context into the prompt (**Lexical RAG**).
- **No Vector DB:** The application **does NOT use vector embeddings (e.g., text-embedding-004) or vector databases (Chroma, FAISS, Pinecone)**. For a finite 40-SKU distributor catalog, deterministic lexical matching guarantees zero SKU hallucinations and ensures sub-millisecond execution without external vector infrastructure.

---

## 3. Gemini 3.5 Flash-Lite vs. Offline Mode

The application supports dual extraction modes:

1. **Offline Mode (Default):**
   - Purely rule-based lexical parser running locally with zero external API calls.
   - Enhanced to handle natural phrasing such as:
     - Quantity preceding product: `"Please send 4 Maggi 70g packets"`
     - Quantity following product: `"Maggi 70g, 3 packets"`
     - Conservative missing unit handling: returns `None` rather than guessing arbitrary pack counts.
   - The UI clearly labels when the offline parser is active.

2. **Gemini 3.5 Flash-Lite Mode:**
   - Requires a valid Google Gemini API key.
   - Uses `gemini-3.5-flash-lite` with structured Pydantic output schema (`LLMParseResult`).
   - If the API key is invalid, missing, or rate-limited, the system falls back gracefully to offline mode with an informative notice.

### How to Configure Gemini API Key Securely:
- **Option A (Streamlit Secrets - Recommended for Cloud):** Create `.streamlit/secrets.toml`:
  ```toml
  GEMINI_API_KEY = "your-actual-gemini-api-key"
  ```
- **Option B (Environment Variable / `.env`):** Create `.env`:
  ```bash
  GEMINI_API_KEY="your-actual-gemini-api-key"
  ```
- **Option C (In-App Sidebar):** Enter the key directly into the password field in the sidebar for the current session.

> [!NOTE]
> No Gemini API key is included in this repository. In offline mode, all core workflows, catalog lookups, reorder models, and demo scenarios function 100% deterministically.

---

## 4. Predictive Reorder Model

The next-week reorder recommendation system is powered by a **balanced Logistic Regression classifier** trained on 16 weeks of synthetic store ordering history:
- **Panel Structure:** 30 stores × 40 SKUs × 16 weeks = 19,200 store-SKU-week observations.
- **Features:** 4-week order frequency, 4-week average quantity, weeks since last order, store reorder propensity, and SKU demand tier.
- **Temporal Separation:**
  - Training: Weeks 1–9
  - Validation: Weeks 10–12
  - Held-out Test: Weeks 13–15
  - Week 16 snapshot is used for next-week (Week 17) operational scoring.
- **Held-Out Test Set Metrics:**
  - **Accuracy:** 84.64%
  - **Precision:** 40.26%
  - **Recall:** 99.73%
  - **F1 Score:** 0.5736
  - **ROC AUC:** 0.9621
  - **Baseline Comparison:** The logistic model significantly outperforms the naive repeat-order baseline (Baseline F1: 0.2467, Recall: 24.93%).
- **Guardrails:** Recommendations are **never** automatically added to orders. They are presented as optional suggestions requiring explicit merchant approval. Out-of-stock items (`BRU002`, `KIT002`) are strictly filtered out.

---

## 5. Four MBA Demo Scenarios

The application provides four one-click demonstration buttons in the AI Order Assistant view:

| Button | Scenario | Description & Expected Flow |
|---|---|---|
| **1. Clean Hinglish order** | Multi-item clean order | `Bhai maggi 70g ke 12 packs aur Tata namak 1kg 6 packs bhej dena` → Matches `MAG001` (12 @ ₹14 = ₹168) and `TSL002` (6 @ ₹32 = ₹192) → Validates ₹360 total → Confirmed. |
| **2. Ambiguous order** | Variant & quantity ambiguity | `Bhai 4 maggi aur 3 Parle G bhej dena` → Identifies ambiguity between 70g/140g Maggi and 65g/250g Parle-G → Prompts user to select variants → Recalculates total → Confirmed. |
| **3. Predictive reorder** | Temporal ML stock replenishment | `Bhai surf excel 500g 4 packs bhejdo` for `STORE003` → Temporal model predicts high stockout risk for Horlicks (93% score) → Displays rationale card → Optional 1-click addition. |
| **4. Guardrails & Block** | Unknown / out-of-stock safety | `Bhai 3 peti Dragon Energy Drink bhej dena` → Unknown product flagged as unverified → Order confirmation blocked until invalid item is removed. |

---

## 6. Streamlit Community Cloud Deployment Guide

The codebase is engineered to be portable and ready for deployment to **Streamlit Community Cloud**:

### Deployment Steps:
1. Push this repository to a private or public GitHub repository.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
3. Click **"New app"** and select:
   - **Repository:** `<your-username>/kirana-ai`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. In **Advanced Settings**, add your secret in the **Secrets** box:
   ```toml
   GEMINI_API_KEY = "your-actual-api-key"
   ```
5. Click **"Deploy"**.

### Portability Features:
- Complete and pinned `requirements.txt`.
- No absolute local Windows paths; all paths derive from `BASE_DIR = Path(__file__).resolve().parent`.
- API keys read from `st.secrets` first, then environment variables, with offline fallback.
- Simulated order log resides in Streamlit session state; no external database setup required.

---

## 7. Automated Test Suite

Run the full suite of regression and unit tests:
```powershell
python -m unittest discover -s tests -v
```
**Results (12/12 Passed in ~0.35s):**
- `test_clean_multi_item`: Validates multi-item extraction, pricing, and total calculation.
- `test_typo`: Tests fuzzy matching on common Hinglish misspellings.
- `test_ambiguous_and_preserved_quantity`: Ensures ambiguous variants trigger clarification while preserving user quantity.
- `test_bulk_unit_no_guess`: Enforces explicit pack verification for bulk units (`peti`, `dabba`).
- `test_unknown_unavailable`: Validates blocking of unknown SKUs and out-of-stock products (`KIT002`).
- `test_price_not_client_controlled`: Verifies that user-supplied prices cannot override authoritative catalog rates.
- `test_block_prompt_and_privacy`: Confirms blocking of system prompt exfiltration and cross-store data leakage.
- `test_conflicting_qty`: Validates clarification trigger on contradictory quantity phrases.
- `test_temporal_model`: Verifies temporal ordering, feature stability, and ML pipeline reproducibility.
- `test_source_integrity`: Confirms exactly 40 SKUs, 30 stores, and relational consistency across synthetic datasets.
- `test_natural_order_formats`: Verifies natural formats (quantity preceding or following product, comma separation).
- `test_conservative_missing_quantities_and_units`: Validates conservative null handling for missing quantity/unit tokens.

---

## 8. Academic Integrity & Non-Claims

- **Simulation Only:** All 30 store names, 16 weeks of ordering history, and WhatsApp transcripts are synthetic artifacts created for MBA coursework.
- **No Vector Embeddings:** Catalog search uses lexical RapidFuzz matching. No vector database is claimed or implemented.
- **Human Confirmation:** The system enforces human sign-off on all orders; it does not place real orders, charge credit cards, or dispatch physical goods.
