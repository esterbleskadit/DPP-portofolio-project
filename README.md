# E-Commerce Churn & Sustainability Optimisation

A data-driven interactive portfolio project bridging customer retention analytics with logistics efficiency and carbon footprint reduction (ESG).

**[View Live Dashboard]()**

---

## Project Goal

The primary goal of this application is to quantify how customer dissatisfaction, onboarding tenure, and reverse logistics directly impact business profitability and carbon ($CO_2$) emissions. By integrating churn prevention models with sustainability metrics, this tool enables e-commerce stakeholders to reduce operational waste while increasing customer lifetime value.

---

## System Architecture & Workflow

```text
[ Raw E-Commerce CSV Data ] 
           │
           ▼
[ Data Preprocessing Pipeline ] (Missing value imputation, scaling, categorical encoding)
           │
           ▼
[ XGBoost Classifier Pipeline ] ──► (Tuned Decision Threshold: 0.65)
           │
           ├──► [ Streamlit Frontend KPIs & ECharts Dashboards ]
           └──► [ SHAP TreeExplainer Waterfall Visualisations ]
           │
           ▼
[ ESG Impact & CO2 Reduction Simulator ] (Quantifies reverse logistics emissions & costs)
```
---

## Business Problem & Key Insights

* **Onboarding Risk Window:** Customers in their first 3 months (`0-3 Mos` tenure) demonstrate the highest churn risk, indicating a critical period for targeted retention campaigns.
* **Environmental Impact of Dissatisfaction:** Registered customer complaints lead to significantly elevated return rates, driving up reverse logistics mileage and overall emissions.
* **Proactive Carbon Savings:** Eliminating 20% of customer complaints projects a reduction of multiple tons of $CO_2$ reverse-logistics emissions alongside substantial cost savings.

---

## Key Features
* Interactive Multi-Tab Dashboard: Deep dive into user behavior patterns, product category churn rates, and payment mode risk distributions using Apache ECharts.
* ESG & Logistics Analytics: Analyzes correlation between customer complaints, delivery distance outliers (up to 127 km), return rates, and resulting CO2footprints.
* Real-Time Risk Simulator & Profiles: Test custom configurations or instant preset profiles (High-Risk Rural Shopper vs. Loyal Urban Regular) to visualize dynamic churn probability gauges.
* Explainable AI (XAI): Integrated SHAP waterfall charts that break down exact positive/negative feature contributions for every individual simulation.
* Executive Reporting: Instant export functionality for summarized risk evaluations and recommended retention interventions.

---

## Repository Structure

```text
ecommerce-churn-portfolio/
├── data/
│   ├── raw/                  # Original raw  dataset
│   └── processed/            # Cleaned data (clean_data.csv)
├── notebooks/
│   └── 01_eda_cleaning.ipynb # Exploratory data analysis & prototyping
├── src/
│   └── clean_pipeline.py     # Reusable data processing script
├── app.py                    # Streamlit & ECharts dashboard script
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```
---

## Data Dictionary 

| Feature Name | Description |
| :--- | :--- |
| **CustomerID** | Unique customer ID |
| **Churn** | Binary target flag (1 = Churned, 0 = Retained) |
| **Tenure** | Tenure of customer in organisation (in months) |
| **PreferredLoginDevice** | Preferred login device used by the customer |
| **CityTier** | City tier categorisation (1, 2, or 3) |
| **WarehouseToHome** | Distance in km between warehouse and customer's home |
| **PreferredPaymentMode** | Preferred payment method of customer |
| **Gender** | Gender of customer |
| **HourSpendOnApp** | Average hours spent on app or website |
| **NumberOfDeviceRegistered** | Total number of devices registered to customer account |
| **PreferedOrderCat** | Preferred order category of customer in last month |
| **SatisfactionScore** | Customer satisfaction rating (1-5 scale) |
| **MaritalStatus** | Marital status of customer |
| **NumberOfAddress** | Total number of saved delivery addresses |
| **Complain** | Binary complaint flag (1 = Raised complaint in last month, 0 = No) |
| **OrderAmountHikeFromlastYear** | Percentage increase in order spending vs. last year |
| **CouponUsed** | Total number of coupons redeemed in the last month |
| **OrderCount** | Total number of order placed in last month |
| **DaySinceLastOrder** | Day elapsed since customer's last order |
| **CashbackAmount** | Average cashback earned in the last month |

---

## Tech Stack

* Frontend & UI: Streamlit, Streamlit-ECharts
* Machine Learning & AI: Scikit-learn, XGBoost, SHAP (`TreeExplainer`)
* Data Processing: `Python 3.x`, `Pandas`, `NumPy`
* Visualisation: Matplotlib
* Environment & Package Management: uv / pip

---

## Dashboard Overview

* Overview (Tab 1): Executive metrics tracking customer retention ratios, churn by product category, payment method risks, and cohort behavioral patterns.
* Sustainability & Logistics (Tab 2): ESG breakdown of $CO_2$ emissions and returns linked to complaint status, including an interactive CO2 Reduction Simulator.
* Risk Simulator (Tab 3): Real-time single-customer churn prediction gauge powered by the XGBoost pipeline, preset selectors, SHAP explainability, and executive text export.
* Data (Tab 4): Filtered dataset viewer with CSV export functionality.

---

## Quick Start

* git clone git@github.com:esterbleskadit/DPP-portofolio-project.git
* cd ecommerce-churn-portfolio
* uv run streamlit run app.py