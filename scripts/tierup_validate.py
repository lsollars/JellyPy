"""
Validate an interpretation request json file for use with TierUp.

Returns the IRID and 'True' if the file meets criteria for TierUp analysis,
    otherwise 'False' with specific validation error.
Interpretation requests must be the v6 model, sent to GMCS for interpretation and not reported.

Usage:
    python tierup_validate.py JSON_FILE
"""
import json
import argparse
from jellypy.tierup.irtools import IRJValidator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('irjson_file')
    args = parser.parse_args()

    with open(args.irjson_file) as f:
        irjson = json.load(f)

    try:
        IRJValidator().validate(irjson)
        is_valid = str(True)
        error_message = str(None)
    except IOError as e:
        is_valid = str(False)
        error_message = str(e)

    print("\t".join([args.irjson_file, is_valid, error_message]))

if __name__ == '__main__':
    main()