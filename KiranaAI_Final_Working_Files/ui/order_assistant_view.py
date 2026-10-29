"""
KiranaAI: Professional Order Desk View
Designed for FMCG distributor sales executives processing incoming Hinglish WhatsApp orders.
Two-column SaaS layout:
  Left: Conversational order intake, message stream & inline clarification.
  Right: Compact business order draft table, inline quantity editing & confirmation.
"""
import html
from datetime import datetime
import streamlit as st
import config

def _say(role, text):
    st.session_state.chat_messages.append({
        'role': role,
        'text': text,
        'ts': datetime.now().strftime('%H:%M')
    })

def _reset(store_id, stores, manager):
    found = stores[stores.store_id == store_id]
    name = found.iloc[0].store_name if not found.empty else store_id
    st.session_state.selected_store_id = store_id
    st.session_state.active_draft = manager.create_empty_draft(store_id, name)
    st.session_state.chat_messages = []
    st.session_state.active_nudge = None

def _send(message, llm, manager, predictor, force_local):
    _say('user', message)
    parsed, items, engine = llm.parse_message(message, st.session_state.chat_messages[:-1], force_local=force_local)
    st.session_state.last_engine_used = engine
    st.session_state.active_nudge = None

    if parsed.intent == 'unsafe_request':
        _say('assistant', 'Request blocked. Catalog prices and private store information cannot be overridden or disclosed.')
        return

    if parsed.intent == 'modify_order':
        _say('assistant', 'Please adjust quantities or remove items using the Order Draft controls on the right.')
        return

    if not items:
        _say('assistant', 'No valid product mentions detected. Please specify product name, pack size, and quantity.')
        return

    manager.update_draft_with_items(st.session_state.active_draft, items, merge_mode='replace')
    draft = st.session_state.active_draft

    if not draft['can_confirm']:
        unresolved_count = sum(1 for it in draft['items'] if it.get('status') != 'matched')
        _say('assistant', f"Parsed {len(items)} line item(s). {unresolved_count} item(s) require pack size or unit clarification before confirmation.")
    else:
        _say('assistant', f"Found {len(items)} product(s). Order draft ready for review. Total: ₹{draft['grand_total_inr']:,.2f}.")

    # Generate ML replenishment recommendation if draft contains matched lines
    if any(x.get('status') == 'matched' for x in draft['items']):
        existing = [x.get('sku') for x in draft['items'] if x.get('sku')]
        recs = predictor.predict_reorder_opportunities(st.session_state.selected_store_id, existing, top_k=1)
        if recs:
            st.session_state.active_nudge = recs[0]


