"""
KiranaAI: Professional Retailer Network View
Searchable customer directory of 30 kirana retail stores with historical volume and direct Order Desk routing.
"""
import streamlit as st
import pandas as pd

def render_stores_view(store_master_df, store_history_df):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.75rem;">
        <div>
            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #172334;">Retailer Network</h3>
            <p style="margin: 0; font-size: 0.8rem; color: #64748B;">Registered kirana retail partner accounts across regional FMCG distribution territories.</p>
        </div>
        <div>
            <span class="pill pill-teal">30 Active Accounts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calculate store aggregates
    sums = store_history_df.groupby('store_id').agg(
        order_lines=('sku_id', 'size'),
        total_packs=('quantity', 'sum'),
        simulated_spend_inr=('line_total_inr', 'sum')
    ).reset_index()

    total_spend = sums['simulated_spend_inr'].sum()
    total_lines = sums['order_lines'].sum()

    # Network KPIs
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num">{len(store_master_df)}</div>
            <div class="kpi-label">Active Retailer Accounts</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num">₹{total_spend:,.2f}</div>
            <div class="kpi-label">16-Week Historical Spend</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num">{total_lines:,}</div>
            <div class="kpi-label">Fulfilled Order Lines</div>
        </div>
        """, unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num">{(total_lines/len(store_master_df)):.0f}</div>
            <div class="kpi-label">Avg Lines per Retailer</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Filter Bar & Quick Select
    search_col, sel_col = st.columns([2, 1])
    with search_col:
        search = st.text_input('Search retailers by name, ID or location', placeholder='Search e.g. Gupta, Bandra, STORE005...', label_visibility='collapsed')
    with sel_col:
        quick_select = st.selectbox(
            'Quick Route to Order Desk',
            ['Select Store to Open Desk...'] + store_master_df['store_id'].tolist(),
            format_func=lambda s: 'Select Store to Open Desk...' if s.startswith('Select') else f"Open {s} - {store_master_df.loc[store_master_df.store_id==s, 'store_name'].iloc[0]}",
            label_visibility='collapsed'
        )
        if quick_select != 'Select Store to Open Desk...':
            st.session_state.selected_store_id = quick_select
            st.session_state['nav_target'] = 'Order Desk'
            st.rerun()

    merged = store_master_df.merge(sums, on='store_id', how='left').fillna(0)
    view = merged.copy()

    if search.strip():
        q = search.strip().lower()
        search_cols = ['store_id', 'store_name', 'location']
        mask = view[search_cols].fillna('').astype(str).apply(lambda c: c.str.lower().str.contains(q, regex=False)).any(axis=1)
        view = view[mask]

    # Formatted display table
    display_df = view[['store_id', 'store_name', 'location', 'order_lines', 'total_packs', 'simulated_spend_inr']].copy()
    display_df.columns = ['Store ID', 'Store Name', 'Territory / Location', 'Order Lines', 'Packs Ordered', 'Historical Spend (₹)']
    display_df['Historical Spend (₹)'] = display_df['Historical Spend (₹)'].apply(lambda x: f"₹{x:,.2f}")
    display_df['Packs Ordered'] = display_df['Packs Ordered'].apply(lambda x: f"{int(x):,}")

    st.dataframe(display_df, hide_index=True, use_container_width=True)

    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 0.65rem 0.85rem; font-size: 0.775rem; color: #64748B; margin-top: 0.5rem;">
        <strong>Account Integration:</strong> Select any store from the dropdown above to load its account context directly into the Order Desk.
    </div>
    """, unsafe_allow_html=True)
