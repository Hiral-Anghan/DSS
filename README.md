📊 Sales Performance Decision Support System (DSS)
📌 Project Overview

The Sales Performance Decision Support System (DSS) is an interactive, role-based analytics application built using Python, Streamlit, and Plotly.
It enables Salespersons, Managers, and Admins to analyze sales performance, customer behavior, and operational efficiency through dynamic dashboards.

This system follows real-world Business Intelligence (BI) and DSS architecture, similar to tools like Power BI and Tableau.

🎯 Objectives

Provide role-based dashboards for different stakeholders

Support data-driven decision making

Analyze sales, returns, customer behavior, and trends

Enable comparative analysis and drill-downs

Maintain single source of truth for analytics logic

👥 User Roles & Capabilities
👤 Salesperson

View personal sales performance

Analyze:

Monthly & last 6 months sales trends

Product-wise, region-wise, store-wise sales

Return rate

New vs Repeat customers

KPI highlights:

Avg Monthly Sales

Total Net Sales

Return Rate

Repeat Customer %

👥 Manager

Monitor team performance

Compare salespersons

Identify strengths & improvement areas

Tabs included:

Overview – Business KPIs & trends

Salesperson Performance – Comparative analytics

Salesperson Drill-down – Full salesperson dashboard reused

⚙️ Admin

System-wide monitoring

Governance & oversight

Tabs included:

Data Overview – Entire dataset & system KPIs

Manager Comparison

Salesperson Comparison

Salesperson Drill-down – Full salesperson dashboard reused

🧠 Key DSS Features

✅ Role-based access control

📈 Interactive charts (Plotly)

🔁 New vs Repeat customer analysis

📦 Product, Region & Store analysis

📊 KPI cards with borders (Power BI–style)

🔎 Drill-down capability

♻ Reusable dashboard components

🧩 Modular code structure

🗂 Project Structure
DSS/
│
├── app.py                     # Main application controller
├── data_loader.py             # Data loading & preprocessing
│
├── dashboards/
│   ├── salesperson_dashboard.py
│   ├── manager_dashboard.py
│   └── admin_dashboard.py
│
├── Product-Sales-Region.xlsx  # Sales dataset
├── users.xlsx                 # User credentials & roles
├── README.md                  # Project documentation

🧾 Data Description
Main Dataset: Product-Sales-Region.xlsx

Key columns used:

date

region

product

salesperson

quantity

unitprice

sales (derived)

returned (0 = not returned, 1 = returned)

customername

customer_type (derived: New / Repeat)

User Dataset: users.xlsx

username

password

role (Salesperson / Manager / Admin)

⚙️ Technologies Used

Python 3.10+

Streamlit – Web application framework

Plotly Express – Interactive visualizations

Pandas & NumPy – Data processing

Excel – Data storage

▶️ How to Run the Project
1️⃣ Install dependencies
pip install streamlit pandas numpy plotly openpyxl

2️⃣ Run the application
streamlit run app.py

3️⃣ Open in browser
http://localhost:8501
