<p align="center">
  <img src="Late%20Risk%20Predictive.png" width="300" alt="Late Delivery Risk Prediction Logo">
</p>

# Late Delivery Risk Prediction
### A Data-Driven Supply Chain Analysis

---

##### Date: 17 Oct 2026  
##### Prepared by: Edwin, Data Analyst  

---

## Project Overview

This project focuses on analyzing and predicting **late delivery risks** in a global supply chain context. Using the **DataCo Supply Chain Analytics dataset**, the goal is to uncover the drivers of delayed shipments and build predictive models that can proactively flag orders at risk.  

The analysis integrates data across **orders, products, shipping modes, payment types, customers, and geography**, enabling a holistic view of supply chain performance. Insights from this project will support logistics optimization, improve customer satisfaction, and reduce operational inefficiencies.

---

## Table of Contents
- [Problem Statement](#problem-statement)
- [Research Objectives](#research-objectives)
- [Description of Datasets](#description-of-datasets)
- [Data Preparation](#data-preparation)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
- [Model Development](#model-development)
- [Tools and Resources](#tools-and-resources)
- [Actionable Recommendations](#actionable-recommendations)
- [Conclusion](#conclusion)
- [Retrospective: Buds, Roses and Thorns](#retrospective-buds-roses-and-thorns)

---

## Problem Statement
**How can we analyse and predict whether an order is at risk of late delivery based on shipping mode, geography, product category, and customer attributes?**

---

🎯 **Research Objectives**

**1. Shipping Mode Impact Analysis**
Objective: Evaluate how different shipping modes (e.g., standard, expedited, same-day) influence the likelihood of late delivery.
Value: Identifies which service levels are most prone to delays and guides logistics optimization.

3. Geographic Risk Profiling  
Objective: Assess how delivery risk varies across regions, countries, and cities by linking Geography data with Orders.
Value: Highlights high-risk geographies where infrastructure or carrier performance may need improvement.

4. Product Category Sensitivity  
Objective: Investigate whether certain product categories (e.g., bulky items, electronics, apparel) are more likely to face late delivery.
Value: Helps tailor packaging, inventory, and shipping strategies for specific product types.

5. Customer Segment Behavior  
Objective: Analyze whether late delivery risk differs across customer segments (e.g., retail vs. wholesale, high-value vs. low-value customers).
Value: Supports differentiated service strategies and prioritization of key customer groups.

6. Predictive Modeling of Late Delivery Risk  
Objective: Build a machine learning model using order attributes (shipping days scheduled vs. actual, payment type, geography, product category) to predict late delivery risk.
Value: Enables proactive interventions such as rerouting shipments or offering alternative delivery options.

---

## Description of Datasets
- **Orders.csv**: Order lifecycle, shipping dates, delivery status, late delivery risk flag.  
- **Order Items.csv**: Line-item details including product, discount, profit ratio, and sales.  
- **Products.csv**: Product master data including category, department, and price.  
- **Categories.csv & Departments.csv**: Classification hierarchy for products.  
- **Customers.csv**: Customer demographics and segmentation.  
- **Geography.csv**: Market, region, country, and city attributes.  
- **Shipping.csv**: Shipping modes and fulfillment service levels.  
- **Payment Types.csv**: Payment methods used by customers.

---

## Data Preparation
- Cleaned and standardized column names across datasets.  
- Removed duplicates and handled missing values.  
- Joined datasets using keys such as `Order Id`, `Customer Id`, `Product Card Id`, and `Location Id`.  
- Engineered features such as **shipping delay days**, **order value**, and **profit ratio**.  

---

## Exploratory Data Analysis (EDA)
### Visualization Placeholders
- 📊 **Bar Chart**: Distribution of late delivery risk across shipping modes.  
- 🌍 **Heat Map**: Regional disparities in delivery performance.  
- 📦 **Stacked Column Chart**: Product categories with higher delay frequencies.  
- 💳 **Pie Chart**: Correlation between payment type and delivery timeliness.  
- 📈 **Line Chart**: Trends in delivery delays over time.  

---

## Model Development
- **Classification Models**: Logistic Regression, Decision Trees, Random Forests.  
- **Evaluation Metrics**: Accuracy, Precision, Recall, F1-score, ROC-AUC.  
- **Visualization Placeholders**:  
  - ROC Curve for model performance.  
  - Feature Importance Bar Chart showing top predictors of late delivery risk.  

---

## Tools and Resources
- **Python 3** (pandas, numpy, matplotlib, seaborn, scikit-learn)  
- **Jupyter Notebook / Google Colab**  
- **Power BI / Tableau** for visualization  
- **GitHub** for version control and collaboration  

---

## Actionable Recommendations
1. Optimize shipping modes with high late delivery risk.  
2. Prioritize logistics improvements in high-risk regions.  
3. Adjust inventory and packaging strategies for sensitive product categories.  
4. Implement proactive alerts using predictive models to flag at-risk orders.  
5. Enhance customer communication for orders predicted to be delayed.  

---

## Conclusion
This project demonstrates how supply chain data can be leveraged to predict late delivery risks. By combining operational, geographic, and product-level insights, organizations can proactively mitigate delays, improve customer satisfaction, and optimize logistics efficiency.

---

## Retrospective: Buds, Roses and Thorns
#### 🌱 Buds (Opportunities for Growth)
- Expand predictive modeling with advanced ML techniques (XGBoost, Neural Networks).  
- Integrate real-time tracking data for dynamic risk prediction.  
- Explore customer sentiment analysis alongside delivery performance.  

#### 🌹 Roses (What Went Well)
- Successfully merged multiple datasets into a coherent analytical framework.  
- Identified clear drivers of late delivery risk.  
- Built interpretable models with actionable insights.  

#### 🌵 Thorns (Challenges and Limitations)
- Missing or incomplete data in customer and geography tables.  
- Limited granularity in shipping mode details.  
- Potential bias due to aggregated data across regions.  

---




