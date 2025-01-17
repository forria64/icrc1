# tests/helper_test.py
import json
import sys
import os
import subprocess
from pathlib import Path

# Optional ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_BOLD = "\033[1m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"
COLOR_RED = "\033[31m"
COLOR_BLINK ="\033[5m"

def get_principal():
    """
    Return the principal of the currently in-use dfx identity.
    """
    try:
        return subprocess.check_output(
            "dfx identity get-principal",
            shell=True,
            text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        print(f"{COLOR_BOLD}ERROR: COULDN'T FETCH PRINCIPAL\n{e}{COLOR_RESET}")
        exit(1)

def run_command(command, desc=None):
    """
    Execute a shell command and stream its output to the terminal with an optional description.

    Args:
        command (str): The shell command to execute.
        desc (str): Optional description to display before executing the command.

    Raises:
        subprocess.CalledProcessError: If the command fails with a non-zero exit code.
    """
    if desc:
        print(f"\n{COLOR_BOLD}==== {desc} ===={COLOR_RESET}\n")

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in iter(process.stdout.readline, ""):
            print(line, end="")
        process.stdout.close()
        return_code = process.wait()

        if return_code != 0:
            print(f"{COLOR_BOLD}COMMAND FAILED WITH RETURN CODE {return_code}{COLOR_RESET}")
            raise subprocess.CalledProcessError(return_code, command)

    except subprocess.CalledProcessError as e:
        print(f"{COLOR_BOLD}ERROR: COULDN'T EXECUTE COMMAND\n{e}{COLOR_RESET}")
        exit(1)

def validate_output(test_desc, actual, expected, counters):
    """
    Validate the output of a test and print the result to the terminal.

    Args:
        test_desc (str): Description of the test being validated.
        actual (any): The actual output from the test.
        expected (any): The expected output to compare against.
        counters (dict): Dictionary tracking test statistics (total, success, failed, id).
    """
    counters['total'] += 1
    if actual == expected:
        print(f"\n{COLOR_GREEN}^^^^^^^^^^^^^^^^^^ TEST {counters['id']} SUCCESSFUL ^^^^^^^^^^^^^^^^^^{COLOR_RESET}")
        print(f"{COLOR_GREEN}{test_desc}{COLOR_RESET}")
        print(f"{COLOR_GREEN}========================================================{COLOR_RESET}\n")
        counters['success'] += 1
    else:
        print(f"\n{COLOR_BOLD}^^^^^^^^^^^^^^^^^^ TEST {counters['id']} FAILED ^^^^^^^^^^^^^^^^^^{COLOR_RESET}")
        print(f"{COLOR_BOLD}{test_desc}{COLOR_RESET}")
        print(f"{COLOR_BOLD}Expected: {expected}, Got: {actual}{COLOR_RESET}")
        print(f"{COLOR_BOLD}========================================================{COLOR_RESET}\n")
        counters['failed'] += 1

def write_init_args(template_path, variables):
    """
    Replaces variables in the template, prints the result, and writes it to .tmp_args/<canister_name>.candid.

    Args:
        template_path (str): Path to the template file. Must not be None.
        variables (dict): A dictionary where keys are placeholders to replace (e.g., {key})
                          and values are their replacements.

    Example:
        template_path = "args/example.template"
        variables = {"owner_principal": "abcd-principal-id", "token_name": "MyToken"}
        This will replace {owner_principal} and {token_name} in the template.
    """
    if not template_path or not os.path.exists(template_path):
        print(f"{COLOR_BOLD}ERROR: NO TEMPLATE FILE FOUND{COLOR_RESET}")
        exit(1)

    try:
        with open(template_path, 'r') as template_file:
            content = template_file.read()

        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, value)

        print(f"{COLOR_BOLD}{COLOR_YELLOW}Processed Template Content:\n{content}{COLOR_RESET}")

        canister_name = Path(template_path).stem
        output_dir = Path(".tmp_args")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{canister_name}.candid"

        with open(output_file, 'w') as file:
            file.write(content)

        print(f"{COLOR_BOLD}{COLOR_YELLOW}Initialization arguments saved to: {output_file}{COLOR_RESET}")

    except Exception as e:
        print(f"{COLOR_BOLD}ERROR: FAILED TO PROCESS TEMPLATE\n{e}{COLOR_RESET}")
        exit(1)

