"""
Unit tests to verify consistency between telegram_messages.csv and dleshem_roar.csv

Tests:
1. All non-zero rid numbers in telegram['rid'] refer to locations in dleshem that are indeed 
   in the same telegram row
2. dleshem['telegram_id'] refer to a telegram['locations'] that contain that location
3. Locations in dleshem['data'] that have the same telegram_id are unique (no duplicates)
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys


# Global configuration for limiting rows (can be set via command line)
MAX_ROWS_TELEGRAM = None  # None = no limit
MAX_ROWS_DLESHEM = None   # None = no limit

# Module-level data variables
data_dir = Path.home() / 'alarms' / 'data'

# Load CSV files
telegram = pd.read_csv(data_dir / 'telegram_messages.csv')
dleshem = pd.read_csv(data_dir / 'dleshem_roar.csv')

# Apply row limits if specified
if MAX_ROWS_TELEGRAM is not None:
    telegram = telegram.iloc[:MAX_ROWS_TELEGRAM]
if MAX_ROWS_DLESHEM is not None:
    dleshem = dleshem.iloc[:MAX_ROWS_DLESHEM]

# Handle potential NaN values
telegram['rid'] = telegram['rid'].fillna(0).astype(str)
dleshem['telegram_id'] = dleshem['telegram_id'].fillna(0).astype(int)
dleshem['rid'] = dleshem['rid'].fillna(0).astype(str)

# Create lookup dictionaries for faster access
rid_to_telegram_row = {}
for idx in range(len(telegram)):
    row = telegram.iloc[idx]
    rid_str = str(row['rid']).strip()
    if rid_str and rid_str != '0':
        # Handle multiple rids separated by semicolon
        rids = [r.strip() for r in rid_str.split(';')]
        for rid in rids:
            if rid not in rid_to_telegram_row:
                rid_to_telegram_row[rid] = []
            rid_to_telegram_row[rid].append((idx, row))

telegram_id_lookup = telegram.set_index('message id')


class TestAlarmDataConsistency(unittest.TestCase):
    """Test suite for alarm data consistency"""
    
    def test_1_telegram_rid_references_valid_dleshem_locations(self):
        """
        Test 1: All non-zero rid numbers in telegram['rid'] refer to locations in dleshem 
        that are indeed in the same telegram row
        
        For each telegram row with a non-zero rid:
        - Find the corresponding entries in dleshem with that rid
        - Verify that the location in dleshem is contained in telegram['locations']
        """
        failures = []
        total_rows = len(telegram)
        for ii in range(total_rows):
            row = telegram.iloc[ii]
            print(f"\rTest 1 Progress: {ii}/{total_rows}", end='', flush=True)
            rid_str = str(row['rid']).strip()
            if not rid_str or rid_str == '0':
                continue
            # Handle multiple rids separated by semicolon
            rids = [r.strip() for r in rid_str.split(';')]
            telegram_locations = str(row['locations']).split('; ')
            message_id = row['message id']
            
            for rid in rids:
                # Find corresponding entries in dleshem
                dleshem_entries = dleshem[dleshem['rid'].astype(str) == rid]
                
                if len(dleshem_entries) == 0:
                    failures.append(
                        f"{ii} Message ID {message_id}: rid {rid} not found in dleshem"
                    )
                    continue
                
                # Verify that at least one location from dleshem is in telegram
                for jj in range(len(dleshem_entries)):
                    if not dleshem_entries['data'].values[jj] in telegram_locations:
                        dleshem_locations = dleshem_entries['data'].values[jj].strip().split(',')
                        for dloc in dleshem_locations:
                            if dloc.strip() not in telegram_locations:
                                failures.append(
                                    f"{ii} Message ID {message_id}: rid {rid} with location '{dloc}' not found in telegram locations"
                                )
                    

        
        print(f"\rTest 1 Progress: {total_rows}/{total_rows} - Complete!")
        if failures:
            self.fail(
                f"Test 1 failed with {len(failures)} issues:\n" +
                "\n".join(failures[:10]) +
                (f"\n... and {len(failures) - 10} more" if len(failures) > 10 else "")
            )
    
    def test_2_dleshem_telegram_id_references_valid_locations(self):
        """
        Test 2: dleshem['telegram_id'] refer to a telegram['locations'] that contain 
        that location
        
        For each dleshem row with a non-zero telegram_id:
        - Find the corresponding row in telegram
        - Verify that the location in dleshem is contained in telegram['locations']
        """
        failures = []
        total_rows = len(dleshem)
        
        for ii in range(total_rows):
            dleshem_row = dleshem.iloc[ii]
            print(f"\rTest 2 Progress: {ii}/{total_rows}", end='', flush=True)
            
            telegram_id = dleshem_row['telegram_id']
            
            # Skip rows with no telegram_id
            if telegram_id == 0 or pd.isna(telegram_id):
                continue
            
            dleshem_location = str(dleshem_row['data']).strip()
            
            # Find corresponding telegram row
            try:
                telegram_row = telegram_id_lookup.loc[telegram_id]
                telegram_locations = str(telegram_row['locations']).split('; ')
                
                # Verify that dleshem location is in telegram locations
                location_found = any(
                    dleshem_location in telegram_loc 
                    or telegram_loc in dleshem_location
                    for telegram_loc in telegram_locations
                )
                
                if not location_found:
                    failures.append(
                        f"Dleshem row {ii}: telegram_id {telegram_id} with location "
                        f"'{dleshem_location}' not found in telegram locations "
                        f"{telegram_locations}"
                    )
            
            except KeyError:
                failures.append(
                    f"Dleshem row {ii}: telegram_id {telegram_id} not found in telegram"
                )
        
        print(f"\rTest 2 Progress: {total_rows}/{total_rows} - Complete!")
        if failures:
            self.fail(
                f"Test 2 failed with {len(failures)} issues:\n" +
                "\n".join(failures[:10]) +
                (f"\n... and {len(failures) - 10} more" if len(failures) > 10 else "")
            )
    
    def test_3_unique_locations_per_telegram_id(self):
        """
        Test 3: Locations in dleshem['data'] that have the same telegram_id are unique
        
        For each unique telegram_id in dleshem:
        - Verify that all locations with that telegram_id are unique (no duplicates)
        """
        failures = []
        
        # Group dleshem by telegram_id
        grouped = list(dleshem.groupby('telegram_id'))
        total_groups = len(grouped)
        
        for ii, (telegram_id, group) in enumerate(grouped):
            print(f"\rTest 3 Progress: {ii}/{total_groups}", end='', flush=True)
            
            if telegram_id == 0 or pd.isna(telegram_id):
                continue
            
            locations = group['data'].astype(str).values
            unique_locations = set(loc.strip() for loc in locations)
            
            if len(locations) != len(unique_locations):
                # Found duplicates
                location_counts = pd.Series(locations).value_counts()
                duplicates = location_counts[location_counts > 1]
                
                failures.append(
                    f"Telegram_id {telegram_id}: Found {len(locations) - len(unique_locations)} "
                    f"duplicate locations:\n" +
                    "\n".join(
                        f"  '{loc}': appears {count} times" 
                        for loc, count in duplicates.items()
                    )
                )
        
        print(f"\rTest 3 Progress: {total_groups}/{total_groups} - Complete!")
        if failures:
            self.fail(
                f"Test 3 failed with {len(failures)} issues:\n" +
                "\n".join(failures)
            )
    
    def test_summary(self):
        """Print summary statistics about the data"""
        print("\n" + "="*60)
        print("ALARM DATA SUMMARY")
        print("="*60)
        
        # Telegram statistics
        print(f"\nTelegram Messages:")
        print(f"  Total rows: {len(telegram)}")
        print(f"  Rows with non-zero rid: {len(telegram[telegram['rid'] != '0'])}")
        print(f"  Rows with zero rid: {len(telegram[telegram['rid'] == '0'])}")
        
        # Dleshem statistics
        print(f"\nDleshem Data:")
        print(f"  Total rows: {len(dleshem)}")
        non_zero_telegram_id = dleshem[dleshem['telegram_id'] != 0]
        print(f"  Rows with non-zero telegram_id: {len(non_zero_telegram_id)}")
        print(f"  Rows with zero telegram_id: {len(dleshem[dleshem['telegram_id'] == 0])}")
        
        # Unique values
        print(f"\nUnique Values:")
        print(f"  Unique telegram_id in dleshem: {dleshem['telegram_id'].nunique()}")
        print(f"  Unique rid in telegram: {len(set(str(r).strip() for r in telegram['rid'].values if str(r).strip() != '0'))}")
        print(f"  Unique rid in dleshem: {len(set(str(r).strip() for r in dleshem['rid'].values if str(r).strip() != '0'))}")
        
        # Cross-reference
        telegram_ids_in_dleshem = set(dleshem[dleshem['telegram_id'] != 0]['telegram_id'].unique())
        message_ids_in_telegram = set(telegram['message id'].unique())
        valid_references = telegram_ids_in_dleshem & message_ids_in_telegram
        
        print(f"\nCross-reference:")
        print(f"  Valid telegram_id references: {len(valid_references)}")
        print(f"  Invalid telegram_id references: {len(telegram_ids_in_dleshem - message_ids_in_telegram)}")
        
        print("="*60 + "\n")


class TestAlarmDataIssues(unittest.TestCase):
    """Additional tests to identify specific issues"""
    
    def test_find_orphaned_rid_in_telegram(self):
        """Find telegram rows with rid that don't exist in dleshem"""
        orphaned = []
        
        for ii in range(len(telegram)):
            row = telegram.iloc[ii]
            rid_str = str(row['rid']).strip()
            if not rid_str or rid_str == '0':
                continue
            
            rids = [r.strip() for r in rid_str.split(';')]
            for rid in rids:
                if rid and rid != '0':
                    if len(dleshem[dleshem['rid'].astype(str) == rid]) == 0:
                        orphaned.append({
                            'message_id': row['message id'],
                            'rid': rid,
                            'location': row['locations']
                        })
        
        if orphaned:
            print(f"\nFound {len(orphaned)} orphaned rids in telegram:")
            for item in orphaned[:5]:
                print(f"  Message {item['message_id']}: rid {item['rid']} - {item['location']}")
            if len(orphaned) > 5:
                print(f"  ... and {len(orphaned) - 5} more")
    
    def test_find_invalid_telegram_id_references(self):
        """Find dleshem rows referencing non-existent telegram messages"""
        invalid = []
        
        telegram_ids = set(telegram['message id'].unique())
        
        for ii in range(len(dleshem)):
            row = dleshem.iloc[ii]
            telegram_id = row['telegram_id']
            if telegram_id != 0 and pd.notna(telegram_id) and int(telegram_id) not in telegram_ids:
                invalid.append({
                    'ii': ii,
                    'telegram_id': telegram_id,
                    'location': row['data']
                })
        
        if invalid:
            print(f"\nFound {len(invalid)} invalid telegram_id references in dleshem:")
            for item in invalid[:5]:
                print(f"  Row {item['ii']}: telegram_id {item['telegram_id']} - {item['location']}")
            if len(invalid) > 5:
                print(f"  ... and {len(invalid) - 5} more")


def set_max_rows(num_rows):
    """Set the global row limits"""
    global MAX_ROWS_TELEGRAM, MAX_ROWS_DLESHEM
    MAX_ROWS_TELEGRAM = num_rows
    MAX_ROWS_DLESHEM = num_rows


def run_tests_with_details():
    """Run all tests with detailed output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all tests
    suite.addTests(loader.loadTestsFromTestCase(TestAlarmDataConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestAlarmDataIssues))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    # Parse command-line arguments
    max_rows = None
    
    # Look for --rows argument
    for i, arg in enumerate(sys.argv):
        if arg == '--rows' and i + 1 < len(sys.argv):
            try:
                max_rows = int(sys.argv[i + 1])
                # Remove these arguments from sys.argv so unittest doesn't complain
                sys.argv.pop(i + 1)
                sys.argv.pop(i)
                break
            except ValueError:
                print(f"Error: --rows argument must be an integer, got '{sys.argv[i + 1]}'")
                sys.exit(1)
    
    # Set row limits
    if max_rows is not None:
        set_max_rows(max_rows)
        print(f"Running tests with row limit: {max_rows}\n")
    
    run_tests_with_details()

