"""
KiranaAI: Professional FMCG Distributor Order Management Portal
Modern B2B SaaS interface for converting informal WhatsApp retailer messages into structured, validated orders.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')

import streamlit as st
import pandas as pd
import config
from core.data_loader import get_data_loader
from core.catalog_matcher import CatalogMatcher
from core.llm_service import LLMService
from core.reorder_model import get_reorder_predictor
from core.order_manager import OrderManager
from ui.styles import get_custom_css
from ui.order_assistant_view import render_order_assistant_view, _reset, _send
from ui.orders_view import render_orders_view
from ui.evaluation_view import render_evaluation_view
from ui.catalog_view import render_catalog_view
from ui.stores_view import render_stores_view

st.set_page_config(
    page_title='KiranaAI — Distributor Order Management',
    page_icon='🛒',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

def main():
    loader = get_data_loader()
    catalog = loader.get_catalog()
    stores = loader.get_store_master()
    history = loader.get_store_history()
    whatsapp = loader.get_whatsapp_orders()

    if 'matcher' not in st.session_state:
        st.session_state.matcher = CatalogMatcher(catalog, loader.get_catalog_processed())
    if 'llm_service' not in st.session_state:
        st.session_state.llm_service = LLMService(st.session_state.matcher)
    if 'reorder_predictor' not in st.session_state:
        st.session_state.reorder_predictor = get_reorder_predictor(loader.get_reorder_dataset(), catalog)
    if 'order_manager' not in st.session_state:
        st.session_state.order_manager = OrderManager(st.session_state.matcher)
    nav_options = [
        'Order Desk',
        'Orders',
        'Replenishment Insights',
        'Product Catalog',
        'Retailer Network'
    ]

    if 'sidebar_nav_radio' not in st.session_state:
        st.session_state['sidebar_nav_radio'] = 'Order Desk'
    if 'nav_target' in st.session_state:
        st.session_state['sidebar_nav_radio'] = st.session_state.pop('nav_target')

    service = st.session_state.llm_service

    # Top Application Header (Clean SaaS Branding - No Course References or Invented Hub Claims)
    st.markdown("""
    <div class="app-top-header">
        <div class="brand-section">
            <div class="brand-icon">K</div>
            <div>
                <h1 class="brand-title">KiranaAI</h1>
                <div class="brand-subtitle">Distributor Order Management</div>
            </div>
        </div>
        <div class="header-badges">
            <span class="pill pill-gray">Simulation Mode</span>
            <span class="pill pill-teal">40 Catalog SKUs</span>
            <span class="pill pill-gray">30 Store Network</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation & Settings
    with st.sidebar:
        st.markdown("""
        <div style="padding: 0.25rem 0.5rem 0.75rem 0.5rem; border-bottom: 1px solid #F1F5F9; margin-bottom: 0.75rem;">
            <div style="font-weight: 700; font-size: 0.95rem; color: #172334;">Operations Console</div>
            <div style="font-size: 0.75rem; color: #64748B;">Wholesale FMCG Distribution</div>
        </div>
        """, unsafe_allow_html=True)

        nav = st.radio('Navigation', nav_options, key='sidebar_nav_radio', label_visibility='collapsed')

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # API Configuration (Compact)
        with st.expander("⚙️ API Configuration", expanded=False):
            key_input = st.text_input('Gemini API Key', type='password', placeholder='Enter API key...', value=service.api_key)
            if key_input != service.api_key:
                service.set_api_key(key_input)
                st.rerun()
            force_local = st.checkbox('Force offline parser', value=False, key='force_local')
        force_local = st.session_state.get('force_local', False)

        # AI Engine Status Card (Accurate State Reporting)
        last_eng = st.session_state.get('last_engine_used', 'Not run')
        if force_local:
            status_title = "● Offline Parser (Forced Local)"
            status_bg = "#F8FAFC"
            status_color = "#475569"
            status_desc = "Local rule-based fallback active by user setting."
        elif 'Gemini' in last_eng and 'error' not in last_eng.lower() and 'fallback' not in last_eng.lower():
            status_title = f"● {last_eng} (Succeeded)"
            status_bg = "#F0FDFA"
            status_color = "#0F766E"
            status_desc = "Last order parsed via live Gemini API."
        elif 'fallback' in last_eng.lower():
            status_title = "● Offline Fallback (Gemini API Error)"
            status_bg = "#FEF3C7"
            status_color = "#B45309"
            status_desc = "API call encountered an error; local parser handled order."
        elif service.is_api_configured():
            status_title = "● Gemini Key Configured (Awaiting Request)"
            status_bg = "#F0FDFA"
            status_color = "#0F766E"
            status_desc = "API key detected. Ready for live order requests."
        else:
            status_title = "● Offline Parser (Rule-based)"
            status_bg = "#F8FAFC"
            status_color = "#475569"
            status_desc = "No API key configured. Deterministic local matching active."

        st.markdown(f"""
        <div style="background: {status_bg}; border: 1px solid #E2E8F0; border-radius: 6px; padding: 0.5rem 0.65rem; margin-bottom: 0.5rem;">
            <div style="font-size: 0.7rem; color: #64748B; font-weight: 600; text-transform: uppercase;">AI Extraction Engine</div>
            <div style="font-size: 0.8rem; font-weight: 600; color: {status_color};">{status_title}</div>
            <div style="font-size: 0.7rem; color: #64748B; margin-top: 0.15rem;">{status_desc}</div>
        </div>
        """, unsafe_allow_html=True)

        # Sole Demo Scenarios Section in the Sidebar (Single Collapsible Location)
        with st.expander("🛠️ Demo Tools", expanded=False):
            st.caption("Run standard operational scenarios or refer to the sample order format below.")
            st.markdown("<div style='font-size:0.75rem; color:#64748B; margin-bottom:0.5rem;'><strong>Sample format:</strong> Bhai Maggi 70g ke 12 packs aur Tata namak 1kg ke 6 packs bhej dena</div>", unsafe_allow_html=True)
            for i, (key, scenario) in enumerate(config.DEMO_SCENARIOS.items()):
                if st.button(f"{i+1}. {scenario['title']}", key=f"side_demo_{key}", use_container_width=True):
                    st.session_state['nav_target'] = 'Order Desk'
                    _reset(scenario['store_id'], stores, st.session_state.order_manager)
                    with st.spinner(f"Loading {scenario['title']}..."):
                        _send(scenario['message'], service, st.session_state.order_manager, st.session_state.reorder_predictor, force_local)
                    st.rerun()

        st.caption("Simulation Mode: All transactions are processed in-session. Illustrative pricing only. No live WhatsApp or ERP dispatch.")

    # Page Routing
    cur_nav = st.session_state.get('sidebar_nav_radio', 'Order Desk')
    if cur_nav == 'Order Desk':
        render_order_assistant_view(
            stores,
            st.session_state.matcher,
            service,
            st.session_state.reorder_predictor,
            st.session_state.order_manager,
            force_local
        )
    elif cur_nav == 'Orders':
        render_orders_view(st.session_state.order_manager, stores)
    elif cur_nav == 'Replenishment Insights':
        render_evaluation_view(st.session_state.reorder_predictor, whatsapp, loader.get_evaluation_cases())
    elif cur_nav == 'Product Catalog':
        render_catalog_view(catalog)
    elif cur_nav == 'Retailer Network':
        render_stores_view(stores, history)

if __name__ == '__main__':
    main()
