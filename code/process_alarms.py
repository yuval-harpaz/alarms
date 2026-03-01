import pandas as pd
import numpy as np
from datetime import datetime

def process_alarms():
    # Read the data
    df = pd.read_csv('/home/yuval/alarms/data/alarms.csv')
    df['time'] = pd.to_datetime(df['time'])
    
    # Filter by threat (missiles and rockets)
    df = df[df['threat'] == 0]
    
    # Define time periods
    start_2025 = pd.to_datetime('2025-06-13 21:10:14')
    end_2025 = pd.to_datetime('2025-06-24 10:34:10')
    start_2026 = pd.to_datetime('2026-02-28 10:10:20')
    
    # Segment 2025 data (Iran only)
    df_2025 = df[(df['time'] >= start_2025) & (df['time'] <= end_2025) & (df['origin'] == 'Iran')].copy()
    
    # Segment 2026 data
    df_2026 = df[df['time'] >= start_2026].copy()
    
    def aggregate_by_hour(df_segment, start_time, year_label):
        if df_segment.empty:
            return pd.DataFrame(columns=['hour', 'year', 'barrages', 'alarms'])
        
        # Calculate relative time in minutes
        df_segment['rel_minutes'] = ((df_segment['time'] - start_time).dt.total_seconds() / 60).astype(int)
        df_segment['hour'] = (df_segment['rel_minutes'] // 60) + 1
        
        # Group by hour to get alarms (count rows) and barrages (count unique minutes)
        # Using unique minutes as specified: "events happening less than a minute apart considered as one event"
        hour_groups = df_segment.groupby('hour')
        
        res = hour_groups.agg(
            alarms=('time', 'count'),
            barrages=('rel_minutes', 'nunique')
        ).reset_index()
        
        res['year'] = year_label
        return res

    res_2025 = aggregate_by_hour(df_2025, start_2025, 2025)
    res_2026 = aggregate_by_hour(df_2026, start_2026, 2026)
    
    # Combine results
    final_df = pd.concat([res_2025, res_2026], ignore_index=True)
    
    # Ensure all hours are represented (filling gaps with 0 if necessary, up to the max hour of each year)
    # Actually, the user just wants the csv with these columns. 
    # Let's ensure columns are in order: hour, year, barrages, alarms
    final_df = final_df[['hour', 'year', 'barrages', 'alarms']]
    
    # Save to CSV
    output_path = '/home/yuval/alarms/data/alarms_comparison.csv'
    final_df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")

if __name__ == "__main__":
    process_alarms()
