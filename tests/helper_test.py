# tests/helper_test.py
import json
import sys

def process_canister_info(canister_info):
    print(f"Received Canister Information:")
    print(f"Name: {canister_info['name']}")
    print(f"Info: {canister_info['info']}")
    print(f"Template Path: {canister_info['template_path']}")
    
    # Add your logic to test or process the canister information here

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 helper_test.py '<canister_info_json>'")
        sys.exit(1)

    canister_info_json = sys.argv[1]
    canister_info = json.loads(canister_info_json)
    process_canister_info(canister_info)

if __name__ == "__main__":
    main()

