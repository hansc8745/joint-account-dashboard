
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Load Excel data
xls = pd.ExcelFile("Joint Acct 2.xlsx")
logs_df = xls.parse('Logs ', skiprows=3)
logs_df.columns = ['Month', 'Date', 'Description', 'Category', 'Debit', 'Credit', 'Balance', 'Dropdown', '@']
logs_df = logs_df[pd.to_datetime(logs_df['Date'], errors='coerce').notna()]
logs_df['Date'] = pd.to_datetime(logs_df['Date'])
logs_df['Debit'] = pd.to_numeric(logs_df['Debit'], errors='coerce')
logs_df['Credit'] = pd.to_numeric(logs_df['Credit'], errors='coerce')
logs_df['YearMonth'] = logs_df['Date'].dt.to_period('M')

# Monthly summary
monthly_summary = logs_df.groupby('YearMonth').agg({
    'Debit': 'sum',
    'Credit': 'sum'
}).rename(columns={'Debit': 'Total Expenses', 'Credit': 'Total Deposits'}).reset_index()

monthly_summary['Net Savings'] = monthly_summary['Total Deposits'] - monthly_summary['Total Expenses']
monthly_summary['YearMonthStr'] = monthly_summary['YearMonth'].astype(str)

# Emergency fund calculation
emergency_goal = 6200
avg_net = monthly_summary['Net Savings'].mean()
suggested_contribution = round(min(avg_net * 0.8, avg_net), 2)
months_to_goal = round(emergency_goal / suggested_contribution, 1) if suggested_contribution > 0 else "N/A"

# Streamlit layout
st.title("💰 Joint Account Financial Dashboard")

# Bar and line chart
fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    subplot_titles=("Deposits vs Expenses", "Net Savings by Month"),
                    vertical_spacing=0.15)

fig.add_trace(go.Bar(
    x=monthly_summary['YearMonthStr'],
    y=monthly_summary['Total Deposits'],
    name='Total Deposits',
    marker_color='green'
), row=1, col=1)

fig.add_trace(go.Bar(
    x=monthly_summary['YearMonthStr'],
    y=monthly_summary['Total Expenses'],
    name='Total Expenses',
    marker_color='red'
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=monthly_summary['YearMonthStr'],
    y=monthly_summary['Net Savings'],
    name='Net Savings',
    mode='lines+markers',
    line=dict(color='blue', width=3)
), row=2, col=1)

fig.update_layout(
    height=700,
    barmode='group',
    template='plotly_white'
)

st.plotly_chart(fig)

# Emergency fund analysis
st.markdown(f"""
### 🛟 Emergency Fund Projection
- **Goal:** \${emergency_goal}
- **Average Net Savings:** \${avg_net:.2f}
- **Suggested Monthly Contribution:** \${suggested_contribution}
- **Estimated Time to Goal:** {months_to_goal} months
""")
