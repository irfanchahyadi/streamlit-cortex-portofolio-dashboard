import streamlit as st

st.set_page_config(
    page_title="Budgeting & Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define pages using files inside 'views/' instead of 'pages/' to avoid default routing conflicts
portfolio_page = st.Page("views/portfolio_dashboard.py", title="Portfolio Dashboard", icon="💼", default=True)
budget_page = st.Page("views/budget_forecasting.py", title="Budgeting & Forecasting", icon="📊")

pg = st.navigation([portfolio_page, budget_page])

pg.run()
