"""Main analysis script for Product Analytics"""
import pandas as pd
from src.engagement import dau_mau, retention_cohort, feature_adoption, user_segments
from src.funnel import conversion_funnel, event_analysis

def main():
    print("=" * 60)
    print("PRODUCT ANALYTICS & USER RETENTION ANALYSIS")
    print("=" * 60)
    
    # Load data
    df = pd.read_csv('data/user_events.csv')
    
    # DAU/MAU
    print("\n📊 ENGAGEMENT METRICS:")
    dau, mau = dau_mau(df)
    print(f"  DAU (Last Week): {dau.tail(7).mean():.0f}")
    print(f"  MAU (Current): {mau.iloc[-1]:.0f}")
    print(f"  Unique Users: {df['user_id'].nunique()}")
    print(f"  Total Events: {len(df)}")
    
    # Event analysis
    print("\n🎯 EVENT ANALYSIS:")
    print(event_analysis(df))
    
    # Conversion funnel
    print("\n📈 CONVERSION FUNNEL:")
    funnel = conversion_funnel(df)
    print(funnel)
    
    # Feature adoption
    print("\n✨ FEATURE ADOPTION:")
    print(feature_adoption(df))
    
    # User segments
    print("\n👥 USER SEGMENTS:")
    segments = user_segments(df)
    print(segments['segment'].value_counts())
    
    # Retention cohort
    print("\n📅 RETENTION COHORT (%):")
    retention = retention_cohort(df)
    print(retention.head(10))
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
