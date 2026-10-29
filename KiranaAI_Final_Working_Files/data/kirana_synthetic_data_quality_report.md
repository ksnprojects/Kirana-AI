# Kirana Synthetic Dataset Quality Report

## Provenance and boundaries
- **Authoritative source:** user-supplied 40-row FMCG product catalog. Original source fields and values retained exactly in the processed copy.
- **All other data:** manually authored or pseudorandomly generated fictional academic examples (fixed seed `20261028`).
- **Commercial caveat:** source `unit_price_inr` values are illustrative, not verified, current or live distributor prices. No sale or dispatch is triggered.
- **Scope:** simulation uses 30 fictional test stores from a hypothetical distributor network of 300 stores; it does not claim coverage of all 300.
- **Privacy:** No phone numbers, emails, street addresses, personal names or real store transaction histories were generated or used.

## File and row counts

| File | Rows |
|---|---:|
| `product_catalog_processed.csv` | 40 |
| `synthetic_order_history.csv` | 2,013 |
| `store_profiles.csv` | 30 |
| `store_product_weekly_features.csv` | 19,200 |
| `labelled_whatsapp_messages.csv` | 40 |
| `llm_evaluation_cases.csv` | 40 |
| `catalog_edge_cases.csv` | 12 |
| `kirana_data_dictionary.csv` (supplementary) | 88 |

## Catalog inventory

- Original SKUs: **40**; unique product families: **20**; categories: **9**.
- Available SKUs: **38**; out-of-stock SKUs: **2** (`BRU002` and `KIT002`).
- Catalog categories (names retained exactly): **Beverages** (8), **Biscuits** (4), **Confectionery** (2), **Dairy** (2), **Home Care** (4), **Packaged Foods** (6), **Personal Care** (6), **Snacks** (2), **Staples** (6).

## Store, order and time overview

- Fictional stores: **30** (`STORE001` to `STORE030`).
- Synthetic confirmed orders: **536**; confirmed order lines: **2,013**.
- Date range: **2026-06-29** through **2026-10-18**; each week runs Monday–Sunday.
- Ordering cadence varies by store segment, chosen active SKU assortment, core/occasional products, stochastic quantity deviations and occasional deferred purchases.
- Only the **38 source-available SKUs** can appear in confirmed order history. Each quantity is a count of individual catalog `pack` units.

## Predictive modelling target and temporal split

- Business question: will a store reorder a specific catalog SKU in the following week?
- For feature cutoff week `w` (1–15), `reorder_due_next_week=1` **iff an actual synthetic confirmed order line for that store–SKU occurs in simulated week `w+1`**, else 0.
- The synthetic ordering schedule was defined by store–SKU-specific cadence and simulated deferrals; the target uses its resulting next-week outcome, **not an independent random bit**.
- **Important semantic limitation:** the label measures simulated *fulfilled orders*, not unmet latent demand. Out-of-stock SKUs therefore have all-zero observed outcomes even if hypothetical demand might exist.
- Features include orders **through the end of week w only**, never week w+1. Target is an evaluation outcome and must be excluded from model inputs.
- For unseen history: `weeks_since_last_purchase` and `average_units_per_order` are blank. `historical_reorder_interval_weeks` is blank until two distinct purchase weeks exist. This is intentional missingness.
- Cutoff weeks **1–9 train**; **10–12 validation**; **13–15 held-out temporal test**; **week 16 future-scoring rows** with target deliberately blank (week 17 unobserved). No random split.
- Labels on cutoff week 12 refer to simulated week-13 purchases; this is permissible for validation once that week has occurred. Temporal test labels begin with week-14 outcomes. Do not let the training pipeline see held-out targets when tuning.
- Cross-store overlap between train and test is deliberate, because the goal is to forecast future purchases for existing stores, not generalize to new stores. New-store generalization remains untested.
- No model was trained, scored or deployed in creating these files. Performance metrics are not claimed.

| Prediction split | Store-SKU-week rows | Positive labels | Positive share |
|---|---:|---:|---:|
| train | 10,800 | 1,140 | 10.56% |
| validation | 3,600 | 379 | 10.53% |
| temporal_test | 3,600 | 373 | 10.36% |
| future_scoring | 1,200 | 0 | N/A; target blank |

## WhatsApp message design and holdout

- Exactly **40** different fictional core messages, with one row per raw message and valid positionally aligned JSON item arrays.
- Prompt-development examples: **18**; frozen held-out evaluation examples: **22**. The sets are disjoint.
- Catalog edge tests: **12** additional supplementary cases; they **do not count** towards the 40 core examples.
- Known out-of-stock products keep the correct original SKU and availability status; unknown products are left with JSON null SKU.
- `peti`, `dabba`, `carton`, `box`, `packet` and `bags` are kept as raw request units unless a specific individual-pack unit is explicitly supplied. No carton factor is invented.
- `aadha dozen packs` is six individual packs by standard number conversion, not a bulk packaging-size assumption.
- Edit requests requiring a prior order or active draft demand authorized context lookup and fresh shopkeeper confirmation.
- A multi-risk message can have both privacy and prompt-injection flags; primary intent stays a single categorical label.
- None of the labelled messages has been run against a live LLM. Expected outcomes are synthetic evaluation labels, not observed model results.

