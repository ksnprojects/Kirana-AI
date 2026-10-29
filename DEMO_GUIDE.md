# KiranaAI: 7-Minute MBA Live Demonstration Guide & Script

This document provides a minute-by-minute walkthrough and presentation guide for presenting **KiranaAI** in an academic or executive setting.

---

## 1. Quick Demonstration Setup

Before beginning the live presentation:
1. Ensure the Streamlit server is running locally:
   ```powershell
   python -m streamlit run app.py
   ```
2. Open `http://localhost:8501` in your browser. Set your browser zoom to 90% or 100% so both the left chat column and right order draft column are clearly visible side by side.
3. Verify that the top header shows:
   - **MBA Foundations of AI**
   - **30 Simulated Stores**
   - **40 Original SKUs**
4. Check the sidebar:
   - Ensure `Force Offline Parser` is toggled as appropriate (Offline mode is recommended for 100% deterministic, zero-latency demos without external API dependencies).

---

## 2. Minute-by-Minute Presentation Script (7 Minutes Total)

```
┌──────────┬─────────────────────────────┬────────────────────────────────────────────┐
│ Timing   │ Screen / Module             │ Core Narrative & Speaker Talking Points    │
├──────────┼─────────────────────────────┼────────────────────────────────────────────┤
│ 0:00–1:00│ Header & Store Network      │ Business Context & The Kirana Problem      │
│ 1:00–2:15│ Demo 1: Clean Hinglish      │ Catalog Grounding & Inbound Extraction     │
│ 2:15–3:30│ Demo 2: Ambiguous Order     │ Conversational Clarification & Guardrails  │
│ 3:30–4:30│ Demo 3: Predictive Reorder  │ Temporal Machine Learning Replenishment    │
│ 4:30–5:30│ Demo 4: Guardrails & Block  │ Inventory Availability & Security Perimeter│
│ 5:30–6:30│ Evaluation & Benchmarks Tab │ Model Metrics, Baselines & Honest Science  │
│ 6:30–7:00│ Summary & Dispatch Log      │ Enterprise Impact & Future Roadmap         │
└──────────┴─────────────────────────────┴────────────────────────────────────────────┘
```

---

### Segment 1: The Kirana Business Problem & Architecture (0:00 – 1:00)

**Screen:** AI Order Assistant (Home) → Briefly click **Store Network** tab in sidebar.

**Speaker Script:**
> *"Good morning, professors and colleagues. In India, FMCG distribution represents a $100B+ market driven by over 12 million micro-retailers, or kiranas. Today, shopkeepers order daily inventory by sending informal, bilingual Hinglish WhatsApp voice and text messages to local distributors.
>
> On the distributor's side, data entry operators manually decipher these chaotic messages, leading to order delays, out-of-stock delivery mismatches, and missed reorder opportunities.
>
> **KiranaAI** is an AI-powered ordering assistant designed to automate this workflow. We built this platform on three foundational principles:
> 1. **Catalog Grounding:** Every item must resolve deterministically to an authoritative 40-SKU distributor catalog—no hallucinated products.
> 2. **Human-in-the-Loop Clarification:** When pack sizes or quantities are vague, the AI prompts the user rather than guessing.
> 3. **Predictive Nudging:** Using 16 weeks of temporal order history across 30 stores, we recommend items the retailer is at risk of stocking out on before they even run out."*

---

### Segment 2: Demo 1 — Clean Hinglish Multi-Item Order (1:00 – 2:15)

**Action:** Click the button **`1. Clean Hinglish order`** at the top of the Order Assistant page.

**Message loaded:**
`"Bhai maggi 70g ke 12 packs aur Tata namak 1kg 6 packs bhej dena"` (for STORE001).

**What to explain:**
> *"Let's test our first scenario: a standard multi-item Hinglish message. 
> Notice what happened in less than a second:
> - The parser extracted two products: 'maggi 70g' (12 packs) and 'Tata namak 1kg' (6 packs).
> - Our lexical catalog matcher mapped them to their exact SKUs: **MAG001** (Maggi 2-Minute Noodles 70g) and **TSL002** (Tata Salt Vacuum Evaporated 1kg).
> - The system retrieved the authoritative catalog prices: ₹14.00 and ₹32.00.
> - It calculated the exact total: **₹360.00** (12 × ₹14 = ₹168 + 6 × ₹32 = ₹192).
> 
> Notice that the order is not automatically sent to the warehouse. An order draft is presented in the right panel with green status badges. When I click **'Confirm order'**, the system logs the order and clears the draft for the next transaction."*

**Action:** Click **`Confirm order`**. Point out the green confirmation message.

---

### Segment 3: Demo 2 — Ambiguous Order & Variant Clarification (2:15 – 3:30)

**Action:** Click the button **`2. Ambiguous order`**.

**Message loaded:**
`"Bhai 4 maggi aur 3 Parle G bhej dena"` (for STORE002).

**What to explain:**
> *"Now let's examine a common real-world problem: ambiguity. In our catalog, Maggi comes in two pack sizes (70g and 140g), and Parle-G comes in two sizes (65g and 250g). The shopkeeper did not specify which one they want.
>
> A naive generative AI might guess one or invent an average price. KiranaAI refuses to guess.
> Notice:
> - Both lines are flagged with an orange warning: 'Clarification needed'.
> - The 'Confirm order' button is **disabled**.
> - The assistant renders interactive selection buttons for each valid catalog option.
>
> Watch as I resolve this: I select **MAG001 (70g)** for Maggi, and **PAR001 (65g)** for Parle-G. 
> Notice that the system preserved the shopkeeper's requested quantities (4 packs and 3 packs).
> With all ambiguities resolved, the total is calculated at **₹86.00**, and the 'Confirm order' button becomes active."*

