"""Funnel and conversion analysis"""
import pandas as pd

def conversion_funnel(df, events_order=['signup', 'login', 'feature_use', 'upgrade']):
    """Analyze conversion through funnel"""
    funnel_data = []
    
    for event in events_order:
        event_users = df[df['event_type'] == event]['user_id'].nunique()
        funnel_data.append({
            'stage': event,
            'unique_users': event_users,
            'conversion_rate': 100  # Will be calculated
        })
    
    funnel_df = pd.DataFrame(funnel_data)
    total_users = funnel_df.iloc[0]['unique_users']
    funnel_df['conversion_from_start'] = (funnel_df['unique_users'] / total_users * 100).round(2)
    funnel_df['drop_off'] = funnel_df['unique_users'].diff().fillna(0)
    
    return funnel_df

def event_analysis(df):
    """Analyze event frequency and types"""
    return df.groupby('event_type').agg({
        'user_id': 'nunique',
        'timestamp': 'count'
    }).rename(columns={
        'user_id': 'unique_users',
        'timestamp': 'total_events'
    }).sort_values('total_events', ascending=False)

def user_journey(df, user_id):
    """Get specific user's journey"""
    user_data = df[df['user_id'] == user_id].sort_values('timestamp')
    return user_data[['timestamp', 'event_type', 'feature_name']].head(20)
