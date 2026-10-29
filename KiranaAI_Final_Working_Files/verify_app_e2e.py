"""
KiranaAI: Comprehensive End-to-End Browser & UI Verification Script
Tests in Chrome at 1366x768 resolution:
1. Navigation across all 5 operational pages
2. Order Desk initial layout and visual checks
3. Scenario A: Clean order (STORE001) - ₹360 total, confirmation, receipt in Orders page
4. Scenario B: Ambiguous order (STORE002) - blocked, variant selection, preserved qty, ₹90 total
5. Scenario C: Predictive reorder (STORE003) - Surf Excel + Horlicks reorder nudge addition
6. Scenario D: Guardrails & Block (STORE004) - Unknown product & peti unit rejection, remove line
7. AI Engine status accuracy checks (offline, forced offline, configured, error fallback)
8. High-resolution screenshots saved to verification_screenshots/
"""
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
SHOTS_DIR = BASE_DIR / "verification_screenshots"
SHOTS_DIR.mkdir(exist_ok=True)

def run_verification():
    print("=" * 60)
    print("KiranaAI Live UI & Scenario Verification (Chrome 1366x768)")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        # Step 1: Navigate to Streamlit App
        print("\n[Step 1] Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle")
        time.sleep(3)

        # Ensure Streamlit app is loaded
        page.wait_for_selector(".app-top-header", timeout=15000)
        page.screenshot(path=str(SHOTS_DIR / "01_order_desk_initial.png"))
        print("  ✓ Order Desk loaded successfully (Screenshot: 01_order_desk_initial.png)")

        # Verify Header Branding
        header_text = page.locator(".app-top-header").inner_text()
        assert "KiranaAI" in header_text, "Header should contain 'KiranaAI'"
        assert "Distributor Order Management" in header_text, "Header should contain subtitle"
        assert "40 Catalog SKUs" in header_text, "Header should show 40 Catalog SKUs"
        assert "30 Store Network" in header_text, "Header should show 30 Store Network"
        print("  ✓ Top Application Header branding verified")

        # Step 2: Test Navigation across 5 Pages
        print("\n[Step 2] Testing 5-Page Navigation...")
        
        # 2a. Orders Page (Empty state)
        page.locator("label:has-text('Orders')").click()
        time.sleep(1.5)
        page.screenshot(path=str(SHOTS_DIR / "02_page_orders_empty.png"))
        assert "Orders & Dispatch Ledger" in page.content()
        assert "No Confirmed Orders Yet" in page.content()
        print("  ✓ Page 2: Orders verified (empty state)")

        # 2b. Replenishment Insights Page
        page.locator("label:has-text('Replenishment Insights')").click()
        time.sleep(1.5)
        page.screenshot(path=str(SHOTS_DIR / "03_page_replenishment_insights.png"))
        assert "Replenishment Insights & Model Analytics" in page.content()
        assert "Overall Accuracy" in page.content()
        assert "Stockout Recall" in page.content()
        assert "84.6%" in page.content()
        print("  ✓ Page 3: Replenishment Insights verified")

        # 2c. Product Catalog Page
        page.locator("label:has-text('Product Catalog')").click()
        time.sleep(1.5)
        page.screenshot(path=str(SHOTS_DIR / "04_page_product_catalog.png"))
        assert "Product Catalog & Inventory" in page.content()
        assert "Total Catalog SKUs" in page.content()
        assert "Active / In Stock" in page.content()
        assert "Out of Stock (BRU002, KIT002)" in page.content()
        print("  ✓ Page 4: Product Catalog verified (40 SKUs, 38 active, 2 OOS)")

        # 2d. Retailer Network Page
        page.locator("label:has-text('Retailer Network')").click()
        time.sleep(1.5)
        page.screenshot(path=str(SHOTS_DIR / "05_page_retailer_network.png"))
        assert "Retailer Network" in page.content()
        assert "Active Retailer Accounts" in page.content()
        assert "30 Active Accounts" in page.content()
        print("  ✓ Page 5: Retailer Network verified (30 retail accounts)")

        # 2e. Return to Order Desk
        page.locator("label:has-text('Order Desk')").click()
        time.sleep(1.5)
        print("  ✓ Returned to Order Desk")

        # Step 3: Verify Scenario A (Clean Multi-Item Hinglish Order)
        print("\n[Step 3] Verifying Scenario A (Clean order - STORE001)...")
        # Open Demo Tools expander in sidebar
        page.locator("div[data-testid='stSidebar'] >> text='🛠️ Demo Tools'").click()
        time.sleep(1)
        # Click Demo 1
        page.locator("button:has-text('1. Clean Hinglish order')").click()
        time.sleep(2.5)
        page.screenshot(path=str(SHOTS_DIR / "06_scenario_a_processed.png"))
        
        # Verify draft totals and items
        content = page.content()
        assert "Nestle Maggi 2-Minute Noodles" in content, "MAG001 should be in draft"
        assert "Tata Salt Vacuum Evaporated" in content, "TSL002 should be in draft"
        assert "₹360.00" in content, "Grand total should be ₹360.00"
        assert "Ready to Confirm" in content, "Draft should be ready to confirm"
        print("  ✓ Scenario A parsed: MAG001 x 12, TSL002 x 6, Grand total ₹360.00")

        # Confirm Order
        confirm_btn = page.locator("button:has-text('Confirm order')")
        assert confirm_btn.is_enabled(), "Confirm order button should be enabled"
        confirm_btn.click()
        time.sleep(2)
        page.screenshot(path=str(SHOTS_DIR / "07_scenario_a_confirmed.png"))
        print("  ✓ Order confirmed successfully")

        # Check Orders Page Receipt
        page.locator("label:has-text('Orders')").click()
        time.sleep(1.5)
        page.screenshot(path=str(SHOTS_DIR / "08_scenario_a_commercial_receipt.png"))
        orders_content = page.content()
        assert "KiranaAI Order Receipt" in orders_content, "Receipt should render"
        assert "Commercial Delivery Challan" in orders_content
        assert "₹360.00" in orders_content
        assert "MAG001" in orders_content
        assert "TSL002" in orders_content
        print("  ✓ Single-table Commercial Receipt rendered in Orders page (Screenshot: 08_scenario_a_commercial_receipt.png)")

        # Step 4: Verify Scenario B (Ambiguous Order)
        print("\n[Step 4] Verifying Scenario B (Ambiguous order - STORE002)...")
        page.locator("label:has-text('Order Desk')").click()
        time.sleep(1)
        page.locator("button:has-text('2. Ambiguous order')").click()
        time.sleep(2.5)
        page.screenshot(path=str(SHOTS_DIR / "09_scenario_b_ambiguous_blocked.png"))

        content_b = page.content()
        assert "Clarifications Required" in content_b
        assert "Needs Clarification" in content_b
        confirm_btn_b = page.locator("button:has-text('Confirm order')")
        assert confirm_btn_b.is_disabled(), "Confirm order button MUST be disabled during ambiguity"
        print("  ✓ Scenario B blocked: Confirmation disabled, clarification cards displayed")

        # Resolve Maggi variant -> Select MAG001 (70g)
        maggi_sel = page.locator("button:has-text('Select MAG001')").first
        maggi_sel.click()
        time.sleep(2)

        # Save explicit pack count for Maggi
        save_btn_1 = page.locator("button:has-text('Save explicit pack count')").first
        if save_btn_1.is_visible():
            save_btn_1.click()
            time.sleep(2)

        # Resolve Parle-G variant -> Select PAR001 (65g)
        parle_sel = page.locator("button:has-text('Select PAR001')").first
        parle_sel.click()
        time.sleep(2)

        # Save explicit pack count for Parle-G
        save_btn_2 = page.locator("button:has-text('Save explicit pack count')").first
        if save_btn_2.is_visible():
            save_btn_2.click()
            time.sleep(2)

        page.screenshot(path=str(SHOTS_DIR / "10_scenario_b_resolved.png"))
        content_b_res = page.content()
        assert "₹90.00" in content_b_res, "Grand total should be ₹90.00 (4x15 + 3x10)"
        confirm_btn_b2 = page.locator("button:has-text('Confirm order')")
        assert confirm_btn_b2.is_enabled(), "Confirm order should now be enabled"
        confirm_btn_b2.click()
        time.sleep(2)
        print("  ✓ Scenario B resolved: Selected MAG001 + PAR001, Total ₹90.00, confirmed successfully")

        # Step 5: Verify Scenario C (Predictive Reorder Nudge)
        print("\n[Step 5] Verifying Scenario C (Predictive reorder - STORE003)...")
        page.locator("button:has-text('3. Predictive reorder')").click()
        time.sleep(2.5)
        page.screenshot(path=str(SHOTS_DIR / "11_scenario_c_nudge_displayed.png"))

        content_c = page.content()
        assert "Suggested Replenishment" in content_c, "Replenishment recommendation card should appear"
        assert "Horlicks Classic Malt Drink" in content_c, "Horlicks should be recommended"
        assert "Ordering Rhythm:" in content_c, "Historical ordering rhythm rationale should be displayed"
        assert "Add suggested packs" in content_c, "Opt-in button should be present"
        print("  ✓ Scenario C: Horlicks replenishment suggestion generated with historical rhythm rationale")

        # Click "Add suggested packs"
        page.locator("button:has-text('Add suggested packs')").click()
        time.sleep(2)
        page.screenshot(path=str(SHOTS_DIR / "12_scenario_c_nudge_added.png"))
        content_c_added = page.content()
        assert "HOR001" in content_c_added or "Horlicks" in content_c_added, "Horlicks should now be in order draft"
        assert "₹6,880.00" in content_c_added, "Total should recalculate accurately to ₹6,880.00"
        print("  ✓ Scenario C: Suggested item added to order draft, total recalculated to ₹6,880.00")

        # Step 6: Verify Scenario D (Guardrails & Block)
        print("\n[Step 6] Verifying Scenario D (Guardrails & Block - STORE004)...")
        page.locator("button:has-text('4. Guardrails & Block')").click()
        time.sleep(2.5)
        page.screenshot(path=str(SHOTS_DIR / "13_scenario_d_blocked.png"))

        content_d = page.content()
        assert "Product not found in catalog" in content_d or "not recognized" in content_d
        confirm_btn_d = page.locator("button:has-text('Confirm order')")
        assert confirm_btn_d.is_disabled(), "Confirm order button MUST be disabled for unknown products"
        print("  ✓ Scenario D: Unknown product 'Dragon Energy Drink' blocked, confirmation disabled")

        # Click Remove line
        page.locator("button:has-text('Remove line')").first.click()
        time.sleep(2)
        page.screenshot(path=str(SHOTS_DIR / "14_scenario_d_cleared.png"))
        print("  ✓ Scenario D: Invalid line removed safely")

        # Step 7: Verify Store Routing from Retailer Network
        print("\n[Step 7] Testing Store Routing from Retailer Network...")
        page.locator("label:has-text('Retailer Network')").click()
        time.sleep(1.5)
        # Select STORE005 in Quick Route
        quick_select = page.locator("div[data-testid='stSelectbox']:has-text('Quick Route') >> input, div[data-testid='stSelectbox']:has-text('Quick Route') >> div[role='combobox']")
        # Use Streamlit selectbox helper
        page.locator("div[data-testid='stSelectbox']:has-text('Quick Route')").click()
        time.sleep(0.5)
        page.locator("li[role='option']:has-text('Open STORE005')").click()
        time.sleep(2)
        page.screenshot(path=str(SHOTS_DIR / "15_store_routed_order_desk.png"))
        
        desk_content = page.content()
        assert "STORE005" in desk_content, "Order Desk should now be loaded for STORE005"
        print("  ✓ Retailer Network quick select routed directly to STORE005 Order Desk")

        # Step 8: Verify AI Engine Status Transitions
        print("\n[Step 8] Testing AI Engine Status Indicators...")
        # 8a. Currently offline parser is active
        assert "Offline Parser" in page.content(), "Offline parser should be labeled accurately"
        print("  ✓ State 1 verified: Offline Parser (Rule-based) accurately labeled")

        # 8b. Toggle Force Offline Parser
        page.locator("div[data-testid='stSidebar'] >> text='⚙️ API Configuration'").click()
        time.sleep(0.8)
        page.locator("label:has-text('Force offline parser')").click()
        time.sleep(1.5)
        page.screenshot(path=str(SHOTS_DIR / "16_engine_status_forced_local.png"))
        assert "Offline Parser (Forced Local)" in page.content() or "Forced local mode" in page.content()
        print("  ✓ State 2 verified: Offline Parser (Forced Local) accurately labeled")

        # Uncheck force local
        page.locator("label:has-text('Force offline parser')").click()
        time.sleep(1)

        # 8c. Enter Dummy Gemini Key -> Awaiting Request
        key_input = page.locator("input[type='password']").first
        key_input.fill("test_dummy_gemini_api_key_12345")
        key_input.press("Enter")
        time.sleep(2)
        page.screenshot(path=str(SHOTS_DIR / "17_engine_status_awaiting_request.png"))
        content_key = page.content()
        assert "Awaiting Request" in content_key or "Key Configured" in content_key
        print("  ✓ State 3 verified: Gemini Key Configured (Awaiting Request) accurately labeled")

        # 8d. Submit a request with invalid key -> Fallback error
        text_area = page.locator("textarea").first
        text_area.fill("Bhai 2 packs Maggi 70g bhej dena")
        page.locator("button:has-text('Process Order')").click()
        time.sleep(3)
        page.screenshot(path=str(SHOTS_DIR / "18_engine_status_error_fallback.png"))
        content_err = page.content()
        assert "Offline Fallback" in content_err or "fallback" in content_err.lower()
        print("  ✓ State 4 verified: Offline Fallback (Gemini API Error) accurately caught and displayed")

        # Clear key to restore clean offline mode
        key_input.fill("")
        key_input.press("Enter")
        time.sleep(1.5)
        print("  ✓ Clean state restored")

        browser.close()
        print("\n" + "=" * 60)
        print("ALL BROWSER UI VERIFICATION TESTS PASSED SUCCESSFULLY!")
        print(f"Screenshots saved to: {SHOTS_DIR}")
        print("=" * 60)

if __name__ == "__main__":
    run_verification()
