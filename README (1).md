<p align="center">
  <img src="Late%20Risk%20Predictive.png" alt="Late Delivery Risk Prediction Logo" width="500">
</p>

# Late Delivery Risk Prediction

### A Data-Driven Supply Chain Analysis

---

##### Date: 18 Oct 2026

##### Prepared by: Edwin, Data Analyst

---

## Project Overview

This project analyses and predicts **late delivery risk** in a global supply chain. Using the **DataCo Supply Chain Analytics dataset** (65,752 orders, Jan 2015 – Jan 2018), it identifies the drivers of late shipments and builds a classification model that flags orders at risk **at the time the order is placed**.

The analysis integrates **orders, order items, products, categories, departments, shipping modes, payment types, customers and geography**, and is delivered as:

- a reproducible **Google Colab / Jupyter notebook** (descriptive analysis + predictive model), and
- a **Power BI** report built from the cleaned star-schema tables exported by the notebook.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Research Objectives](#research-objectives)
- [Repository Contents](#repository-contents)
- [Description of Datasets](#description-of-datasets)
- [Data Preparation](#data-preparation)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
- [Predictive Model Development](#predictive-model-development)
- [How to Run](#how-to-run)
- [Power BI Data Model](#power-bi-data-model)
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
| `Late_Delivery_Risk_Prediction.ipynb` | End-to-end notebook: data merge, 5 objectives, predictive model, exports |
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
- **Customers.csv** – customer demographics and segment (personal fields are dropped during preparation).
- **Geography.csv** – market, region, country, state and city of each order.
- **Shipping.csv** – shipping mode and shipping date per shipment.
- **Payment Types.csv** – payment methods.

---

## Data Preparation

- Read all tables directly from this repo and standardised text (trimmed spaces, fixed encoding).
- Joined tables on `Order Id`, `Order Customer Id` / `Customer Id`, `Shipment_Id`, `Location_Id`, `Payment_Type_ID`, `Product Card Id`, `Category Id` and `Department Id`.
- **Removed customer personal data** (name, email, password, street).
- Parsed mixed date formats; engineered **`delay_days`** (actual − scheduled), year / quarter / month / weekday / hour.
- Built **order-level features** from line items: number of items, quantity, order value, average discount, primary category and department.
- Created a **customer value tier** (Low / Medium / High by total spend).
- Mapped Spanish country names to ISO-3 codes for the country map.
- Checked the target: **54.8% of orders are flagged late**, so the classes are reasonably balanced.

---

## Exploratory Data Analysis (EDA)

Charts are produced by the notebook and saved in `images/`. Significance is tested with chi-square (Cramér's V for effect size).

| Objective | Visuals | Key finding |
|---|---|---|
| 1. Shipping mode | Bar: % late by mode; box plot: delay days | **The dominant driver.** First Class **95%** late, Second Class **77%**, Same Day **46%**, Standard Class **38%** (Cramér's V ≈ 0.46). |
| 2. Geography | Bar: risk by region; world map by country | **Little variation.** Regions range only from about 49% to 58%, and the region effect is not statistically significant (p ≈ 0.09). Small-country extremes reflect small samples. |
| 3. Product category | Treemap; stacked bar by department | **No meaningful department effect** (p ≈ 0.76); department rates sit between 54% and 59%. Extreme category values (e.g. Golf Bags & Carts) rest on very few items. |
| 4. Customer segment | Donut: share of late; clustered bars | **No difference** between Consumer, Corporate and Home Office (about 55% each) or across value tiers (p > 0.6). |
| 5. Temporal | Monthly and quarterly line; KPI card | **Stable over time.** Late risk stays around 55% with no trend (about 0 pp/month) and no significant seasonality. |

> **Takeaway:** lateness in this dataset is driven by the **shipping service level**, not by where the order goes, what is in it, or who orders it.

An extra check found that **payment type** also shows variation (Transfer about 48% late vs. about 57% for Cash, Debit and Payment).

---

## Predictive Model Development

**Goal:** classify each order as late or on time using only information available at order time.

- **Features:** shipping mode, scheduled shipping days, market, region, country, customer segment, payment type, primary category / department, items, quantity, order value, discount, unit price, month, weekday, hour.
- **Leakage control:** `Days for shipping (real)`, `delay_days`, `shipping date`, `Delivery Status` and `Order Status` are **excluded**, because they are only known after delivery.
- **Method:** 80/20 stratified split; Logistic Regression, Random Forest and Gradient Boosting compared; best model validated with 5-fold cross-validation.
- **Evaluation metrics:** Accuracy, Precision, Recall, F1-score, ROC-AUC.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| **Gradient Boosting** | **0.716** | 0.857 | 0.578 | 0.691 | **0.768** |
| Random Forest | 0.716 | 0.857 | 0.579 | 0.691 | 0.764 |
| Logistic Regression | 0.703 | 0.844 | 0.561 | 0.674 | 0.743 |

Gradient Boosting 5-fold cross-validated ROC-AUC: **0.769 ± 0.004**.

**What the model says**
- Orders it flags as late are right about **86%** of the time (high precision), but it **catches only about 58%** of truly late orders (moderate recall). The probability threshold can be lowered if catching more late orders matters more than false alarms.
- **Shipping mode is by far the most important feature.** Order hour and payment type add small signals; geography, category, segment and value add essentially nothing.
- Treat the order-hour signal with caution – it is likely an artefact of how the dataset was generated rather than a real operational driver.

Visuals: ROC curves, confusion matrix and feature-importance chart (`images/06_*.png`).

---

## How to Run

1. Open `Late_Delivery_Risk_Prediction.ipynb` in **Google Colab** (File → Upload notebook).
2. Choose **Runtime → Run all**. The notebook reads the CSVs directly from this repository – no Google Drive needed.
3. The last cell downloads `late_risk_outputs.zip` (charts, `master_orders.csv`, model results and Power BI tables). Colab storage is temporary, so download it before the session ends.
4. Upload the outputs you want to keep (e.g. `master_orders.csv`, `powerbi/`, `images/`) to this repository.

---

## Power BI Data Model

The notebook exports a star schema to `powerbi/`:

- **Facts:** `fact_orders`, `fact_order_items`, `fact_predictions`
- **Dimensions:** `dim_date`, `dim_geography`, `dim_customer`, `dim_product`, `dim_shipping`, `dim_payment`
- **Model tables:** `model_metrics`, `model_roc_points`, `model_feature_importance`

**Relationships:** `fact_orders` → `Shipment_Id`, `Location_Id`, `Order Customer Id`, `Payment_Type_ID` to their dimensions; `fact_orders[order_day]` → `dim_date[Date]`; `fact_order_items` → `fact_orders` (`Order Id`) and `dim_product`; `fact_predictions` → `fact_orders` (`Order Id`).

**Core measure:** `Late % = DIVIDE(SUM(fact_orders[late]), COUNTROWS(fact_orders))`

---

## Tools and Resources

- **Python 3** (pandas, numpy, matplotlib, seaborn, plotly, scipy, scikit-learn)
- **Google Colab / Jupyter Notebook**
- **Power BI** for the dashboard
- **GitHub** for data hosting and version control

---

## Actionable Recommendations

1. **Review the First Class and Second Class service levels.** Their scheduled windows (1 and 2 days) are routinely missed (95% and 77% late). Either lengthen the promised windows or fix carrier and fulfilment capacity for these services.
2. **Re-examine Same Day and Standard Class** promises: Standard is late on 38% of orders even with a 4-day window.
3. **Do not prioritise region, category or segment-specific fixes.** The data shows no meaningful differences there; effort is better spent on shipping-service performance.
4. **Use the model to flag at-risk orders at checkout**, focusing proactive customer communication on orders with a High risk band.
5. **Set the alert threshold by business cost.** Lower it to catch more late orders (higher recall) if missed delays are costlier than extra notifications.
6. **Investigate payment-type differences** (e.g. Transfer orders are late less often) to see whether a process difference explains them.

---

## Limitations

- Shipping mode and scheduled days are closely linked, so the model largely learns the service-level effect; other drivers are weak in this data.
- Recall is moderate (about 58%): some late orders are not flagged.
- Category and country results for small groups rest on few orders.
- The dataset appears to be a synthetic or simulated benchmark, so uniform results across geography, segment and time may not reflect a real operation.
- The lateness flag follows "actual > scheduled days" for about 97% of orders; the remaining 3% are defined by the source data.

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

- Merged nine tables into one coherent, reproducible analytical pipeline that runs straight from GitHub.
- Clearly identified shipping mode as the main driver and showed other factors are not significant.
- Excluded leakage variables so the model reflects what is truly known at order time.
- Exported a clean star schema ready for Power BI.

#### 🌵 Thorns (Challenges and Limitations)

- Spanish country names, mixed date formats and inconsistent file names needed cleaning.
- Limited granularity: shipping details are only available at mode level.
- Most explanatory variables show little signal, which limits model accuracy.
