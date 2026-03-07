import pandas as pd
import numpy as np

def main():
    # File paths
    input_file = 'https://raw.githubusercontent.com/yuval-harpaz/alarms/refs/heads/master/data/alarms.csv'
    output_file = '/home/yuval/Documents/daily_roar.csv'
    # Data loading
    df = pd.read_csv(input_file)
    # Filtering by date (2026-02-28 or later)
    df = df[df['time'] >= '2026-02-28'].copy()
    unique_locations = df['cities'].unique()
    city_fragments = [
        "תל אביב", "ירושלים", "חיפה", "באר שבע", "אשדוד", "פתח תקווה", "מודיעין", "עכו", 
        "כפר סבא", "פרדס חנה", "דימונה", "מטולה", "קריית שמונה", "ראשון לציון", 
        "אשקלון", "נתניה", "בני ברק", "רחובות", "הרצליה", "בית שמש", "נצרת", 
        "אום אל פחם", "לוד"
    ]
    city_fragments.sort()
    chosen_locations = []
    for requested_location in city_fragments:
        found = False
        for loc in unique_locations:
            if requested_location in loc:
                chosen_locations.append(loc)
                found = True
        if not found:
            print(f"Location {requested_location} not found in any of the requested locations.")
    # chosen_locations.sort()
    # Extract date part for grouping
    # keep only threats 0 and 5
    df = df[df['threat'].isin([0, 5])]
    # kkep only chosen locations
    df = df[df['cities'].isin(chosen_locations)]
    df['date'] = df['time'].str[:10]
    dates = sorted(df['date'].unique())
    # Handle NaNs and ensure string type for grouping/sorting
    df['origin'] = df['origin'].fillna('Unlabeled').astype(str)
    origins = np.unique(df['origin'])
    df_daily = pd.DataFrame(columns=['location', 'date', 'threat']+origins.tolist())
    row = 0
    for location in chosen_locations:
        for date in dates:
            for ithreat, threat in enumerate([0, 5]):
                row += 1
                df_daily.at[row, 'location'] = location
                df_daily.at[row, 'date'] = date
                df_daily.at[row, 'threat'] = ['רקטות \ טילים', 'כלי טיס עויין'][ithreat]
                for origin in origins:
                    sum_alarms = df[(df['cities'] == location) & (df['date'] == date) & (df['threat'] == threat) & (df['origin'] == origin)].shape[0]
                    df_daily.at[row, origin] = sum_alarms
    df_daily.to_csv(output_file, index=False)
    print(f"Summary saved to {output_file}")
    
if __name__ == "__main__":
    main()