## Missing-value checks

Blank/nullable values are reported below. Blank target values for week 16, unavailable historical-statistic features and optional follow-up fields are expected.

| Dataset | Field | Blank / missing cells |
|---|---|---:|
| `store_product_weekly_features.csv` | `weeks_since_last_purchase` | 14,091 |
| `store_product_weekly_features.csv` | `average_units_per_order` | 14,091 |
| `store_product_weekly_features.csv` | `historical_reorder_interval_weeks` | 15,280 |
| `store_product_weekly_features.csv` | `reorder_due_next_week` | 1,200 |
| `labelled_whatsapp_messages.csv` | `clarification_reason` | 26 |
| `labelled_whatsapp_messages.csv` | `expected_follow_up_question` | 26 |
| `catalog_edge_cases.csv` | `expected_sku_id` | 5 |

## Validation outcomes

| Check | Result | Evidence |
|---|---|---|
| Original catalog exactly 40 with authoritative fields unchanged | **PASS** | 40 variants, 12 source columns byte-equivalent as strings |
| 30 unique fictional store IDs | **PASS** | STORE001..STORE030 |
| 40 unique core message texts and IDs | **PASS** | 40 total distinct messages |
| Every confirmed order SKU exists in source catalog | **PASS** | SKUs validated against original file |
| Order product, family, size, price and category match source SKU | **PASS** | Exact source SKU attributes retained |
| Confirmed order totals match integer quantity times price | **PASS** | All line totals independently recalculated |
| No out-of-stock SKU in confirmed orders | **PASS** | BRU002 and KIT002 never fulfilled |
| No new catalog categories or SKUs | **PASS** | Matches source exactly |
| All JSON message arrays valid and aligned | **PASS** | All item arrays equal length |
| No fabricated SKU from unknown product messages | **PASS** | Unknown products have null SKU; no separate message price field |
| Every resolved message SKU is in original catalog, with exact pack identity | **PASS** | Pack size, availability, product name aligned to catalog |
| Unknown or ambiguous identity never gets a guessed exact SKU | **PASS** | Unresolved item identities use null |
| Unverified local bulk units never silently converted | **PASS** | Original local unit and raw numerical count preserved |
| Every clarification row has a question/reason | **PASS** | Follow-up natural language populated |
| Order dates within indexed 16 Monday-Sunday weeks | **PASS** | 2026-06-29 to 2026-10-18 inclusive |
| Full panel 30 stores × 40 SKUs × 16 weeks | **PASS** | 19,200 unique store-SKU-week combinations |
| Forward target exactly next simulated week purchasing event | **PASS** | Labels from following observed simulated purchase; week16 blank |
| All feature values reproducible solely from cutoff-week or earlier orders | **PASS** | Full panel constructed from historic purchase accumulator; first 240 independently checked |
| Chronological and disjoint temporal splits | **PASS** | Train1-9,val10-12,test13-15,future16 |
| Disjoint development and final LLM evaluation cases | **PASS** | 18 dev, 22 held-out; no overlap |
| Only fictional references; no contact numbers, emails, addresses | **PASS** | No real records were ingested besides non-personal product catalog |
| Supplementary edge cases clearly separate from 40 core | **PASS** | 12 supplementary tests |
| Data dictionary includes every published column | **PASS** | 88 field definitions |

**Overall result: 23/23 PASS; 0 FAIL.**

## Known limitations and approval decisions

1. **Catalog status and price:** source values are a snapshot and illustrative. Distributor team must supply live stock, genuine selling-unit conversion and verified prices before operations.
2. **Store representativeness:** only 30 simulated stores and 16 weeks. Approve prototype business assumptions before claiming relevance to a 300-store operation.
3. **Purchasing patterns:** chosen segment mix, preferred brands/categories, purchase intervals, deferral probabilities, quantities and the Monday–Sunday date window are invented; they are not market estimates.
4. **Synthetic target bias:** predictions may learn simulator periodicity and not real demand; evaluate on permissioned real transactions after privacy review before production deployment.
5. **Annotation caveat:** some Roman-Hindi shorthand has multiple possible interpretations. Manual team review is needed, particularly for pack/packet/box semantics and local-language phrasing.
6. **Security:** programmatic checking of CSV labels does not prove an LLM rejects real prompt injection. Test a real application separately, with server-enforced data access and approval gates.
7. **Human-in-the-loop:** shopkeeper must review SKU, pack, quantity, total and corrections and explicitly confirm. No automatic dispatch or cross-store disclosure.
8. **Evaluation integrity:** preserve the 22 held-out examples for final testing only; prompt engineering against them would compromise the holdout.

## Reproducibility

- Run `python generate_kirana_datasets.py product_catalog_original.csv` alongside the packaged source copy and `artifact_tool` to regenerate CSVs, the report, and Excel workbooks.
- Random seed: `20261028`. Algorithms, fixed evaluation labels and catalog aliases are embedded in the generator.
- Original uploaded catalog is copied unchanged into `product_catalog_original.csv` for traceability.
