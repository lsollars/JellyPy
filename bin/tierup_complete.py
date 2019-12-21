"""
Validate a TierUp analysis CV as complete.

Returns the filename and 'True' if the file is complete, otherwise 'False'.

Usage:
    python tierup_complete.py JSON_FILE
"""

import csv
import argparse

def is_complete(tierup_csv):
    with open(tierup_csv, 'r') as f:
        reader = csv.DictReader(f)
        tier3_count = (next(reader)['tier3_count']) # NOTE: Now 'TIER3'
        f.seek(0)
        expected = (len(f.readlines()) - 1)
    if int(tier3_count) == expected:
        return True
    else:
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tierup_csv')
    args = parser.parse_args()

    print("\t".join([args.tierup_csv, str(is_complete(args.tierup_csv))]))

if __name__ == "__main__":
    main()