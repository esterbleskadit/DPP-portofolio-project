# E-Commerce Churn & Sustainability Analytics Dashboard

A data-driven interactive portfolio project bridging **customer retention analytics** with **logistics efficiency and carbon footprint reduction (ESG)**.

**[View Live Dashboard](https://your-streamlit-app-link.streamlit.app)** *(Update link after deployment)*

---

## Project Goal

The primary goal of this application is to quantify how customer dissatisfaction, onboarding tenure, and reverse logistics directly impact business profitability and carbon ($CO_2$) emissions. By integrating churn prevention models with sustainability metrics, this tool enables e-commerce stakeholders to reduce operational waste while increasing customer lifetime value.

---

## Business Problem & Key Business Insights

* **Onboarding Risk Window:** Customers in their first 3 months (`0-3 Mos` tenure bucket) demonstrate the highest churn risk, indicating a critical period for targeted retention campaigns.
* **Environmental Impact of Dissatisfaction:** Registered customer complaints lead to significantly elevated return rates, driving up reverse logistics mileage and overall emissions.
* **Proactive Carbon Savings:** Eliminating 20% of customer complaints projects a reduction of multiple tons of $CO_2$ reverse-logistics emissions alongside substantial cost savings.

---
## Repository Structure

```text
ecommerce-churn-portfolio/
├── data/
│   ├── raw/                  # Original raw dataset
│   └── processed/            # Cleaned data (clean_data.csv)
├── notebooks/
│   └── 01_eda_cleaning.ipynb # Exploratory data analysis & prototyping
├── src/
│   └── clean_pipeline.py     # Reusable data processing script
├── app.py                    # Streamlit & ECharts dashboard script
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation

---
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

* **Frontend & Framework: Streamlit Streamlit-ECharts
* **Data Processing:** `Python 3.x`, `Pandas`, `NumPy`
* **Environment & Package Management: uv / pip

---

## Dashboard Architecture

* **Overview (Tab 1):** Executive metrics tracking customer retention ratios, churn by product category, payment method risks, and cohort behavioral patterns.
* **Sustainability & Logistics (Tab 2):** ESG breakdown of $CO_2$ emissions and returns linked to complaint status, including an interactive **CO2 Reduction Simulator**.
* **Risk Simulator (Tab 3):** Real-time single-customer churn prediction gauge based on tenure, order recency, satisfaction scores, and logistics distance.
* **Raw Data (Tab 4):** Filtered dataset viewer with CSV export functionality.

---

## Quick Start

* **git clone <your-repo-url>
* **cd ecommerce-churn-portfolio
* **uv run streamlit run app.py

