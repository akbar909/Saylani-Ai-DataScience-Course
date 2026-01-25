import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS FOR PRO UI ============
st.markdown("""
<style>
    /* Remove top padding */
    .block-container {
        padding-top: 1rem !important;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
    }
    
    /* KPI Cards - Compact */
    .kpi-card {
        background: linear-gradient(145deg, #1e1e3f, #2a2a5a);
        border-radius: 12px;
        padding: 12px 10px;
        text-align: center;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    }
    
    .kpi-value {
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 6px 0;
    }
    
    .kpi-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-icon {
        font-size: 1.3rem;
        margin-bottom: 2px;
    }
    
    .kpi-delta-positive {
        color: #22c55e;
        font-size: 0.75rem;
    }
    
    .kpi-delta-negative {
        color: #ef4444;
        font-size: 0.75rem;
    }
    
    /* Section Headers - Compact */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin: 15px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(99, 102, 241, 0.5);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e1e3f, #0f0f23);
    }
    
    /* Reduce sidebar top padding */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    
    /* Tab styling - Compact */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: rgba(30, 30, 63, 0.5);
        border-radius: 10px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #94a3b8;
        padding: 8px 14px;
        font-size: 0.85rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
    }
    
    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(90deg, #22c55e, #16a34a);
        color: white;
        border: none;
        border-radius: 8px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        color: #60a5fa;
    }
</style>
""", unsafe_allow_html=True)


# ============ DATA LOADING FUNCTION ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "cleaned_sales_data.csv")

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, parse_dates=["Sale_Date"])

    # Calculate Profit
    df["Profit"] = (df["Unit_Price"] - df["Unit_Cost"]) * df["Quantity_Sold"]
    df["Profit_Margin"] = (df["Unit_Price"] - df["Unit_Cost"]) / df["Unit_Price"]

    # Extract time features
    df["Month"] = df["Sale_Date"].dt.to_period("M").astype(str)
    df["Day_of_Week"] = df["Sale_Date"].dt.day_name()
    df["Year"] = df["Sale_Date"].dt.year

    return df


# ============ LOAD DATA ============
df = load_data(DATA_PATH)

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## 🎛️ Dashboard Controls")
    
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    # Date Range Filter
    min_date = df['Sale_Date'].min().date()
    max_date = df['Sale_Date'].max().date()
    
    date_range = st.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Region Filter
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("🌍 Region", regions)
    
    # Product Category Filter
    categories = ['All'] + sorted(df['Product_Category'].unique().tolist())
    selected_category = st.selectbox("🛒 Product Category", categories)
    
    # Sales Channel Filter
    channels = ['All'] + sorted(df['Sales_Channel'].unique().tolist())
    selected_channel = st.selectbox("📡 Sales Channel", channels)
    
    # Customer Type Filter
    customer_types = ['All'] + sorted(df['Customer_Type'].unique().tolist())
    selected_customer = st.selectbox("👥 Customer Type", customer_types)
    
    # Payment Method Filter
    payment_methods = ['All'] + sorted(df['Payment_Method'].unique().tolist())
    selected_payment = st.selectbox("💳 Payment Method", payment_methods)


# ============ APPLY FILTERS ============
filtered_df = df.copy()

# Date filter
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Sale_Date'].dt.date >= date_range[0]) & 
        (filtered_df['Sale_Date'].dt.date <= date_range[1])
    ]

# Apply other filters
if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['Product_Category'] == selected_category]
if selected_channel != 'All':
    filtered_df = filtered_df[filtered_df['Sales_Channel'] == selected_channel]
if selected_customer != 'All':
    filtered_df = filtered_df[filtered_df['Customer_Type'] == selected_customer]
if selected_payment != 'All':
    filtered_df = filtered_df[filtered_df['Payment_Method'] == selected_payment]


# ============ HEADER ============
st.markdown("""
    <div style="text-align: center; padding: 5px 0 10px 0;">
        <h1 style="font-size: 1.8rem; font-weight: 700; margin: 0;
            background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;">
            📊 Sales Analytics Dashboard
        </h1>
        <p style="color: #94a3b8; font-size: 0.9rem; margin: 5px 0 0 0;">
            Comprehensive insights into your sales performance
        </p>
    </div>
""", unsafe_allow_html=True)