def deploy_canister(canister_id, argument_file=None):
    """
    Creates, builds, and installs a single canister with an optional init argument.
    """
    run_command(f"dfx canister create {canister_id}", desc=f"Create canister {canister_id}")
    run_command(f"dfx build {canister_id}", desc=f"Build canister {canister_id}")

    if argument_file:
        cmd = f'dfx canister install {canister_id} --argument "$(cat {argument_file})"'
    else:
        cmd = f'dfx canister install {canister_id}'

    run_command(cmd, desc=f"Install canister {canister_id}")
    print(f"{COLOR_RESET}Installed canister '{canister_id}' successfully.{COLOR_RESET}")

def main():
    if len(sys.argv) != 2:
        print(f"{COLOR_RED}Usage: python3 helper_test.py '<canister_info_json>'{COLOR_RESET}")
        sys.exit(1)

    # Parse input JSON and extract canister data
    canister_info_json = sys.argv[1]
    canister_info = json.loads(canister_info_json)
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

    if selected_canister:
        #CUSTOM TEST LOGIC
        
        print(f"\n{COLOR_BOLD}{COLOR_BLINK}<<< SETTING UP TESTING ENVIRONMENT >>>{COLOR_RESET}\n")
        
        #PHASE 1 GETTING INFO AND CONFIGURING NECESSARY IDENTITIES
        owner_principal = get_principal()
        selected_canister_info = all_canisters.get(selected_canister, {})
        #PHASE 2 WRITING INITIALIZATION ARGUMENTS FROM TEMPLATE
        template_path = selected_canister_info.get("template_path")
        if not template_path or not os.path.exists(template_path):
            print(f"{COLOR_BOLD}ERROR: NO TEMPLATE FILE FOUND{COLOR_RESET}")
            sys.exit(1)
        variables = {"owner_principal": owner_principal}
        write_init_args(template_path, variables)
        
        print(f"\n{COLOR_BOLD}{COLOR_BLINK}<<< TESTING ENVIRONMENT SET UP >>>{COLOR_RESET}\n")
        
        
        print(f"\n{COLOR_BOLD}{COLOR_BLINK}<<< TESTING STARTED >>>{COLOR_RESET}\n")
        # Demonstrate run_command and validate_output
        counters = {"total": 0, "success": 0, "failed": 0, "id": 1}
        test_command = "ls"
        run_command(test_command, desc="Get info from dfx")
        validate_output(
            test_desc="Validate dfx info output", 
            actual="Success", 
            expected="Success", 
            counters=counters
        )
        # Summary of results
        print(f"\n{COLOR_BOLD}{COLOR_BLINK}<<< TESTING COMPLETED >>>{COLOR_RESET}\n")
        print(f"{COLOR_GREEN}Tests Passed: {counters['success']}{COLOR_RESET}")
        print(f"{COLOR_RED}Tests Failed: {counters['failed']}{COLOR_RESET}")
        print(f"{COLOR_BOLD}{COLOR_YELLOW}Total Tests: {counters['total']}{COLOR_RESET}")


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
#            },
#            ...
#        },
#        "selected_canister": "<name_of_selected_canister>"  # The name of the canister selected by the user.
#    }
# 4. You can access all canisters and the selected canister for further processing.
#    For example:
#       - To get the entry point of the selected canister:
#         `canisters["selected_canister"]["main"]`
#       - To process the selected canister's template:
#         Use `write_init_args` as demonstrated above.
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