def render_order_assistant_view(stores, matcher, llm, predictor, manager, force_local=False):
    if 'selected_store_id' not in st.session_state or st.session_state.selected_store_id not in set(stores.store_id):
        _reset('STORE001', stores, manager)
    for key, default in [('chat_messages', []), ('active_nudge', None), ('last_engine_used', 'Not run')]:
        if key not in st.session_state:
            st.session_state[key] = default
    if 'active_draft' not in st.session_state or st.session_state.active_draft.get('store_id') != st.session_state.selected_store_id:
        _reset(st.session_state.selected_store_id, stores, manager)

    # Main Order Desk Two-Column Layout (Optimized for 1366x768 display)
    col_left, col_right = st.columns([1, 1], gap="medium")

    # =========================================================================
    # LEFT COLUMN: INCOMING ORDERS & CONVERSATIONAL CAPTURE
    # =========================================================================
    with col_left:
        st.markdown("""
        <div class="saas-card-header" style="margin-bottom: 0.5rem;">
            <h4 class="saas-card-title">Incoming Order Capture</h4>
            <span class="pill pill-teal">WhatsApp Channel</span>
        </div>
        """, unsafe_allow_html=True)

        # Store Selector
        store_ids = stores.store_id.tolist()
        current_store = st.session_state.selected_store_id
        store_row = stores.loc[stores.store_id == current_store]
        store_name = store_row['store_name'].iloc[0] if not store_row.empty else current_store
        store_location = store_row['location'].iloc[0] if 'location' in store_row.columns and not store_row.empty else 'Retailer'

        selected = st.selectbox(
            'Retailer Account',
            store_ids,
            index=store_ids.index(current_store),
            format_func=lambda s: f"{s} — {stores.loc[stores.store_id==s, 'store_name'].iloc[0]}"
        )
        if selected != current_store:
            _reset(selected, stores, manager)
            st.rerun()

        # Compact Conversation Stream
        st.markdown('<div class="chat-stream-box">', unsafe_allow_html=True)
        if not st.session_state.chat_messages:
            st.markdown("""
            <div style="text-align: center; color: #94A3B8; font-size: 0.8rem; padding: 2rem 0;">
                No messages yet. Paste an incoming retailer order message below or use Demo Tools from the sidebar.
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_messages:
                safe_text = html.escape(str(msg['text']))
                safe_ts = html.escape(str(msg['ts']))
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div class="msg-retailer">
                        <div class="msg-sender">
                            <span>🏪 {html.escape(store_name)}</span>
                            <span class="msg-time">{safe_ts}</span>
                        </div>
                        <div>{safe_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="msg-assistant">
                        <div class="msg-sender" style="color: #0F766E;">
                            <span>🤖 Order Desk Assistant</span>
                            <span class="msg-time">{safe_ts}</span>
                        </div>
                        <div>{safe_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Order Input Form
        with st.form('order_input_form', clear_on_submit=True):
            raw_input = st.text_area(
                'Incoming WhatsApp Message',
                placeholder='Type or paste a retailer order message',
                height=70,
                label_visibility='collapsed'
            )
            b_proc, b_clr = st.columns([3, 1])
            with b_proc:
                submit = st.form_submit_button('Process Order', type='primary', use_container_width=True)
            with b_clr:
                clear_chat = st.form_submit_button('Clear', use_container_width=True)

        if submit and raw_input.strip():
            with st.spinner('Parsing order and matching catalog SKUs...'):
                _send(raw_input.strip(), llm, manager, predictor, force_local)
            st.rerun()

        if clear_chat:
            st.session_state.chat_messages = []
            st.rerun()

        # Engine Status Reporting (Accurate distinction of states)
        engine_str = st.session_state.last_engine_used
        if force_local:
            st.markdown("""<div style="font-size: 0.75rem; color: #475569; margin-bottom: 0.5rem;">
                ⚙️ <strong>Engine:</strong> Offline Parser (Forced local mode)
            </div>""", unsafe_allow_html=True)
        elif 'Gemini' in engine_str and 'error' not in engine_str.lower() and 'fallback' not in engine_str.lower():
            st.markdown("""<div style="font-size: 0.75rem; color: #0F766E; margin-bottom: 0.5rem;">
                ✨ <strong>Engine:</strong> {html.escape(engine_str)} (request succeeded)
            </div>""", unsafe_allow_html=True)
        elif 'fallback' in engine_str.lower():
            st.markdown(f"""<div style="font-size: 0.75rem; color: #B45309; margin-bottom: 0.5rem;">
                ⚠️ <strong>Engine:</strong> Offline Fallback ({html.escape(engine_str)})
            </div>""", unsafe_allow_html=True)
        elif llm.is_api_configured():
            st.markdown("""<div style="font-size: 0.75rem; color: #0F766E; margin-bottom: 0.5rem;">
                🔑 <strong>Engine:</strong> Gemini Key Configured (Awaiting Request)
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.5rem;">
                ⚙️ <strong>Engine:</strong> Offline Rule-Based Parser (No API Key)
            </div>""", unsafe_allow_html=True)

        # =====================================================================
        # INLINE CLARIFICATION WORKFLOW (Clean SaaS style)
        # =====================================================================
        draft = st.session_state.active_draft
        items = draft.get('items', [])
        
        has_ambiguity = any(it['status'] in ('ambiguous', 'unknown_product', 'out_of_stock', 'needs_clarification', 'missing_quantity') for it in items)
        if has_ambiguity:
            st.markdown("""
            <div style="margin-top: 0.5rem; margin-bottom: 0.35rem;">
                <span class="pill pill-amber">⚠️ Clarifications Required</span>
            </div>
            """, unsafe_allow_html=True)

            for idx, item in enumerate(items):
                status = item.get('status')
                raw_mention = item.get('raw_product_mention') or 'Requested item'
                safe_raw = html.escape(str(raw_mention))
                req_qty = item.get('quantity')
                qty_display = f"{int(req_qty)} packs" if req_qty is not None else "quantity unspecified"

                # 1. Ambiguous Product Variants
                if status == 'ambiguous':
                    family = item.get('product_family') or raw_mention
                    safe_family = html.escape(str(family))
                    st.markdown(f"""
                    <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 6px; padding: 0.65rem 0.75rem; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600; font-size: 0.85rem; color: #92400E;">
                            {safe_family.capitalize()} — Pack size required
                        </div>
                        <div style="font-size: 0.775rem; color: #78350F; margin-top: 0.1rem;">
                            Which variant did the retailer mean? (Requested: <strong>{html.escape(qty_display)}</strong>)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    for candidate in item.get('candidate_skus', []):
                        c_label = candidate.get('product_name') or candidate.get('pack_size') or candidate['sku']
                        pack_label = candidate.get('pack_size') or ''
                        btn_text = f"Select {candidate['sku']} · {c_label}"
                        if pack_label and pack_label not in c_label:
                            btn_text = f"Select {candidate['sku']} · {c_label} ({pack_label})"
                        if st.button(btn_text, key=f"sel_var_{idx}_{candidate['sku']}", use_container_width=True):
                            manager.resolve_ambiguity(draft, idx, candidate['sku'])
                            _say('assistant', f"Selected {candidate['product_name']}. Original quantity ({qty_display}) preserved.")
                            st.rerun()

                # 2. Missing Quantity or Bulk Unit Gating (Peti/Dabba)
                elif status in ('needs_clarification', 'missing_quantity'):
                    p_name = item.get('product_name') or raw_mention
                    safe_name = html.escape(str(p_name))
                    clarif_msg = item.get('clarification_message') or "Individual pack count needed"
                    safe_msg = html.escape(str(clarif_msg))
                    st.markdown(f"""
                    <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 6px; padding: 0.65rem 0.75rem; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600; font-size: 0.85rem; color: #92400E;">
                            {safe_name} — Individual pack count needed
                        </div>
                        <div style="font-size: 0.75rem; color: #78350F; margin-top: 0.1rem;">
                            {safe_msg}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    q_col1, q_col2 = st.columns([2, 1])
                    with q_col1:
                        cur_q = int(req_qty) if req_qty is not None and 1 <= req_qty <= 500 else 1
                        new_q = st.number_input('Packs', min_value=1, max_value=500, value=cur_q, key=f"inp_qty_{idx}", label_visibility='collapsed')
                    with q_col2:
                        if st.button('Save explicit pack count', key=f"save_qty_{idx}", use_container_width=True):
                            manager.update_item_quantity(draft, idx, new_q, 'pack')
                            _say('assistant', f"Confirmed {new_q} individual packs for {p_name}.")
                            st.rerun()

                # 3. Unknown Off-Catalog Product
                elif status == 'unknown_product':
                    st.markdown(f"""
                    <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 0.65rem 0.75rem; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600; font-size: 0.825rem; color: #B91C1C;">Product not found in catalog</div>
                        <div style="font-size: 0.75rem; color: #991B1B;">"{safe_raw}" is not recognized in the 40-SKU distributor catalog.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Remove line ({raw_mention})", key=f"del_unk_{idx}"):
                        manager.remove_item(draft, idx)
                        st.rerun()

                # 4. Out-of-Stock Product
                elif status == 'out_of_stock':
                    p_name = item.get('product_name') or raw_mention
                    safe_name = html.escape(str(p_name))
                    st.markdown(f"""
                    <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 0.65rem 0.75rem; margin-bottom: 0.5rem;">
                        <div style="font-weight: 600; font-size: 0.825rem; color: #B91C1C;">Currently Unavailable (Out of Stock)</div>
                        <div style="font-size: 0.75rem; color: #991B1B;">{safe_name} is marked unavailable in catalog inventory.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Remove line ({p_name})", key=f"del_oos_{idx}"):
                        manager.remove_item(draft, idx)
                        st.rerun()

        # =====================================================================
        # ML REORDER RECOMMENDATION (Accurate, non-fabricated rationale)
        # =====================================================================
        if st.session_state.active_nudge:
            n = st.session_state.active_nudge
            safe_prod = html.escape(str(n['product_name']))
            safe_cat = html.escape(str(n['category']))
            safe_store = html.escape(str(store_name))
            st.markdown(f"""
            <div class="nudge-box">
                <div class="nudge-header">
                    <span class="nudge-title">💡 Suggested Replenishment</span>
                    <span class="pill pill-green">Reorder Likelihood: {n['probability']:.0%}</span>
                </div>
                <div class="nudge-body">
                    <strong>{safe_prod}</strong> ({safe_cat})<br>
                    <span style="color: #64748B;">Ordering Rhythm:</span> {safe_store} ordered this in <strong>{n['ordered_last_4w']} of the last 4 weeks</strong> (avg {n['avg_qty_last_4w']:.0f} packs). Temporal model estimates high likelihood of replenishment need.<br>
                    <span style="color: #64748B;">Suggested Order:</span> <strong>{n['suggested_quantity']} individual packs</strong> @ ₹{n['unit_price_inr']:,.2f}<br>
                    <span style="font-size: 0.7rem; color: #64748B;">Note: Based on historical ordering intervals; requires operator approval.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            n_a, n_b = st.columns(2)
            with n_a:
                if st.button('Add suggested packs', type='primary', key='add_nudge_btn', use_container_width=True):
                    manager.add_nudge_item(draft, n['sku'], n['suggested_quantity'], 'pack')
                    _say('assistant', f"Added {n['suggested_quantity']} packs of {n['product_name']} after sales approval.")
                    st.session_state.active_nudge = None
                    st.rerun()
            with n_b:
                if st.button('Dismiss', key='dismiss_nudge_btn', use_container_width=True):
                    st.session_state.active_nudge = None
                    st.rerun()

    # =========================================================================
    # RIGHT COLUMN: ORDER DRAFT REVIEW PANEL
    # =========================================================================
    with col_right:
        draft = st.session_state.active_draft
        items = draft.get('items', [])
        can_confirm = draft.get('can_confirm', False)
        grand_total = draft.get('grand_total_inr', 0.0)
        total_packs = int(draft.get('total_base_units', 0))

        # Card Header with Status Pill
        if not items:
            status_html = '<span class="pill pill-gray">Empty Draft</span>'
        elif can_confirm:
            status_html = '<span class="pill pill-green">✓ Ready to Confirm</span>'
        elif any(it.get('status') in ('unknown_product', 'out_of_stock') for it in items):
            status_html = '<span class="pill pill-red">Blocked: Invalid Items</span>'
        else:
            status_html = '<span class="pill pill-amber">Needs Clarification</span>'

        st.markdown(f"""
        <div class="saas-card-header">
            <div>
                <h4 class="saas-card-title">Order Draft</h4>
                <div style="font-size: 0.75rem; color: #64748B;">{html.escape(store_name)} ({html.escape(current_store)})</div>
            </div>
            <div>
                {status_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Empty Draft State
        if not items:
            st.markdown("""
            <div style="text-align: center; color: #94A3B8; font-size: 0.825rem; padding: 3rem 1rem; background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 6px;">
                <div style="font-size: 1.5rem; margin-bottom: 0.35rem;">📋</div>
                <div>No line items in current order draft.</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.25rem;">
                    Process an order message on the left or select a scenario from the sidebar Demo Tools.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Table-style Item Listing
            st.markdown("""
            <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #64748B; font-weight: 600; text-transform: uppercase; padding: 0.3rem 0.5rem; border-bottom: 1px solid #E2E8F0;">
                <span style="width: 45%;">Product Description</span>
                <span style="width: 15%;">SKU</span>
                <span style="width: 15%; text-align: right;">Unit Rate</span>
                <span style="width: 25%; text-align: right;">Line Total</span>
            </div>
            """, unsafe_allow_html=True)

            for idx, item in enumerate(items):
                status = item.get('status', 'unknown_product')
                sku = item.get('sku') or '—'
                p_name = item.get('product_name') or item.get('raw_product_mention') or 'Unresolved Product'
                p_pack = item.get('pack_size') or ''
                rate = float(item.get('unit_price_inr') or 0)
                qty = item.get('quantity')
                line_total = float(item.get('line_total_inr') or 0)

                safe_pname = html.escape(str(p_name))
                safe_pack = html.escape(str(p_pack))
                safe_sku = html.escape(str(sku))

                # Status pill for this row
                if status == 'matched':
                    pill_badge = '<span class="pill pill-green" style="font-size: 0.65rem;">Matched</span>'
                elif status == 'ambiguous':
                    pill_badge = '<span class="pill pill-amber" style="font-size: 0.65rem;">Ambiguous</span>'
                elif status == 'out_of_stock':
                    pill_badge = '<span class="pill pill-red" style="font-size: 0.65rem;">Out of Stock</span>'
                else:
                    pill_badge = '<span class="pill pill-red" style="font-size: 0.65rem;">Unverified</span>'

                # Item Header Line
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #F1F5F9; border-radius: 6px; padding: 0.5rem 0.65rem; margin-top: 0.35rem; box-shadow: 0 1px 1px rgba(0,0,0,0.02);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div style="font-size: 0.85rem; font-weight: 600; color: #172334;">{safe_pname}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">{safe_pack} {pill_badge}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.85rem; font-weight: 700; color: #172334;">₹{line_total:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">@ ₹{rate:,.2f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Inline Controls: Quantity Stepper & Remove Button
                e_col1, e_col2, e_col3 = st.columns([2, 1.2, 1])
                with e_col1:
                    cur_val = int(qty) if qty is not None and float(qty).is_integer() and 1 <= qty <= 500 else 1
                    new_val = st.number_input(
                        'Packs',
                        min_value=1,
                        max_value=500,
                        value=cur_val,
                        key=f"item_qty_{draft['draft_id']}_{idx}",
                        label_visibility='collapsed'
                    )
                with e_col2:
                    btn_lbl = 'Save explicit pack count' if status != 'matched' else 'Update pack quantity'
                    if st.button(btn_lbl, key=f"upd_btn_{draft['draft_id']}_{idx}"):
                        manager.update_item_quantity(draft, idx, new_val, 'pack')
                        st.rerun()
                with e_col3:
                    if st.button('Remove line', key=f"del_line_{draft['draft_id']}_{idx}"):
                        manager.remove_item(draft, idx)
                        st.rerun()

            # Order Financial Totals
            st.markdown(f"""
            <div class="order-financial-card">
                <div class="fin-row">
                    <span>Line Items</span>
                    <span style="font-weight: 600; color: #172334;">{len(items)} products</span>
                </div>
                <div class="fin-row">
                    <span>Total Individual Packs</span>
                    <span style="font-weight: 600; color: #172334;">{total_packs} packs</span>
                </div>
                <div class="fin-row">
                    <span>Pricing Basis</span>
                    <span>Catalog Wholesale Rates</span>
                </div>
                <div class="fin-total-row">
                    <span>Order Total (INR)</span>
                    <span>₹{grand_total:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Validation Messages
        if draft.get('validation_errors'):
            st.markdown("""
            <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 0.65rem 0.85rem; margin-top: 0.5rem; font-size: 0.775rem; color: #991B1B;">
                <strong>Order blocked from confirmation:</strong>
            """, unsafe_allow_html=True)
            for err in draft['validation_errors']:
                st.markdown(f"<div style='margin-left: 0.5rem;'>• {html.escape(str(err))}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if can_confirm and items:
            st.markdown("""
            <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 0.5rem 0.75rem; margin-top: 0.5rem; font-size: 0.775rem; color: #166534;">
                ✓ Catalog prices and quantities verified. Ready for human confirmation.
            </div>
            """, unsafe_allow_html=True)

        # Bottom Action Bar
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        act_col1, act_col2 = st.columns([1, 2])
        with act_col1:
            if st.button('Clear Draft', use_container_width=True):
                _reset(st.session_state.selected_store_id, stores, manager)
                st.rerun()
        with act_col2:
            confirm_clicked = st.button(
                'Confirm order',
                type='primary',
                use_container_width=True,
                disabled=not can_confirm
            )
            if confirm_clicked:
                confirmed_rec = manager.confirm_order(draft)
                if confirmed_rec:
                    _say('assistant', f"✓ Order confirmed successfully! Receipt reference: {confirmed_rec['order_id']} · Total: ₹{confirmed_rec['grand_total_inr']:,.2f}.")
                    st.session_state.active_draft = manager.create_empty_draft(st.session_state.selected_store_id, draft['store_name'])
                    st.session_state.active_nudge = None
                    st.success(f"Order {confirmed_rec['order_id']} logged to dispatch ledger.")
                    st.rerun()
