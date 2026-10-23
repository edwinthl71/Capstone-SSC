<p align="center">
  <img src="Late%20Risk%20Predictive.png" alt="Late Delivery Risk Prediction Logo" width="500">
</p>

# Late Delivery Risk Prediction

### A Data-Driven Supply Chain Analysis

---

##### Date: 23 Oct 2026

##### Prepared by: Edwin, Data Analyst

---

## Project Overview

This project analyses and predicts **late delivery risk** in a global supply chain. Using the **DataCo Supply Chain Analytics dataset** (65,752 orders, Jan 2015 – Jan 2018), it identifies the drivers of late shipments and builds a classification model that flags orders at risk **at the time the order is placed**.

The analysis integrates **orders, order items, products, categories, departments, shipping modes, payment types, customers and geography**, and is delivered as:

- a reproducible **Google Colab notebook** (data cleaning, descriptive analysis of five research objectives, predictive model), and
- a **Power BI** report built from the cleaned star-schema tables exported by the notebook.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Research Objectives](#research-objectives)
- [Repository Contents](#repository-contents)
- [Description of Datasets](#description-of-datasets)
- [Data Preparation](#data-preparation)
- [Exploratory Data Analysis (EDA) and Observations](#exploratory-data-analysis-eda-and-observations)
- [Predictive Model Development](#predictive-model-development)
- [How to Run](#how-to-run)
- [Power BI Report and Data Model](#power-bi-report-and-data-model)
- [Tools and Resources](#tools-and-resources)
- [Actionable Recommendations](#actionable-recommendations)
- [Limitations](#limitations)
- [Conclusion](#conclusion)
- [Retrospective: Buds, Roses and Thorns](#retrospective-buds-roses-and-thorns)

---

## Problem Statement

**How can we analyse and predict whether an order is at risk of late delivery based on shipping mode, geography, product category and customer attributes?**

The `Orders` table includes a `Late_delivery_risk` flag plus scheduled vs. actual shipping days, which makes it well suited to a classification model that helps reduce fulfilment issues.

---

## Research Objectives

**1. Shipping Mode Impact Analysis**
Evaluate how different shipping modes (Standard, Second Class, First Class, Same Day) influence the likelihood of late delivery.
*Value:* identifies which service levels are most prone to delays and guides logistics optimisation.

**2. Geographic Risk Profiling**
Assess how delivery risk varies across regions, countries and cities by linking Geography data with Orders.
*Value:* highlights high-risk geographies where infrastructure or carrier performance may need improvement.

**3. Product Category Sensitivity**
Investigate whether certain product categories or departments are more likely to face late delivery.
*Value:* helps tailor packaging, inventory and shipping strategies for specific product types.

**4. Customer Segment Behaviour**
Analyse whether late delivery risk differs across customer segments (Consumer, Corporate, Home Office) and between high-, medium- and low-value customers.
*Value:* supports differentiated service strategies and prioritisation of key customer groups.

**5. Temporal Trends in Delivery Delays**
Examine how late delivery risk changes over time (monthly and quarterly), identifying seasonal patterns or long-term trends.
*Value:* shows whether delays are cyclical, improving or worsening, supporting resource planning and realistic customer expectations.

---

## Repository Contents

| File | Description |
|---|---|
| `Late_Delivery_Risk_Prediction.ipynb` | End-to-end notebook: load and clean data, 5 objectives with observations, predictive model, exports |
| `Categories.csv`, `Customers.csv`, `Departments.csv`, `Geography.csv`, `Order Items.csv`, `Orders.csv`, `Payment Types.csv`, `Products.csv`, `Shipping.csv` | Source tables |
| `master_orders.csv` | Cleaned, merged order-level dataset produced by the notebook |
| `powerbi/` | Cleaned star-schema tables and model outputs for Power BI |
| `images/` | Charts exported from the notebook |
| `Late Risk Predictive.png` | Project logo |

---

## Description of Datasets

- **Orders.csv** – order lifecycle, shipping dates, delivery status, `Late_delivery_risk` flag, real vs. scheduled shipping days.
- **Order Items.csv** – line-item details: product, quantity, discount, profit ratio, sales.
- **Products.csv** – product master data and price.
- **Categories.csv & Departments.csv** – product classification hierarchy.
- **Customers.csv** – customer demographics and segment.
- **Geography.csv** – market, region, country, state and city of each order.
- **Shipping.csv** – shipping mode and shipping date per shipment.
- **Payment Types.csv** – payment methods.

---

## Data Preparation

Step 2 of the notebook is split into labelled blocks (2A to 2E). All cleaning is in one clearly marked cell, **2B – DATA CLEANING**, with numbered tasks and a cleaning log.

| Task | Cleaning operation | Result on this dataset |
|---|---|---|
| **2B-1** | Standardise text (trim spaces, collapse repeated spaces) | 6,630 cells fixed, mostly in Geography (5,923) and Customers (695) |
| **2B-2** | Remove personal data (name, email, password, street) | 5 customer columns dropped |
| **2B-3** | Drop mostly empty or unused columns | `Order Zipcode` (87% missing), `Product Description` (100% missing) and `Customer Zipcode` dropped |
| **2B-4** | Remove duplicate rows | 0 duplicates found |
| **2B-5** | Check remaining missing values | 0 missing cells left in all tables |
| **2B-6** | Convert text dates to datetime (mixed source formats) | 0 unparseable dates |
| **2B-7** | Validity and key-integrity checks | 0 problems: no negative days, quantities or sales; all keys unique; late flag is only 0 or 1 |

After cleaning:
- **2C Merge:** tables are joined on `Order Id`, `Order Customer Id`, `Shipment_Id`, `Location_Id`, `Payment_Type_ID`, `Product Card Id`, `Category Id` and `Department Id`. Row counts are checked so no merge duplicates orders. Spanish country names are mapped to ISO-3 codes for the map.
- **2D Feature engineering:** `delay_days` (actual − scheduled), date parts, order-level item features (number of items, quantity, order value, discount, primary category and department) and a customer value tier (Low / Medium / High by total spend).
- **2E Validation:** no orders without items, customer segment or region; 0 missing values in the final table. The target is balanced: **54.8% of orders are flagged late**.

---

## Exploratory Data Analysis (EDA) and Observations

Charts are produced by the notebook and saved in `images/`. Significance is tested with chi-square, with Cramér's V as the effect size. Each objective has an **Observation** cell in the notebook.

### Objective 1 – Shipping mode (the dominant driver)
- Late rate by mode: First Class **95.3%**, Second Class **76.7%**, Same Day **46.2%**, Standard Class **38.1%** (overall 54.8%).
- The premium services miss their promises: First Class is scheduled for 1 day but averages 2; Second Class is scheduled for 2 but averages 4. Standard Class averages exactly its 4 scheduled days.
- Chi-square p < 0.001, Cramér's V = 0.46, the largest effect of any variable tested.

### Objective 2 – Geography (no significant effect)
- Regions range from 49.5% (Canada) to 57.6% (Central Africa); the large regions sit near the average. Markets differ by only 1.2 points.
- Chi-square p = 0.086, V = 0.022: not significant. Country extremes (for example Portugal 45.8%, South Korea 60.7%) rest on small samples.

### Objective 3 – Product category (no meaningful effect)
- Department late rates sit between 54.4% (Discs Shop) and 58.9% (Pet Shop); chi-square p = 0.756, V = 0.006.
- Extreme categories are small samples (Golf Bags & Carts 68.9% on 61 items). Lacrosse, Pet Supplies and Cameras are reasonable watch items.

### Objective 4 – Customer segment (no difference)
- Consumer 54.7%, Corporate 54.7%, Home Office 55.2% (p = 0.613). Low, medium and high value customers are all about 54.8% (p = 0.991).
- Shipping mode explains the risk inside every segment (First Class 95–96%, Standard 37–39%).

### Objective 5 – Temporal trends (flat)
- Monthly late risk ranges from 52.4% to 57.3% around the 54.8% average, with a trend of about 0 percentage points per month.
- No meaningful seasonality (calendar months 53.7%–55.4%, p = 0.716). The 56.3% for early 2018 is a single month.

> **Takeaway:** lateness in this dataset is driven by the **shipping service level**, not by where the order goes, what is in it, when it is placed or who orders it.

An extra check found that **payment type** also varies (Transfer about 48% late vs about 57% for Cash, Debit and Payment).

---

## Predictive Model Development

**Goal:** classify each order as late or on time using only information available at order time.

- **Features:** shipping mode, scheduled shipping days, market, region, country, customer segment, payment type, primary category / department, items, quantity, order value, discount, unit price, month, weekday, hour.
- **Leakage control:** `Days for shipping (real)`, `delay_days`, `shipping date`, `Delivery Status` and `Order Status` are **excluded**, because they are only known after delivery.
- **Method:** 80/20 stratified split; Logistic Regression, Random Forest and Gradient Boosting compared; best model validated with 5-fold cross-validation.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| **Gradient Boosting** | **0.716** | 0.857 | 0.578 | 0.691 | **0.768** |
| Random Forest | 0.716 | 0.857 | 0.579 | 0.691 | 0.764 |
| Logistic Regression | 0.703 | 0.844 | 0.561 | 0.674 | 0.743 |

Gradient Boosting 5-fold cross-validated ROC-AUC: **0.769 ± 0.004**.

**Observations**
- **High precision, moderate recall.** About 86% of orders flagged late really were late, but only 58% of truly late orders are caught (4,170 of 7,210 in the test set; 3,040 missed, 694 false alarms).
- **Shipping mode drives the predictions.** Permutation importance: shipping mode 0.244, order hour 0.043, payment type 0.015; everything else is close to zero. The order-hour signal is likely a data artefact.
- **Risk bands separate well.** In the test set, 86.5% of High-band orders were late, against 39.7% in Medium and 22.4% in Low.

---

## How to Run

1. Open `Late_Delivery_Risk_Prediction.ipynb` in **Google Colab** (File → Upload notebook).
2. Choose **Runtime → Run all**. The notebook reads the CSVs directly from this repository, so Google Drive is not needed.
3. The last cell downloads `late_risk_outputs.zip` (charts, `master_orders.csv`, model results and Power BI tables). Colab storage is temporary, so download it before the session ends.
4. Upload the outputs you want to keep (for example `master_orders.csv`, `powerbi/`, `images/`) to this repository.

---

## Power BI Report and Data Model

The report has six pages: one per research objective, plus predictive model results. Each page has a title banner with the key takeaway, slicers, KPI cards and charts.

The notebook exports a star schema to `powerbi/`:

- **Facts:** `fact_orders`, `fact_order_items`, `fact_predictions`
- **Dimensions:** `dim_date`, `dim_geography`, `dim_customer`, `dim_product`, `dim_shipping`, `dim_payment`
- **Model tables:** `model_metrics`, `model_roc_points`, `model_feature_importance`

**Relationships:** `fact_orders` → `Shipment_Id`, `Location_Id`, `Order Customer Id`, `Payment_Type_ID` to their dimensions; `fact_orders[order_day]` → `dim_date[Date]`; `fact_order_items` → `fact_orders` (`Order Id`) and `dim_product`; `fact_predictions` → `fact_orders` (`Order Id`).

**Core measure:** `Late % = DIVIDE(SUM(fact_orders[late]), COUNTROWS(fact_orders))`

---

## Tools and Resources

- **Python 3** (pandas, numpy, matplotlib, seaborn, plotly, scipy, scikit-learn)
- **Google Colab**
- **Power BI Desktop** for the dashboard
- **GitHub** for data hosting and version control

---

## Actionable Recommendations

1. **Review the First Class and Second Class service levels.** Their scheduled windows (1 and 2 days) are routinely missed (95% and 77% late). Either lengthen the promised windows to about 2 and 4 days or fix carrier and fulfilment capacity for these services.
2. **Re-examine Same Day and Standard Class** promises: Standard is late on 38% of orders even though its average matches the 4-day window.
3. **Do not prioritise region, category or segment-specific fixes.** The data shows no significant differences there.
4. **Use the model to flag at-risk orders at checkout**, focusing proactive customer communication on orders in the High risk band.
5. **Set the alert threshold by business cost.** Lower it to catch more late orders (higher recall) if missed delays cost more than extra notifications.
6. **Do not plan around seasonality.** Late risk is constant through the year, so peak-season capacity will not fix it; service-level design will.
7. **Investigate payment-type differences** (Transfer orders are late less often) to see whether a process difference explains them.

---

## Limitations

- Shipping mode and scheduled days are closely linked, so the model largely learns the service-level effect; other drivers are weak in this data.
- Recall is moderate (about 58%): some late orders are not flagged.
- Category and country results for small groups rest on few orders.
- The dataset appears to be a synthetic or simulated benchmark, so uniform results across geography, segment and time may not reflect a real operation.
- The late flag matches "actual > scheduled days" for about 97.5% of orders; the remainder follows the source definition.

---

## Conclusion

This project shows that late delivery risk in this supply chain is **driven mainly by the shipping service level**, while geography, product category, customer segment and time have little effect. A Gradient Boosting model predicts late delivery with **ROC-AUC ≈ 0.77** using only order-time information, giving the business a practical way to flag at-risk orders and focus improvements on the shipping modes that fail most often.

---

## Retrospective: Buds, Roses and Thorns

#### 🌱 Buds (Opportunities for Growth)

- Test XGBoost / LightGBM and tune the decision threshold for higher recall.
- Add carrier, warehouse and real-time tracking data for dynamic risk prediction.
- Explore customer satisfaction and sentiment alongside delivery performance.

#### 🌹 Roses (What Went Well)

- Merged nine tables into one coherent, reproducible pipeline that runs straight from GitHub.
- Built a numbered, logged data-cleaning step with validity checks, and added an observation to every objective.
- Clearly identified shipping mode as the main driver and showed other factors are not significant.
- Excluded leakage variables so the model reflects what is truly known at order time.
- Exported a clean star schema and built a six-page Power BI report from it.

#### 🌵 Thorns (Challenges and Limitations)

- Spanish country names, mixed date formats, stray whitespace and inconsistent file names needed cleaning.
- Limited granularity: shipping details are only available at mode level.
- Most explanatory variables show little signal, which limits model accuracy.
