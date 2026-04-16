"""📱 PRODUCT ANALYTICS - USER RETENTION DASHBOARD"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Product Analytics", layout="wide")

C1, C2, C3, C4 = "#1a1a2e", "#f39c12", "#27ae60", "#e74c3c"

st.markdown(f"""<style>
.header {{background: linear-gradient(135deg, #1a1a2e 0%, #f39c12 100%); padding: 40px; border-radius: 15px; color: white; margin-bottom: 30px;}}
.funnel-stage {{background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%); padding: 20px; border-radius: 10px; color: white; margin: 10px 0; text-align: center;}}
.kpi {{background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); padding: 25px; border-radius: 10px; color: white; text-align: center; margin: 5px;}}
</style>""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('data/product_data.csv')

df = load_data()
st.markdown(f'<div class="header"><h1>🎯 Product Conversion Funnel</h1><p>User Journey & Engagement Pipeline</p></div>', unsafe_allow_html=True)

# Calculate funnel metrics
total_users = df['user_id'].nunique()
dau = len(df[df['days_since_login'] <= 1])
weekly_active = len(df[df['days_since_login'] <= 7])
monthly_active = len(df[df['days_since_login'] <= 30])

# MAIN VISUALIZATION: CONVERSION FUNNEL
st.subheader("🔗 USER ENGAGEMENT FUNNEL")

funnel_data = {
    'Stage': ['Total Users', 'Daily Active Users', 'Weekly Active Users', 'Monthly Active Users'],
    'Users': [total_users, dau, weekly_active, monthly_active],
    'Percentage': [100, (dau/total_users)*100, (weekly_active/total_users)*100, (monthly_active/total_users)*100]
}
funnel_df = pd.DataFrame(funnel_data)

fig = go.Figure(go.Funnel(
    y=funnel_df['Stage'],
    x=funnel_df['Users'],
    marker=dict(color=['#1a1a2e', '#f39c12', '#27ae60', '#3498db']),
    text=[f"{x} users<br>({pct:.1f}%)" for x, pct in zip(funnel_df['Users'], funnel_df['Percentage'])],
    textposition="inside",
    textfont=dict(size=14, color='white'),
    connector=dict(line=dict(color='rgba(0,0,0,0.2)'))
))
fig.update_layout(
    height=500,
    margin=dict(l=100, r=100, t=100, b=100),
    plot_bgcolor='rgba(0,0,0,.02)',
    paper_bgcolor='rgba(240,240,240,1)',
    font=dict(size=12)
)
st.plotly_chart(fig, use_container_width=True)

# FUNNEL STAGE METRICS
st.subheader("📊 FUNNEL STAGE PERFORMANCE")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div class="kpi"><h4>TOTAL USERS</h4><h2>{total_users}</h2><p>Registered Users</p></div>', unsafe_allow_html=True)

with col2:
    dau_pct = (dau/total_users)*100
    st.markdown(f'<div class="kpi"><h4>DAILY ACTIVE</h4><h2>{dau}</h2><p>{dau_pct:.1f}% of Total</p></div>', unsafe_allow_html=True)

with col3:
    wau_pct = (weekly_active/total_users)*100
    st.markdown(f'<div class="kpi"><h4>WEEKLY ACTIVE</h4><h2>{weekly_active}</h2><p>{wau_pct:.1f}% of Total</p></div>', unsafe_allow_html=True)

with col4:
    mau_pct = (monthly_active/total_users)*100
    st.markdown(f'<div class="kpi"><h4>MONTHLY ACTIVE</h4><h2>{monthly_active}</h2><p>{mau_pct:.1f}% of Total</p></div>', unsafe_allow_html=True)

st.divider()

# DROP-OFF ANALYSIS
st.subheader("📉 DROP-OFF RATES BETWEEN STAGES")
col1, col2, col3 = st.columns(3)

with col1:
    total_to_dau_drop = ((total_users - dau) / total_users * 100)
    st.markdown(f'<div class="funnel-stage"><p>Total → Daily</p><h3>{total_to_dau_drop:.1f}%</h3><p>Drop-off Rate</p></div>', unsafe_allow_html=True)

with col2:
    dau_to_wau_drop = ((dau - weekly_active) / dau * 100) if dau > 0 else 0
    st.markdown(f'<div class="funnel-stage"><p>Daily → Weekly</p><h3>{dau_to_wau_drop:.1f}%</h3><p>Drop-off Rate</p></div>', unsafe_allow_html=True)

with col3:
    wau_to_mau_drop = ((weekly_active - monthly_active) / weekly_active * 100) if weekly_active > 0 else 0
    st.markdown(f'<div class="funnel-stage"><p>Weekly → Monthly</p><h3>{wau_to_mau_drop:.1f}%</h3><p>Drop-off Rate</p></div>', unsafe_allow_html=True)

st.divider()

# ENGAGEMENT DISTRIBUTION
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 ENGAGEMENT SEGMENTS")
    df['engagement_level'] = pd.cut(df['days_since_login'], 
                                     bins=[0, 1, 7, 30, 90, 365], 
                                     labels=['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Inactive'])
    engagement = df['engagement_level'].value_counts().sort_index()
    
    fig = px.pie(
        names=engagement.index,
        values=engagement.values,
        color_discrete_sequence=['#27ae60', '#f39c12', '#3498db', '#e74c3c', '#95a5a6'],
        hole=0.3,
        title="User Engagement Segments"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("⭐ TOP FEATURES BY ADOPTION")
    feature_usage = df.groupby('feature_used').size().sort_values(ascending=True).tail(8)
    
    fig = px.barh(
        x=feature_usage.values,
        y=feature_usage.index,
        color=feature_usage.values,
        color_continuous_scale='Viridis',
        labels={'x': 'Usage Count', 'y': 'Feature'},
        title="Feature Usage Ranking"
    )
    fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,.05)')
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# DETAILED TABLE
st.subheader("📋 USER DETAILS & ENGAGEMENT")
display_df = df[['user_id', 'signup_date', 'feature_used', 'session_duration_mins', 'days_since_login', 'engagement_level']].head(100)
st.dataframe(display_df, use_container_width=True, hide_index=True)

csv = display_df.to_csv(index=False)
st.download_button("📥 Download User Analytics", csv, "user_analytics.csv", "text/csv")
