"""User engagement and retention analysis"""
import pandas as pd
from datetime import timedelta

def dau_mau(df):
    """Calculate Daily and Monthly Active Users"""
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    df['month'] = pd.to_datetime(df['timestamp']).dt.to_period('M')
    
    dau = df.groupby('date')['user_id'].nunique()
    mau = df.groupby('month')['user_id'].nunique()
    
    return dau, mau

def retention_cohort(df):
    """Analyze retention by cohort"""
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create user cohorts based on first activity date
    user_first_date = df.groupby('user_id')['timestamp'].min().reset_index()
    user_first_date['cohort'] = user_first_date['timestamp'].dt.to_period('W')
    
    df = df.merge(user_first_date[['user_id', 'cohort']], on='user_id')
    df['event_week'] = df['timestamp'].dt.to_period('W')
    df['week_num'] = (df['event_week'] - df['cohort']).apply(lambda x: x.n)
    
    # Retention table
    retention_table = df.groupby(['cohort', 'week_num'])['user_id'].nunique().unstack(fill_value=0)
    retention_pct = retention_table.divide(retention_table.iloc[:, 0], axis=0) * 100
    
    return retention_pct.round(1)

def feature_adoption(df):
    """Analyze feature adoption rates"""
    return df.groupby('feature_name').agg({
        'user_id': 'nunique',
        'timestamp': 'count'
    }).rename(columns={
        'user_id': 'unique_users',
        'timestamp': 'total_events'
    }).round(2)

def user_segments(df):
    """Segment users by activity level"""
    user_activity = df.groupby('user_id').agg({
        'event_type': 'count',
        'timestamp': lambda x: (pd.to_datetime(x).max() - pd.to_datetime(x).min()).days
    }).rename(columns={'event_type': 'events', 'timestamp': 'days_active'})
    
    user_activity['segment'] = pd.cut(user_activity['days_active'], 
                                      bins=[0, 7, 30, 90, 365],
                                      labels=['New', 'Active', 'Engaged', 'VIP'])
    return user_activity