# ============ KPI CARDS ============
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_sales = filtered_df['Sales_Amount'].sum()
total_quantity = filtered_df['Quantity_Sold'].sum()
total_transactions = len(filtered_df)
avg_discount = filtered_df['Discount'].mean() * 100
total_profit = filtered_df['Profit'].sum()
avg_order_value = filtered_df['Sales_Amount'].mean()

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Total Sales</div>
            <div class="kpi-value">${total_sales:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📦</div>
            <div class="kpi-label">Quantity Sold</div>
            <div class="kpi-value">{total_quantity:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🧾</div>
            <div class="kpi-label">Transactions</div>
            <div class="kpi-value">{total_transactions:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-label">Avg Discount</div>
            <div class="kpi-value">{avg_discount:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">💎</div>
            <div class="kpi-label">Total Profit</div>
            <div class="kpi-value">${total_profit:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">Avg Order Value</div>
            <div class="kpi-value">${avg_order_value:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ============ TABS ============
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Sales Overview", 
    "💎 Profit Analysis", 
    "👥 Customer Insights",
    "🏆 Top Performers",
    "💡 Key Insights",
    "📋 Data Explorer"
])


# ============ TAB 1: SALES OVERVIEW ============
with tab1:
    st.markdown('<div class="section-header">📅 Sales Trend Over Time</div>', unsafe_allow_html=True)
    
    # Sales trend
    sales_trend = filtered_df.groupby(filtered_df['Sale_Date'].dt.to_period('M').astype(str)).agg({
        'Sales_Amount': 'sum',
        'Quantity_Sold': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=sales_trend['Sale_Date'], 
        y=sales_trend['Sales_Amount'],
        mode='lines+markers',
        name='Sales',
        line=dict(color='#60a5fa', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(96, 165, 250, 0.2)'
    ))
    fig_trend.add_trace(go.Scatter(
        x=sales_trend['Sale_Date'], 
        y=sales_trend['Profit'],
        mode='lines+markers',
        name='Profit',
        line=dict(color='#22c55e', width=3),
        marker=dict(size=8)
    ))
    
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Row 2: Category and Region
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">🛒 Sales by Product Category</div>', unsafe_allow_html=True)
        category_sales = filtered_df.groupby('Product_Category')['Sales_Amount'].sum().reset_index()
        fig_category = px.pie(
            category_sales, 
            values='Sales_Amount', 
            names='Product_Category',
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        fig_category.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.2)
        )
        fig_category.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">🌍 Sales by Region</div>', unsafe_allow_html=True)
        region_sales = filtered_df.groupby('Region')['Sales_Amount'].sum().reset_index()
        fig_region = px.bar(
            region_sales.sort_values('Sales_Amount', ascending=True), 
            x='Sales_Amount', 
            y='Region',
            orientation='h',
            color='Sales_Amount',
            color_continuous_scale='Blues'
        )
        fig_region.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    # Row 3: Sales Rep and Payment Method
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">👨‍💼 Sales by Sales Rep</div>', unsafe_allow_html=True)
        rep_sales = filtered_df.groupby('Sales_Rep').agg({
            'Sales_Amount': 'sum',
            'Quantity_Sold': 'sum'
        }).reset_index().sort_values('Sales_Amount', ascending=False)
        
        fig_rep = px.bar(
            rep_sales, 
            x='Sales_Rep', 
            y='Sales_Amount',
            color='Quantity_Sold',
            color_continuous_scale='Viridis',
            text='Sales_Amount'
        )
        fig_rep.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_rep.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            coloraxis_colorbar=dict(title='Qty'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_rep, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">💳 Sales by Payment Method</div>', unsafe_allow_html=True)
        payment_sales = filtered_df.groupby('Payment_Method')['Sales_Amount'].sum().reset_index()
        fig_payment = px.pie(
            payment_sales, 
            values='Sales_Amount', 
            names='Payment_Method',
            color_discrete_sequence=px.colors.sequential.Tealgrn_r
        )
        fig_payment.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400
        )
        fig_payment.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_payment, use_container_width=True)


# ============ TAB 2: PROFIT ANALYSIS ============
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">💎 Profit by Product Category</div>', unsafe_allow_html=True)
        profit_category = filtered_df.groupby('Product_Category').agg({
            'Profit': 'sum',
            'Profit_Margin': 'mean'
        }).reset_index().sort_values('Profit', ascending=False)
        
        fig_profit_cat = px.bar(
            profit_category, 
            x='Product_Category', 
            y='Profit',
            color='Profit_Margin',
            color_continuous_scale='RdYlGn',
            text='Profit'
        )
        fig_profit_cat.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_profit_cat.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            coloraxis_colorbar=dict(title='Margin %'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_profit_cat, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">🌍 Profit by Region</div>', unsafe_allow_html=True)
        profit_region = filtered_df.groupby('Region').agg({
            'Profit': 'sum',
            'Profit_Margin': 'mean'
        }).reset_index().sort_values('Profit', ascending=False)
        
        fig_profit_reg = px.bar(
            profit_region, 
            x='Region', 
            y='Profit',
            color='Profit_Margin',
            color_continuous_scale='RdYlGn',
            text='Profit'
        )
        fig_profit_reg.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_profit_reg.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            coloraxis_colorbar=dict(title='Margin %'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_profit_reg, use_container_width=True)
    
    # Profit Heatmap
    st.markdown('<div class="section-header">🔥 Profit Heatmap: Category vs Region</div>', unsafe_allow_html=True)
    profit_heatmap = filtered_df.pivot_table(
        values='Profit', 
        index='Product_Category', 
        columns='Region', 
        aggfunc='sum'
    ).fillna(0)
    
    fig_heatmap = px.imshow(
        profit_heatmap,
        color_continuous_scale='RdYlGn',
        aspect='auto',
        text_auto='.0f'
    )
    fig_heatmap.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        height=400
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)


# ============ TAB 3: CUSTOMER INSIGHTS ============
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">👥 New vs Returning Customers</div>', unsafe_allow_html=True)
        customer_sales = filtered_df.groupby('Customer_Type').agg({
            'Sales_Amount': 'sum',
            'Quantity_Sold': 'sum',
            'Product_ID': 'count'
        }).reset_index()
        customer_sales.columns = ['Customer_Type', 'Sales', 'Quantity', 'Transactions']
        
        fig_customer = px.bar(
            customer_sales, 
            x='Customer_Type', 
            y=['Sales', 'Transactions'],
            barmode='group',
            color_discrete_sequence=['#60a5fa', '#a78bfa']
        )
        fig_customer.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig_customer, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">📡 Online vs Retail Sales</div>', unsafe_allow_html=True)
        channel_sales = filtered_df.groupby('Sales_Channel').agg({
            'Sales_Amount': 'sum',
            'Profit': 'sum'
        }).reset_index()
        
        fig_channel = px.pie(
            channel_sales, 
            values='Sales_Amount', 
            names='Sales_Channel',
            hole=0.6,
            color_discrete_sequence=['#22c55e', '#6366f1']
        )
        fig_channel.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            annotations=[dict(text='Channel', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        fig_channel.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig_channel, use_container_width=True)
    
    # Day of Week Analysis
    st.markdown('<div class="section-header">📆 Sales by Day of Week</div>', unsafe_allow_html=True)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_sales = filtered_df.groupby('Day_of_Week')['Sales_Amount'].sum().reindex(day_order).reset_index()
    
    fig_day = px.bar(
        day_sales, 
        x='Day_of_Week', 
        y='Sales_Amount',
        color='Sales_Amount',
        color_continuous_scale='Purples'
    )
    fig_day.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        height=350,
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig_day, use_container_width=True)


# ============ TAB 4: TOP PERFORMERS ============
with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">🔝 Top 10 Products by Revenue</div>', unsafe_allow_html=True)
        top_products = filtered_df.groupby('Product_ID').agg({
            'Sales_Amount': 'sum',
            'Quantity_Sold': 'sum',
            'Profit': 'sum'
        }).reset_index().nlargest(10, 'Sales_Amount')
        top_products['Product_ID'] = top_products['Product_ID'].astype(str)
        
        fig_top = px.bar(
            top_products, 
            x='Sales_Amount', 
            y='Product_ID',
            orientation='h',
            color='Profit',
            color_continuous_scale='Viridis',
            text='Sales_Amount'
        )
        fig_top.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_top.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=450,
            coloraxis_colorbar=dict(title='Profit'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=False, categoryorder='total ascending')
        )
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">🏆 Top Sales Reps Leaderboard</div>', unsafe_allow_html=True)
        top_reps = filtered_df.groupby('Sales_Rep').agg({
            'Sales_Amount': 'sum',
            'Profit': 'sum',
            'Product_ID': 'count'
        }).reset_index()
        top_reps.columns = ['Sales_Rep', 'Total Sales', 'Total Profit', 'Deals Closed']
        top_reps = top_reps.sort_values('Total Sales', ascending=False)
        
        # Style the dataframe
        st.dataframe(
            top_reps.style.format({
                'Total Sales': '${:,.0f}',
                'Total Profit': '${:,.0f}',
                'Deals Closed': '{:,}'
            }).background_gradient(cmap='Blues', subset=['Total Sales'])
            .background_gradient(cmap='Greens', subset=['Total Profit']),
            use_container_width=True,
            height=400
        )
    
    # Bottom 10 products
    st.markdown('<div class="section-header">⚠️ Bottom 10 Products (Needs Attention)</div>', unsafe_allow_html=True)
    bottom_products = filtered_df.groupby('Product_ID').agg({
        'Sales_Amount': 'sum',
        'Quantity_Sold': 'sum',
        'Profit': 'sum'
    }).reset_index().nsmallest(10, 'Sales_Amount')
    bottom_products['Product_ID'] = bottom_products['Product_ID'].astype(str)
    
    fig_bottom = px.bar(
        bottom_products.sort_values('Sales_Amount', ascending=True), 
        x='Sales_Amount', 
        y='Product_ID',
        orientation='h',
        color='Profit',
        color_continuous_scale='Reds_r',
        text='Sales_Amount'
    )
    fig_bottom.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig_bottom.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        height=400,
        coloraxis_colorbar=dict(title='Profit'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_bottom, use_container_width=True)


# ============ TAB 5: KEY INSIGHTS ============
with tab5:
    st.markdown('<div class="section-header">💡 Key Business Insights</div>', unsafe_allow_html=True)
    
    # Calculate insights
    best_category = filtered_df.groupby('Product_Category')['Sales_Amount'].sum().idxmax()
    best_category_sales = filtered_df.groupby('Product_Category')['Sales_Amount'].sum().max()
    
    best_region = filtered_df.groupby('Region')['Sales_Amount'].sum().idxmax()
    best_region_sales = filtered_df.groupby('Region')['Sales_Amount'].sum().max()
    
    best_rep = filtered_df.groupby('Sales_Rep')['Sales_Amount'].sum().idxmax()
    best_rep_sales = filtered_df.groupby('Sales_Rep')['Sales_Amount'].sum().max()
    
    most_profitable_category = filtered_df.groupby('Product_Category')['Profit'].sum().idxmax()
    most_profitable_category_profit = filtered_df.groupby('Product_Category')['Profit'].sum().max()
    
    best_day = filtered_df.groupby('Day_of_Week')['Sales_Amount'].sum().idxmax()
    
    avg_profit_margin = filtered_df['Profit_Margin'].mean()
    
    new_vs_returning = filtered_df.groupby('Customer_Type')['Sales_Amount'].sum()
    dominant_customer = new_vs_returning.idxmax()
    
    online_vs_retail = filtered_df.groupby('Sales_Channel')['Sales_Amount'].sum()
    dominant_channel = online_vs_retail.idxmax()
    
    best_payment = filtered_df.groupby('Payment_Method')['Sales_Amount'].sum().idxmax()
    
    # Display insights in cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e3a5f, #2a4a6f); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #22c55e;">
            <h3 style="color: #22c55e; margin: 0 0 10px 0; font-size: 1rem;">🏆 Top Performing Category</h3>
            <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;"><strong>{best_category}</strong> leads with <strong>${best_category_sales:,.0f}</strong> in sales</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e3a5f, #2a4a6f); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #60a5fa;">
            <h3 style="color: #60a5fa; margin: 0 0 10px 0; font-size: 1rem;">🌍 Best Region</h3>
            <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;"><strong>{best_region}</strong> region generated <strong>${best_region_sales:,.0f}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e3a5f, #2a4a6f); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #a78bfa;">
            <h3 style="color: #a78bfa; margin: 0 0 10px 0; font-size: 1rem;">👨‍💼 Top Sales Rep</h3>
            <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;"><strong>{best_rep}</strong> closed <strong>${best_rep_sales:,.0f}</strong> in deals</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e3a5f, #2a4a6f); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #f472b6;">
            <h3 style="color: #f472b6; margin: 0 0 10px 0; font-size: 1rem;">💎 Most Profitable Category</h3>
            <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;"><strong>{most_profitable_category}</strong> earned <strong>${most_profitable_category_profit:,.0f}</strong> profit</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e3a5f, #2a4a6f); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #fbbf24;">
            <h3 style="color: #fbbf24; margin: 0 0 10px 0; font-size: 1rem;">📆 Best Sales Day</h3>
            <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;"><strong>{best_day}</strong> has the highest sales volume</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e3a5f, #2a4a6f); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #34d399;">
            <h3 style="color: #34d399; margin: 0 0 10px 0; font-size: 1rem;">👥 Customer Preference</h3>
            <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;"><strong>{dominant_customer}</strong> customers contribute more to revenue</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e3a5f, #2a4a6f); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #fb923c;">
            <h3 style="color: #fb923c; margin: 0 0 10px 0; font-size: 1rem;">📡 Dominant Channel</h3>
            <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;"><strong>{dominant_channel}</strong> channel drives more sales</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e3a5f, #2a4a6f); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #38bdf8;">
            <h3 style="color: #38bdf8; margin: 0 0 10px 0; font-size: 1rem;">💳 Preferred Payment</h3>
            <p style="color: #e2e8f0; margin: 0; font-size: 0.95rem;"><strong>{best_payment}</strong> is the most used payment method</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Summary insights
    st.markdown('<div class="section-header">📊 Summary Statistics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Profit Margin", f"{avg_profit_margin:.1f}%")
    with col2:
        st.metric("Total Products", f"{filtered_df['Product_ID'].nunique()}")
    with col3:
        st.metric("Total Sales Reps", f"{filtered_df['Sales_Rep'].nunique()}")
    with col4:
        st.metric("Avg Items/Transaction", f"{filtered_df['Quantity_Sold'].mean():.1f}")
    
    # Recommendations
    st.markdown('<div class="section-header">🎯 Recommendations</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #1a1a3e, #252550); border-radius: 12px; padding: 20px; border: 1px solid rgba(99, 102, 241, 0.3);">
        <ul style="color: #e2e8f0; margin: 0; padding-left: 20px; line-height: 2;">
            <li>📈 <strong>Focus on {best_category}</strong> - It's your top revenue generator</li>
            <li>🌍 <strong>Expand in {best_region}</strong> - This region shows the highest potential</li>
            <li>👨‍💼 <strong>Learn from {best_rep}</strong> - Share their strategies with the team</li>
            <li>📆 <strong>Run promotions on {best_day}s</strong> - Customers are most active</li>
            <li>💳 <strong>Optimize {best_payment} checkout</strong> - Most customers prefer this method</li>
            <li>👥 <strong>Invest in {dominant_customer} customer programs</strong> - They drive more revenue</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# ============ TAB 6: DATA EXPLORER ============
with tab6:
    st.markdown('<div class="section-header">📋 Filtered Data Preview</div>', unsafe_allow_html=True)
    
    # Data stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total Rows", f"{len(filtered_df):,}")
    with col2:
        st.metric("📋 Columns", f"{len(filtered_df.columns)}")
    with col3:
        st.metric("📅 Date Range", f"{filtered_df['Sale_Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Sale_Date'].max().strftime('%Y-%m-%d')}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display dataframe
    st.dataframe(
        filtered_df.style.format({
            'Sales_Amount': '${:,.2f}',
            'Unit_Cost': '${:,.2f}',
            'Unit_Price': '${:,.2f}',
            'Profit': '${:,.2f}',
            'Discount': '{:.0%}',
            'Profit_Margin': '{:.1f}%'
        }),
        use_container_width=True,
        height=500
    )
    
    # Download button
    st.markdown("<br>", unsafe_allow_html=True)
    
    @st.cache_data
    def convert_df_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8')
    
    csv_data = convert_df_to_csv(filtered_df)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name=f"filtered_sales_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )


# ============ FOOTER ============
st.markdown("""
    <div style="text-align: center; padding: 30px 0 10px 0; color: #64748b; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 40px;">
        <p>📊 Sales Analytics Dashboard | Built with Streamlit & Plotly</p>
        <p style="font-size: 0.8rem;">🚀 Last Updated: {}</p>
    </div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)
