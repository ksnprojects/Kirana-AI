"""
KiranaAI: Professional Orders & Receipts View
Renders confirmed distributor orders with structured tabular summaries and a single-block HTML commercial receipt.
"""
import html
import streamlit as st
import pandas as pd

def render_orders_view(order_manager, stores_df):
    orders = order_manager.confirmed_orders_log

    # Top summary metrics
    total_val = sum(o.get('grand_total_inr', 0) for o in orders)
    total_units = sum(o.get('total_base_units', 0) for o in orders)

    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.75rem;">
        <div>
            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #172334;">Orders & Dispatch Ledger</h3>
            <p style="margin: 0; font-size: 0.8rem; color: #64748B;">Orders confirmed during the current session (simulated wholesale operations).</p>
        </div>
        <div>
            <span class="pill pill-gray">Simulation Mode</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num">{len(orders)}</div>
            <div class="kpi-label">Confirmed Orders</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num">₹{total_val:,.2f}</div>
            <div class="kpi-label">Session Order Value</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num">{int(total_units)}</div>
            <div class="kpi-label">Total Packs Confirmed</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-metric-card">
            <div class="kpi-num" style="color: #0F766E;">40 SKUs</div>
            <div class="kpi-label">Catalog-Grounded</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    if not orders:
        st.markdown("""
        <div class="saas-card" style="text-align: center; padding: 2.5rem 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📦</div>
            <h4 style="margin: 0; font-weight: 600; color: #172334;">No Confirmed Orders Yet</h4>
            <p style="font-size: 0.85rem; color: #64748B; margin-top: 0.25rem; max-width: 440px; margin-left: auto; margin-right: auto;">
                Orders confirmed in the Order Desk will appear here with itemized delivery receipts and session records.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Left: Order Summary List, Right: Formatted Receipt
    col_left, col_right = st.columns([1.1, 1], gap="medium")

    with col_left:
        st.markdown("""
        <div class="saas-card-header" style="margin-bottom: 0.5rem;">
            <h4 class="saas-card-title">Order Ledger</h4>
            <span class="pill pill-teal">In-Session Log</span>
        </div>
        """, unsafe_allow_html=True)

        summary_rows = []
        for o in orders:
            s_name = o.get('store_name') or o.get('store_id')
            summary_rows.append({
                'Order ID': o['order_id'],
                'Retailer': f"{o['store_id']} - {s_name}",
                'Items': f"{len(o.get('items_detail', []))} products ({int(o.get('total_base_units', 0))} packs)",
                'Total': f"₹{o['grand_total_inr']:,.2f}",
                'Status': 'Confirmed (Simulated)'
            })
        
        df_display = pd.DataFrame(summary_rows)
        st.dataframe(df_display, hide_index=True, use_container_width=True)

        order_ids = [o['order_id'] for o in orders]
        selected_order_id = st.selectbox(
            "Select Order to View Commercial Receipt:",
            order_ids,
            index=len(order_ids) - 1,
            format_func=lambda x: f"{x} — ₹{next((o['grand_total_inr'] for o in orders if o['order_id'] == x), 0):,.2f}"
        )

    with col_right:
        selected_order = next((o for o in orders if o['order_id'] == selected_order_id), orders[-1])
        store_id = selected_order.get('store_id', 'Unknown')
        store_match = stores_df[stores_df.store_id == store_id]
        store_name = store_match.iloc[0]['store_name'] if not store_match.empty else selected_order.get('store_name', store_id)
        store_loc = store_match.iloc[0]['location'] if not store_match.empty and 'location' in store_match.columns else 'Retailer Account'
        items = selected_order.get('items_detail', [])

        # Build table rows safely inside a single HTML string
        table_rows_html = []
        for item in items:
            p_name = html.escape(str(item.get('product_name') or item.get('raw_product_mention') or 'Catalog Item'))
            sku = html.escape(str(item.get('sku') or item.get('matched_sku') or '—'))
            qty = int(item.get('quantity') or 0)
            rate = float(item.get('unit_price_inr') or 0)
            amt = float(item.get('line_total_inr') or (qty * rate))
            table_rows_html.append(f"""
            <tr>
                <td style="font-weight: 500; font-size: 0.825rem; padding: 0.5rem 0.4rem; border-bottom: 1px solid #F1F5F9;">{p_name}</td>
                <td style="padding: 0.5rem 0.4rem; border-bottom: 1px solid #F1F5F9;"><span class="pill pill-gray" style="font-size: 0.65rem;">{sku}</span></td>
                <td style="text-align: right; font-weight: 600; padding: 0.5rem 0.4rem; border-bottom: 1px solid #F1F5F9;">{qty}</td>
                <td style="text-align: right; color: #64748B; padding: 0.5rem 0.4rem; border-bottom: 1px solid #F1F5F9;">₹{rate:,.2f}</td>
                <td style="text-align: right; font-weight: 600; color: #172334; padding: 0.5rem 0.4rem; border-bottom: 1px solid #F1F5F9;">₹{amt:,.2f}</td>
            </tr>
            """)
        
        all_rows_str = "".join(table_rows_html)
        safe_store_name = html.escape(str(store_name))
        safe_store_loc = html.escape(str(store_loc))
        safe_order_id = html.escape(str(selected_order['order_id']))
        ts_val = selected_order.get('confirmation_timestamp') or selected_order.get('timestamp') or 'Today'
        safe_timestamp = html.escape(str(ts_val))
        grand_total_str = f"₹{selected_order.get('grand_total_inr', 0):,.2f}"
        total_packs_str = f"{int(selected_order.get('total_base_units', 0))} packs"

        # Assemble full invoice in ONE SINGLE valid HTML block
        receipt_full_html = f"""<div class="invoice-card">
<div class="invoice-header">
<div>
<h3 class="invoice-title">KiranaAI Order Receipt</h3>
<div class="invoice-sub">Commercial Delivery Challan & Order Confirmation</div>
</div>
<div style="text-align: right;">
<span class="pill pill-green">✓ Confirmed (Simulated)</span>
<div style="font-size: 0.75rem; color: #64748B; margin-top: 0.25rem;">{safe_timestamp}</div>
</div>
</div>

<div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.75rem; background: #F8FAFC; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #E2E8F0;">
<div>
<div style="color: #64748B; font-size: 0.7rem; text-transform: uppercase; font-weight: 600;">Bill To / Retailer</div>
<div style="font-weight: 600; color: #172334;">{safe_store_name}</div>
<div style="color: #64748B; font-size: 0.75rem;">Account: {html.escape(store_id)} · {safe_store_loc}</div>
</div>
<div style="text-align: right;">
<div style="color: #64748B; font-size: 0.7rem; text-transform: uppercase; font-weight: 600;">Order Reference</div>
<div style="font-weight: 600; color: #0F766E;">{safe_order_id}</div>
<div style="color: #64748B; font-size: 0.75rem;">Wholesale FMCG Dispatch</div>
</div>
</div>

<table class="invoice-table" style="width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 0.75rem 0;">
<thead>
<tr>
<th style="width: 45%; text-align: left; padding: 0.4rem; border-bottom: 1px solid #E2E8F0; color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Product Description</th>
<th style="width: 15%; text-align: left; padding: 0.4rem; border-bottom: 1px solid #E2E8F0; color: #64748B; font-size: 0.75rem; text-transform: uppercase;">SKU</th>
<th style="width: 12%; text-align: right; padding: 0.4rem; border-bottom: 1px solid #E2E8F0; color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Qty</th>
<th style="width: 14%; text-align: right; padding: 0.4rem; border-bottom: 1px solid #E2E8F0; color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Rate</th>
<th style="width: 14%; text-align: right; padding: 0.4rem; border-bottom: 1px solid #E2E8F0; color: #64748B; font-size: 0.75rem; text-transform: uppercase;">Amount</th>
</tr>
</thead>
<tbody>
{all_rows_str}
</tbody>
</table>

<div class="order-financial-card" style="margin-top: 0.75rem;">
<div class="fin-row">
<span>Subtotal ({total_packs_str})</span>
<span style="font-weight: 600; color: #172334;">{grand_total_str}</span>
</div>
<div class="fin-row">
<span>Wholesale Unit Basis</span>
<span>Catalog Rates</span>
</div>
<div class="fin-total-row">
<span>Order Total (INR)</span>
<span>{grand_total_str}</span>
</div>
</div>

<div style="margin-top: 0.75rem; padding-top: 0.5rem; border-top: 1px dashed #E2E8F0; display: flex; justify-content: space-between; align-items: center;">
<span class="pill pill-gray" style="font-size: 0.7rem;">Simulated Order · Internal Record</span>
<span style="font-size: 0.7rem; color: #94A3B8;">KiranaAI v2.4</span>
</div>
</div>"""
        clean_html = "\n".join(line.strip() for line in receipt_full_html.splitlines())
        if hasattr(st, 'html'):
            st.html(clean_html)
        else:
            st.markdown(clean_html, unsafe_allow_html=True)

        with st.expander("🛠️ Audit & Developer Payload (Simulation Data)", expanded=False):
            st.caption("Raw audit record for academic inspection:")
            st.json({k: v for k, v in selected_order.items() if k != 'items_detail'})
