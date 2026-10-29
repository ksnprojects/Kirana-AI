"""KiranaAI configuration: authoritative 40-SKU catalog and deployment settings."""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'

CATALOG_FILE = DATA_DIR / 'product_catalog.csv'
CATALOG_PROCESSED_FILE = DATA_DIR / 'product_catalog_processed.csv'
STORE_MASTER_FILE = DATA_DIR / 'store_profiles.csv'
STORE_HISTORY_FILE = DATA_DIR / 'synthetic_order_history.csv'
REORDER_DATASET_FILE = DATA_DIR / 'store_product_weekly_features.csv'
WHATSAPP_ORDERS_FILE = DATA_DIR / 'labelled_whatsapp_messages.csv'
EVALUATION_CASES_FILE = DATA_DIR / 'llm_evaluation_cases.csv'
EDGE_CASES_FILE = DATA_DIR / 'catalog_edge_cases.csv'

# Secure API key retrieval: Streamlit Secrets (Cloud) -> Environment Variable (.env / System)
def get_gemini_api_key():
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            if 'GEMINI_API_KEY' in st.secrets:
                return str(st.secrets['GEMINI_API_KEY']).strip()
            if 'GOOGLE_API_KEY' in st.secrets:
                return str(st.secrets['GOOGLE_API_KEY']).strip()
    except Exception:
        pass
    return (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or '').strip()

GEMINI_API_KEY = get_gemini_api_key()
DEFAULT_GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite')
# If the selected model returns HTTP 404, try one newer alternative.
GEMINI_404_FALLBACK_MODEL = os.getenv('GEMINI_404_FALLBACK_MODEL', 'gemini-3.8-flash')

DEMO_SCENARIOS = {
    'clean_order': {
        'title': 'Clean Hinglish order',
        'store_id': 'STORE001',
        'message': 'Bhai maggi 70g ke 12 packs aur Tata namak 1kg 6 packs bhej dena'
    },
    'ambiguous_order': {
        'title': 'Ambiguous order',
        'store_id': 'STORE002',
        'message': 'Bhai 4 maggi aur 3 Parle G bhej dena'
    },
    'reorder_nudge': {
        'title': 'Predictive reorder',
        'store_id': 'STORE003',
        'message': 'Bhai surf excel 500g 4 packs bhejdo'
    },
    'unknown_product': {
        'title': 'Guardrails & Block',
        'store_id': 'STORE004',
        'message': 'Bhai 3 peti Dragon Energy Drink bhej dena'
    }
}
