"""
KiranaAI: Professional Product Catalog View
Compact, searchable inventory catalog for distributor operations with brand and availability filters.
"""
import streamlit as st
import pandas as pd

def render_catalog_view(catalog_df):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.75rem;">
        <div>
            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #172334;">Product Catalog & Inventory</h3>
            <p style="margin: 0; font-size: 0.8rem; color: #64748B;">Authoritative distributor master catalog with wholesale unit pricing and real-time inventory status.</p>
        </div>
        <div>
            <span class="pill pill-teal">Master Catalog</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inventory KPI strip
    total_skus = len(catalog_df)
    avail_skus = int((catalog_df.availability == 'available').sum())
    oos_skus = total_skus - avail_skus
    categories = sorted(catalog_df['category'].dropna().unique().tolist())
    brands = sorted(catalog_df['brand'].dropna().unique().tolist())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num">{total_skus}</div>
            <div class="kpi-label">Total Catalog SKUs</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num" style="color: #15803D;">{avail_skus}</div>
            <div class="kpi-label">Active / In Stock</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num" style="color: #DC2626;">{oos_skus}</div>
            <div class="kpi-label">Out of Stock (BRU002, KIT002)</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num">{len(categories)}</div>
            <div class="kpi-label">Product Categories</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Search & Filtering Bar
    f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
    with f1:
        query = st.text_input('Search by name, brand, SKU or alias', placeholder='Search e.g. Maggi, Salt, TSL002...', label_visibility='collapsed')
    with f2:
        sel_cat = st.selectbox('Category Filter', ['All Categories'] + categories, label_visibility='collapsed')
    with f3:
        sel_brand = st.selectbox('Brand Filter', ['All Brands'] + brands, label_visibility='collapsed')
    with f4:
        sel_stock = st.selectbox('Stock Status', ['All Statuses', 'In Stock', 'Out of Stock'], label_visibility='collapsed')

    view = catalog_df.copy()

    # Apply category filter
    if sel_cat != 'All Categories':
        view = view[view.category == sel_cat]

    # Apply brand filter
    if sel_brand != 'All Brands':
        view = view[view.brand == sel_brand]

    # Apply stock filter
    if sel_stock == 'In Stock':
        view = view[view.availability == 'available']
    elif sel_stock == 'Out of Stock':
        view = view[view.availability != 'available']

    # Apply search text query
    if query.strip():
        q = query.strip().lower()
        search_cols = ['sku_id', 'brand', 'product_name', 'search_aliases', 'family_aliases', 'pack_size']
        mask = view[search_cols].fillna('').astype(str).apply(lambda c: c.str.lower().str.contains(q, regex=False)).any(axis=1)
        view = view[mask]

    # Prepare formatted display table
    display_df = view[['sku_id', 'brand', 'product_name', 'category', 'pack_size', 'unit_price_inr', 'availability']].copy()
    display_df.columns = ['SKU', 'Brand', 'Product Name', 'Category', 'Pack Size', 'Unit Price (₹)', 'Inventory Status']
    display_df['Unit Price (₹)'] = display_df['Unit Price (₹)'].apply(lambda x: f"₹{x:,.2f}")
    display_df['Inventory Status'] = display_df['Inventory Status'].apply(lambda x: '✓ In Stock' if x == 'available' else '✕ Out of Stock')

    st.dataframe(display_df, hide_index=True, use_container_width=True)

    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 0.65rem 0.85rem; font-size: 0.775rem; color: #64748B; margin-top: 0.5rem;">
        <strong>Wholesale Unit Policy:</strong> Pack sizes (e.g. 70g, 250g, 1kg) define authoritative catalog SKUs. 
        Bulk wholesale units (such as <em>peti</em> or <em>dabba</em>) are blocked until an explicit individual pack count is verified by the sales team, ensuring zero billing discrepancies.
    </div>
    """, unsafe_allow_html=True)
