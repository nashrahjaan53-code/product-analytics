import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.engagement import dau_mau, feature_adoption, user_segments
from src.funnel import conversion_funnel, event_analysis

st.set_page_config(page_title="Product Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .header {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 20px;
        border-radius: 10px;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
df = pd.read_csv('data/user_events.csv')

if df is not None and len(df) > 0:
    st.markdown('<div class="header"><h1>📈 Product Analytics & User Retention Dashboard</h1></div>', 
                unsafe_allow_html=True)
    
    # Calculate metrics
    unique_users = df['user_id'].nunique()
    total_events = len(df)
    dau, mau = dau_mau(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Unique Users", unique_users)
    with col2:
        st.metric("Total Events", total_events)
    with col3:
        st.metric("DAU (Last 7 Days)", int(dau.tail(7).mean()))
    with col4:
        st.metric("Events/User", round(total_events / unique_users, 2))
    
    st.divider()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Engagement", "🎯 Funnel", "✨ Features", "👥 Segments", "📉 Retention"])
    
    # TAB 1: ENGAGEMENT
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("DAU Trend (Line Chart)")
            dau_df = pd.DataFrame({'Date': dau.index, 'DAU': dau.values})
            fig_dau = px.line(dau_df, x='Date', y='DAU', markers=True,
                            title="Daily Active Users Over Time",
                            color_discrete_sequence=['#a8edea'])
            fig_dau.update_traces(line=dict(width=3))
            st.plotly_chart(fig_dau, use_container_width=True)
        
        with col2:
            st.subheader("MAU Trend (Area Chart)")
            mau_list = [mau.iloc[i] if i < len(mau) else mau.iloc[-1] for i in range(len(dau))]
            mau_df = pd.DataFrame({'Date': dau.index, 'MAU': mau_list[:len(dau)]})
            fig_mau = px.area(mau_df, x='Date', y='MAU',
                            title="Monthly Active Users Trend",
                            fill='tozeroy',
                            color_discrete_sequence=['#fed6e3'])
            st.plotly_chart(fig_mau, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Event Type Distribution (Pie)")
            event_dist = df['event_type'].value_counts()
            fig_event_pie = px.pie(values=event_dist.values, names=event_dist.index,
                                  title="Event Distribution",
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_event_pie, use_container_width=True)
        
        with col2:
            st.subheader("Events per User (Histogram)")
            user_events = df.groupby('user_id').size()
            fig_events_hist = px.histogram(user_events, nbins=10,
                                          title="Event Count Distribution",
                                          labels={'value': 'Events per User'},
                                          color_discrete_sequence=['#a8edea'])
            st.plotly_chart(fig_events_hist, use_container_width=True)
    
    # TAB 2: FUNNEL
    with tab2:
        st.subheader("User Conversion Funnel")
        
        funnel_data = conversion_funnel(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Funnel Visualization")
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_data['stage'],
                x=funnel_data['unique_users'],
                marker=dict(color=['#a8edea', '#fed6e3', '#78e7d1', '#ffa6c1']),
                textposition='auto',
                textinfo='value+percent initial'
            ))
            fig_funnel.update_layout(title="Conversion Funnel")
            st.plotly_chart(fig_funnel, use_container_width=True)
        
        with col2:
            st.subheader("Conversion Rate by Stage")
            fig_conv = px.bar(funnel_data, x='stage', y='conversion_from_start',
                            title="Cumulative Conversion Rate",
                            labels={'conversion_from_start': 'Conversion %', 'stage': 'Stage'},
                            color='conversion_from_start',
                            color_continuous_scale='Viridis')
            st.plotly_chart(fig_conv, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("User Drop-off Analysis")
            fig_dropoff = px.bar(funnel_data, x='stage', y='drop_off',
                               title="User Drop-off by Stage",
                               labels={'drop_off': 'Users Lost', 'stage': 'Stage'},
                               color='drop_off',
                               color_continuous_scale='Reds')
            st.plotly_chart(fig_dropoff, use_container_width=True)
        
        with col2:
            st.subheader("Funnel Details Table")
            st.dataframe(funnel_data, use_container_width=True, hide_index=True)
    
    # TAB 3: FEATURES
    with tab3:
        st.subheader("Feature Adoption Analysis")
        
        feature_adopt = feature_adoption(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Feature Usage by Users (Horizontal Bar)")
            feature_adopt_sorted = feature_adopt.sort_values('unique_users', ascending=True)
            fig_feat_users = px.barh(x=feature_adopt_sorted['unique_users'],
                                    y=feature_adopt_sorted.index,
                                    title="Feature Adoption - User Count",
                                    labels={'x': 'Unique Users'},
                                    color=feature_adopt_sorted['unique_users'],
                                    color_continuous_scale='Teal')
            st.plotly_chart(fig_feat_users, use_container_width=True)
        
        with col2:
            st.subheader("Feature Engagement (Total Events)")
            feature_events = feature_adopt.sort_values('total_events', ascending=True)
            fig_feat_events = px.barh(x=feature_events['total_events'],
                                     y=feature_events.index,
                                     title="Feature Engagement - Total Events",
                                     labels={'x': 'Total Events'},
                                     color=feature_events['total_events'],
                                     color_continuous_scale='Blues')
            st.plotly_chart(fig_feat_events, use_container_width=True)
        
        st.subheader("Feature Adoption Table")
        st.dataframe(feature_adopt.round(1), use_container_width=True)
        
        # Download
        csv = feature_adopt.reset_index().to_csv(index=False)
        st.download_button(
            label="📥 Download Feature Data",
            data=csv,
            file_name="feature_adoption.csv",
            mime="text/csv"
        )
    
    # TAB 4: SEGMENTS
    with tab4:
        st.subheader("User Segmentation Analysis")
        
        segments = user_segments(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("User Segment Distribution (Pie)")
            segment_counts = segments['segment'].value_counts()
            fig_seg_pie = px.pie(values=segment_counts.values, names=segment_counts.index,
                               title="Users by Segment",
                               color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_seg_pie, use_container_width=True)
        
        with col2:
            st.subheader("Segment Characteristics (Box)")
            segment_events = segments.groupby('segment')['events'].mean().sort_values()
            fig_seg_events = px.bar(x=segment_events.index, y=segment_events.values,
                                   title="Average Events per Segment",
                                   labels={'y': 'Avg Events'},
                                   color=segment_events.values,
                                   color_continuous_scale='Spectral')
            st.plotly_chart(fig_seg_events, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Days Active by Segment (Box Plot)")
            fig_days = px.box(segments.reset_index(), x='segment', y='days_active',
                            color='segment', title="Days Active Distribution by Segment")
            st.plotly_chart(fig_days, use_container_width=True)
        
        with col2:
            st.subheader("Segment Summary Statistics")
            segment_stats = segments.groupby('segment')[['events', 'days_active']].agg(['mean', 'count'])
            st.dataframe(segment_stats.round(1), use_container_width=True)
    
    # TAB 5: RETENTION
    with tab5:
        st.subheader("📊 Retention & Cohort Analysis")
        
        # Event analysis
        event_data = event_analysis(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Event Type Analytics (Bar)")
            event_sorted = event_data.sort_values('unique_users', ascending=False)
            fig_events_bar = px.bar(x=event_sorted.index, y=event_sorted['unique_users'],
                                   title="User Count by Event Type",
                                   labels={'y': 'Unique Users'},
                                   color='unique_users',
                                   color_continuous_scale='Plasma')
            st.plotly_chart(fig_events_bar, use_container_width=True)
        
        with col2:
            st.subheader("Event Frequency Ranking")
            event_freq = event_data.sort_values('total_events', ascending=True)
            fig_event_freq = px.barh(x=event_freq['total_events'],
                                    y=event_freq.index,
                                    title="Total Event Count by Type",
                                    color=event_freq['total_events'],
                                    color_continuous_scale='Greens')
            st.plotly_chart(fig_event_freq, use_container_width=True)
        
        st.subheader("Event Analytics Table")
        st.dataframe(event_data.round(1), use_container_width=True)
        
        # KPI Summary
        st.subheader("Key Retention Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            signup_users = df[df['event_type'] == 'signup']['user_id'].nunique()
            st.metric("Signup Users", signup_users)
        
        with col2:
            login_users = df[df['event_type'] == 'login']['user_id'].nunique()
            st.metric("Returning Users", login_users)
        
        with col3:
            if signup_users > 0:
                retention = (login_users / signup_users * 100)
                st.metric("Day-1 Retention %", f"{retention:.1f}%")
else:
    st.error("Unable to load data.")
