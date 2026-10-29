"""
KiranaAI: Professional B2B SaaS UI Styling
Inspired by modern business applications (Shopify Admin, Zoho Inventory).
Palette:
  Background: #F8FAFC
  Cards: #FFFFFF
  Primary Text: #172334
  Secondary Text: #64748B
  Primary Accent: #0F766E (Deep Teal)
  Borders: #E2E8F0
  Success: #15803D (Green)
  Warning: #B45309 (Amber)
  Error: #DC2626 (Red)
"""

def get_custom_css() -> str:
    return """
<style>
/* 1. Global Reset & Typography */
html, body, p, div, span, label, li {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", "Helvetica Neue", Arial, sans-serif;
    color: #172334;
    -webkit-font-smoothing: antialiased;
}

/* Retain Material Symbols font for native Streamlit icons */
[data-testid="stIconMaterial"],
span[data-testid*="stIcon"],
.material-symbols-rounded,
.material-symbols-outlined {
    font-family: "Material Symbols Rounded" !important;
    font-weight: 400 !important;
    font-style: normal !important;
    display: inline-block !important;
    line-height: 1 !important;
}

/* Page background */
.stApp {
    background-color: #F8FAFC !important;
}

/* Container spacing for 1366x768 screens */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1440px !important;
}

/* 2. Top Application Header */
.app-top-header {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 0.85rem 1.25rem;
    margin-bottom: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.brand-section {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.brand-icon {
    width: 34px;
    height: 34px;
    background: #0F766E;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 1.1rem;
}

.brand-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #172334;
    letter-spacing: -0.01em;
    line-height: 1.2;
    margin: 0;
}

.brand-subtitle {
    font-size: 0.8rem;
    color: #64748B;
    font-weight: 500;
    margin: 0;
}

.header-badges {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* 3. Status Badges & Pills */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.55rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    line-height: 1.2;
}

.pill-teal {
    background-color: #F0FDFA;
    color: #0F766E;
    border: 1px solid #CCFBF1;
}

.pill-green {
    background-color: #DCFCE7;
    color: #15803D;
    border: 1px solid #BBF7D0;
}

.pill-amber {
    background-color: #FEF3C7;
    color: #B45309;
    border: 1px solid #FDE68A;
}

.pill-red {
    background-color: #FEE2E2;
    color: #DC2626;
    border: 1px solid #FECACA;
}

.pill-gray {
    background-color: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}

/* 4. White SaaS Card Containers */
.saas-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.saas-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 0.5rem;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid #F1F5F9;
}

.saas-card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #172334;
    margin: 0;
}

/* 5. Clean Messaging Stream (Shopify / B2B Chat style) */
.chat-stream-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.75rem;
    max-height: 250px;
    overflow-y: auto;
    margin-bottom: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.msg-retailer {
    align-self: flex-start;
    background: #FFFFFF;
    color: #172334;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.55rem 0.8rem;
    max-width: 90%;
    font-size: 0.85rem;
    line-height: 1.4;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.msg-assistant {
    align-self: flex-start;
    background: #F0FDFA;
    color: #172334;
    border: 1px solid #CCFBF1;
    border-radius: 6px;
    padding: 0.55rem 0.8rem;
    max-width: 90%;
    font-size: 0.85rem;
    line-height: 1.4;
}

.msg-sender {
    font-size: 0.68rem;
    font-weight: 600;
    color: #0F766E;
    margin-bottom: 0.15rem;
    display: flex;
    justify-content: space-between;
}

.msg-time {
    font-size: 0.65rem;
    color: #94A3B8;
    font-weight: 400;
}

/* 6. Order Desk Table & Item Rows */
.order-table-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 0.75rem;
}

.order-row-item {
    padding: 0.65rem 0.75rem;
    border-bottom: 1px solid #F1F5F9;
    background: #FFFFFF;
}

.order-row-item:last-child {
    border-bottom: none;
}

.item-main-line {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
}

.item-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #172334;
    margin: 0;
}

.item-meta {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 0.1rem;
}

.item-price {
    font-size: 0.875rem;
    font-weight: 600;
    color: #172334;
    text-align: right;
    white-space: nowrap;
}

/* 7. Summary & Total Box */
.order-financial-card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-top: 0.5rem;
}

.fin-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: #64748B;
    margin-bottom: 0.25rem;
}

.fin-total-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #CBD5E1;
    padding-top: 0.45rem;
    margin-top: 0.45rem;
    font-size: 1.05rem;
    font-weight: 700;
    color: #0F766E;
}

/* 8. Modern Replenishment Suggestion Card */
.nudge-box {
    background: #F0FDF4;
    border: 1px solid #86EFAC;
    border-radius: 6px;
    padding: 0.75rem 0.85rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

.nudge-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.25rem;
}

.nudge-title {
    font-size: 0.825rem;
    font-weight: 700;
    color: #15803D;
    margin: 0;
}

.nudge-body {
    font-size: 0.775rem;
    color: #334155;
    line-height: 1.4;
    margin-bottom: 0.5rem;
}

/* 9. Commercial Invoice / Receipt Card */
.invoice-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    max-width: 720px;
    margin: 0 auto;
}

.invoice-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 2px solid #F1F5F9;
    padding-bottom: 1rem;
    margin-bottom: 1rem;
}

.invoice-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #172334;
    margin: 0;
}

.invoice-sub {
    font-size: 0.8rem;
    color: #64748B;
    margin-top: 0.2rem;
}

.invoice-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    margin: 1rem 0;
}

.invoice-table th {
    text-align: left;
    padding: 0.5rem 0.4rem;
    border-bottom: 1px solid #E2E8F0;
    color: #64748B;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
}

.invoice-table td {
    padding: 0.6rem 0.4rem;
    border-bottom: 1px solid #F8FAFC;
    color: #172334;
}

/* 10. KPI Analytics Cards */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.kpi-metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.kpi-num {
    font-size: 1.35rem;
    font-weight: 700;
    color: #0F766E;
    line-height: 1.1;
}

.kpi-label {
    font-size: 0.75rem;
    color: #64748B;
    font-weight: 500;
    margin-top: 0.2rem;
}

/* 11. Streamlit Widget Polish */
/* Text inputs, selects, textareas */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background-color: #FFFFFF !important;
    border-color: #CBD5E1 !important;
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    color: #172334 !important;
}

/* Actual input / textarea text visibility */
input, textarea, [data-baseweb="select"] input {
    color: #172334 !important;
    -webkit-text-fill-color: #172334 !important;
    caret-color: #172334 !important;
    background-color: transparent !important;
}

textarea::placeholder,
input::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}

/* Improve text visibility inside dark-themed native wrappers */
div[data-baseweb="textarea"] textarea,
div[data-baseweb="input"] input {
    color: #172334 !important;
    -webkit-text-fill-color: #172334 !important;
}

/* Form labels */
.stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
    margin-bottom: 0.2rem !important;
}

/* Primary buttons & Form Submits */
button[kind="primary"],
button[kind="primaryFormSubmit"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {
    background-color: #0F766E !important;
    border: 1px solid #0D655E !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-radius: 6px !important;
    padding: 0.45rem 1.1rem !important;
    box-shadow: 0 1px 2px rgba(15, 118, 110, 0.2) !important;
    transition: all 0.15s ease-in-out !important;
}

button[kind="primary"]:hover,
button[kind="primaryFormSubmit"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background-color: #0D655E !important;
    border-color: #0B534E !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 4px rgba(15, 118, 110, 0.3) !important;
}

/* Secondary buttons & Form Submits */
button[kind="secondary"],
button[kind="secondaryFormSubmit"],
button[data-testid="stBaseButton-secondary"],
button[data-testid="stBaseButton-secondaryFormSubmit"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #172334 !important;
    font-weight: 500 !important;
    font-size: 0.825rem !important;
    border-radius: 6px !important;
    padding: 0.4rem 0.9rem !important;
    transition: all 0.15s ease-in-out !important;
}

button[kind="secondary"]:hover,
button[kind="secondaryFormSubmit"]:hover,
button[data-testid="stBaseButton-secondary"]:hover,
button[data-testid="stBaseButton-secondaryFormSubmit"]:hover {
    background-color: #F8FAFC !important;
    border-color: #94A3B8 !important;
    color: #172334 !important;
}

/* Compact sidebar */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    padding-top: 1rem !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Compact horizontal radios in sidebar */
div[data-testid="stRadio"] > div {
    gap: 0.25rem !important;
}

div[data-testid="stRadio"] label {
    padding: 0.45rem 0.75rem !important;
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #334155 !important;
    transition: background 0.1s ease;
}

div[data-testid="stRadio"] label:hover {
    background-color: #F1F5F9 !important;
}


/* Allow long button labels to wrap instead of showing ellipsis */
div.stButton > button {
    white-space: normal !important;
    height: auto !important;
    min-height: 2.6rem !important;
    line-height: 1.3 !important;
}

div.stButton > button p,
div.stButton > button span {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

/* Improve expander / markdown readability */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: #172334;
}

/* Metric components */
div[data-testid="stMetricValue"] {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #172334 !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    color: #64748B !important;
    font-weight: 500 !important;
}

/* Compact alerts */
div[data-testid="stAlert"] {
    padding: 0.6rem 0.85rem !important;
    border-radius: 6px !important;
    font-size: 0.825rem !important;
    margin-bottom: 0.5rem !important;
}
</style>
"""
