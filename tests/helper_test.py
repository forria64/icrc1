# tests/helper_test.py
import json
import sys
import time
import os

# Optional ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_BOLD = "\033[1m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"
COLOR_RED = "\033[31m"
COLOR_BLINK ="\033[5m"

def process_canister_info(canister_info):
    """
    Processes and displays the canister information passed from helper.py.

    Args:
        canister_info (dict): Dictionary containing information about all canisters
                             and the selected canister.
    """
    all_canisters = canister_info.get("canisters", {})
    selected_canister = canister_info.get("selected_canister", None)

    print(f"\n{COLOR_BOLD}Received Canister Information:{COLOR_RESET}\n")
    print(f"{COLOR_BOLD}{COLOR_YELLOW}All Canisters:{COLOR_RESET}")
    for name, info in all_canisters.items():
        print(f"  {COLOR_GREEN}Name: {name}{COLOR_RESET}")
        for key, value in info.items():
            print(f"    {COLOR_YELLOW}{key}:{COLOR_RESET} {value}")
        print()

    print(f"{COLOR_RED}Selected Canister: {selected_canister}{COLOR_RESET}\n")
    
def main():
    if len(sys.argv) != 2:
        print(f"{COLOR_RED}Usage: python3 helper_test.py '<canister_info_json>'{COLOR_RESET}")
        sys.exit(1)

    canister_info_json = sys.argv[1]
    canister_info = json.loads(canister_info_json)
    process_canister_info(canister_info)

# HOWDY THERE, SPACE COWBOYS !!!
# =====================================
# If you're looking to add your custom test scripts to the /tests directory,
# you can process the arguments passed from helper.py as follows:
# 1. Expect the script to be called with a single JSON string argument.
# 2. Use `json.loads()` to parse the JSON string into a Python dictionary.
# 3. The dictionary will have the following structure:
#    {
#        "canisters": {
#            "<canister_name>": {
#                "type": "<type_of_canister>",    # Type of the canister (e.g., "motoko", "rust", etc.)
#                "main": "<entry_point>",         # Entry point file for the canister.
#                "template_path": "<template_path>",         # Path of the template for the canister's arguments
#            },
#            ...
#        },
#        "selected_canister": "<name_of_selected_canister>"  # The name of the canister selected by the user.
#    }
# 4. You can access all canisters and the selected canister for further processing.
#    For example:
#       - To get the entry point of the selected canister:
#         `canisters["selected_canister"]["main"]`
#       - To list all dependencies of a specific canister:
#         `canisters["<canister_name>"]["dependencies"]`
# 5. Write your custom logic to handle this data as needed.

    print(f"""{COLOR_BLINK}
    ######################################################################################################
    ######################################################################################################
    ######################################################################################################
    ##############              ######  ######    ######          ##        ##              ##############
    ##############  ##########  ##      ####          ##  ##      ######    ##  ##########  ##############
    ##############  ##      ##  ##  ########  ##  ####  ######      ##    ####  ##      ##  ##############
    ##############  ##      ##  ####  ########    ######    ##  ######  ######  ##      ##  ##############
    ##############  ##      ##  ##      ##        ####    ##  ##    ##  ######  ##      ##  ##############
    ##############  ##########  ##  ##  ####  ########  ##        ####  ######  ##########  ##############
    ##############              ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##              ##############
    ##############################  ##  ########    ########    ##  ####    ##############################
    ##############    ##  ####    ########          ####  ##  ####    ##    ##      ##    ################
    ##################  ##  ######    ####  ########  ####    ############        ####      ##############
    ##############  ##  ##      ##  ######  ####  ##  ##      ##    ####  ##    ##          ##############
    ########################  ######    ##  ##        ####    ##          ####  ####  ####  ##############
    ##############    ##    ##  ##      ##  ####      ####    ##      ##    ######  ######  ##############
    ##################      ####  ##  ##    ##    ##            ####  ##        ####    ##  ##############
    ################  ####  ##    ##  ####  ##          ########  ##  ######  ########  ##  ##############
    ##############  ##  ########        ########    ######    ####    ##        ##########################
    ##############      ####    ##    ##  ######  ####  ##      ##    ##  ##        ##      ##############
    ################    ####  ####  ########  ##  ####    ######  ####      ##    ########  ##############
    ################  ####  ##      ####    ####    ####      ####  ##      ######    ##    ##############
    ##############    ######  ####      ####  ##      ####  ##  ##      ####        ####    ##############
    ################    ##      ##      ##          ########          ####    ##    ##  ##################
    ##############            ##  ################  ####  ##  ######  ##        ##    ##    ##############
    ##############  ######  ##    ######    ##  ##########  ##      ####    ####  ######    ##############
    ##############  ##      ####  ############        ##  ######    ##    ######      ##    ##############
    ##############      ####      ##########  ####  ######    ####  ####    ##            ################
    ##################    ##########    ##  ##  ##  ####    ##  ##    ##  ##    ####        ##############
    ##############  ##  ##      ##########  ##      ##    ######  ##  ######  ####      ##  ##############
    ################  ######  ##    ##      ############  ######        ####  ##    ######################
    ##############    ##        ##      ##      ##    ##      ##    ##                    ################
    ##############################            ########  ##        ####      ######    ####  ##############
    ##############              ##          ####    ####        ##  ######  ##  ##    ##    ##############
    ##############  ##########  ######    ##  ##      ####  ##  ##########  ######    ##    ##############
    ##############  ##      ##  ########  ##  ##    ######  ##  ##  ##                ####  ##############
    ##############  ##      ##  ##      ##    ##  ##  ##  ##############  ####  ##  ##    ################
    ##############  ##      ##  ##########  ##    ##  ####  ####      ##    ##    ##  ####  ##############
    ##############  ##########  ##  ##  ##  ##  ####  ##  ######    ##      ##  ####    ##################
    ##############              ##  ##      ##    ####  ####    ##      ##########    ##    ##############
    ######################################################################################################
    ######################################################################################################
    ######################################################################################################{COLOR_RESET}""")
    print(f"{COLOR_BOLD}    ################### IF I MADE YOUR LIFE EASIER, BUY ME A COFFEE, LOVE. WOULD YOU?  ###################{COLOR_RESET}")
    print(f"{COLOR_BOLD}<<< monero:434S3JGKT8Mi5SUAFUfZN6hGDqKQsRM6Ybe5Qk519uu6127RvYDZJPrBg14hXRsxJ6ez3MDYR4FfTS3r7jzuzJQF8rxUMb5 >>>{COLOR_RESET}")
if __name__ == "__main__":
    main()