**Action:** Click **`Select MAG001`**, then **`Select PAR001`**. Click **`Confirm order`**.

---

### Segment 4: Demo 3 — Temporal Predictive Reorder Nudge (3:30 – 4:30)

**Action:** Click the button **`3. Predictive reorder`**.

**Message loaded:**
`"Bhai surf excel 500g 4 packs bhejdo"` (for STORE003).

**What to explain:**
> *"Beyond processing inbound orders, KiranaAI helps distributors grow basket size. When STORE003 orders Surf Excel, look at the blue recommendation card that appears above the order draft:
>
> **'Predictive Reorder Recommendation: Horlicks Classic Malt Drink 500g — 93% Reorder Score'**.
>
> How was this generated?
> We trained a balanced Logistic Regression model on 16 weeks of store purchase history. The model looks at STORE003's ordering rhythm: this store ordered Horlicks in 2 of the last 4 weeks with an average order of 48 packs. Based on elapsed time since the last order, the temporal model identifies a 93% probability that the store's shelf is nearly depleted.
>
> Crucially, from an MBA ethics and trust standpoint, **we never sneak recommended items onto the customer's bill**. It is presented as a transparent suggestion with clear rationale. If the shopkeeper approves, one click on **'Add suggested packs'** adds 22 packs of Horlicks to the draft, instantly updating the grand total."*

**Action:** Click **`➕ Add suggested packs`**. Show the total updating from ₹720 to ₹6,880.

---

### Segment 5: Demo 4 — Perimeter Guardrails & Stock-out Protection (4:30 – 5:30)

**Action:** Click the button **`4. Guardrails & Block`**.

**Message loaded:**
`"Bhai 3 peti Dragon Energy Drink bhej dena"` (for STORE004).

**What to explain:**
> *"In any AI deployment, what the system refuses to do is as important as what it does.
> In this scenario, two guardrails are triggered simultaneously:
> 1. **Unknown SKU:** 'Dragon Energy Drink' does not exist in our authoritative 40-SKU catalog. The system flags it as unverified and blocks confirmation. It does not hallucinate a price or substitute a random product.
> 2. **Unverified Bulk Unit:** The message requests '3 peti' (cartons). In FMCG, wholesale carton packing multipliers vary wildly (e.g., 24 vs 48 units per carton). Because our catalog does not have verified carton multipliers, the system blocks the order and requires explicit confirmation in individual packs.
>
> Similarly, if a shopkeeper orders an out-of-stock item (such as Bru Gold Coffee 100g, SKU BRU002, or KitKat 37.5g, SKU KIT002), confirmation is strictly blocked until the inventory issue is resolved.
> The operator can easily click **'Remove line'** to discard the invalid request and proceed safely."*

**Action:** Click **`🗑️ Remove line`**.

---

### Segment 6: Model Evaluation & Benchmarking (5:30 – 6:30)

**Action:** Switch to **`📊 Model Evaluation & Benchmarks`** in the sidebar.

**What to explain:**
> *"To ensure rigorous academic evaluation, we separated our 16-week synthetic panel into strict temporal folds:
> - Weeks 1–9: Training
> - Weeks 10–12: Validation
> - Weeks 13–15: Held-out Test
>
> On the held-out test set of 3,600 store-SKU-week observations:
> - Our balanced Logistic Regression model achieves **84.64% accuracy** and **99.73% recall**, with an **F1 score of 0.5736** and an **AUC of 0.9621**.
> - Compared to a baseline heuristic of 'repeat last week's order' (which only achieves 24.9% recall and 0.2467 F1), our machine learning model captures almost four times as many true replenishment opportunities.
> - High recall is the optimal business objective for replenishment nudges: we minimize missed sales while keeping suggestions non-intrusive."*

---

### Segment 7: Wrap-up & Confirmed Orders Log (6:30 – 7:00)

**Action:** Switch to **`📦 Confirmed Orders & Dispatch Log`** in the sidebar.

**What to explain:**
> *"Finally, navigating to the Dispatch Log, we see all the simulated orders we reviewed and confirmed during this session, complete with store IDs, timestamped items, line-item totals, and audit trails.
>
> In summary, KiranaAI demonstrates how small business conversational ordering can be integrated into enterprise distribution systems with zero hallucinations, strict inventory guardrails, and actionable predictive replenishment."*

---

## 3. Anticipated Questions & Answers (Q&A)

**Q1: Why did you use RapidFuzz and Lexical RAG instead of a Vector Database like Chroma or Pinecone?**
> **A:** *"In a regional distributor catalog with 40 to a few hundred well-defined SKUs, vector embeddings often introduce semantic drift—for example, confusing 70g and 140g Maggi because their embedding vectors are nearly identical in cosine space. Lexical fuzzy matching over token ratios and an alias dictionary provides deterministic precision, guarantees exact SKU matching, runs in less than 5 milliseconds, and eliminates the operational complexity of running a vector database."*

**Q2: What happens if the internet goes down or the Gemini API fails?**
> **A:** *"KiranaAI features dual-tier architecture. If the Gemini API key is missing, network access is interrupted, or an API error occurs, the application automatically falls back to its built-in rule-based offline parser. All catalog matching, reorder modeling, and order confirmation workflows continue to function seamlessly without downtime."*

**Q3: Why don't you automatically add reorder recommendations to the cart?**
> **A:** *"In B2B commerce, unauthorized cart additions damage customer trust and increase order return rates. Retailers operate under tight cash flow constraints. Presenting recommendations as explicit, transparent suggestions preserves merchant autonomy while still driving incremental basket size."*
