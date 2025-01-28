# Path: testing/tests/helper_test.py

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
COLOR_BLINK = "\033[5m"

# Because this file lives inside 'testing/tests/',
# we use '.parent.parent' to go up two levels to the project root if needed
# or specifically to the 'testing' folder if that's what we want:
BASE_DIR = Path(__file__).parent.parent

def get_principal():
    """
    Returns the principal of the currently in-use dfx identity.
    """
    try:
        return subprocess.check_output(
            "dfx identity get-principal",
            shell=True,
            text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        print(f"{COLOR_BOLD}ERROR: COULD NOT FETCH PRINCIPAL\n{e}{COLOR_RESET}")
        exit(1)

def run_command(command, desc=None):
    """
    Executes a shell command, streaming the output to the console.

    Args:
        command (str): The shell command to execute.
        desc (str, optional): Displayed before running the command.

    Returns:
        bool: True if the command exit code is 0; otherwise False.
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
            return False
        return True
    except Exception as e:
        print(f"{COLOR_BOLD}UNEXPECTED ERROR OCCURRED: {e}{COLOR_RESET}")
        return False

def validate_output(test_desc, actual, expected, counters):
    """
    Validates test results and prints them. Updates a counters dict.

    Args:
        test_desc (str): Description of what is being tested.
        actual (any): The actual result of the test.
        expected (any): The expected result.
        counters (dict): Contains 'total', 'success', 'failed', 'id' keys.
    """
    counters['total'] += 1
    test_id = counters['id']

    if actual == expected:
        print(f"\n{COLOR_GREEN}^^^^^^^^^^^^^^^^^^ TEST {test_id} SUCCESSFUL ^^^^^^^^^^^^^^^^^^{COLOR_RESET}")
        print(f"{COLOR_GREEN}{test_desc}{COLOR_RESET}")
        print(f"{COLOR_GREEN}========================================================{COLOR_RESET}\n")
        counters['success'] += 1
    else:
        print(f"\n{COLOR_BOLD}^^^^^^^^^^^^^^^^^^ TEST {test_id} FAILED ^^^^^^^^^^^^^^^^^^{COLOR_RESET}")
        print(f"{COLOR_BOLD}{test_desc}{COLOR_RESET}")
        print(f"{COLOR_BOLD}Expected: {expected}, Got: {actual}{COLOR_RESET}")
        print(f"{COLOR_BOLD}========================================================{COLOR_RESET}\n")
        counters['failed'] += 1

    counters['id'] += 1

def write_init_args(template_path, variables):
    """
    Replaces placeholders in the template file and saves the resulting .candid file
    to 'args/<canister_name>.candid'.

    Args:
        template_path (str): Path to the template file (should be in args_templates).
        variables (dict): A mapping of placeholder -> replacement value.
    """
    if not template_path or not os.path.exists(template_path):
        print(f"{COLOR_BOLD}ERROR: NO TEMPLATE FILE FOUND AT {template_path}{COLOR_RESET}")
        exit(1)

    try:
        with open(template_path, 'r') as template_file:
            content = template_file.read()

        # Replace placeholders
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, value)

        print(f"{COLOR_BOLD}{COLOR_YELLOW}Processed Template Content:\n{content}{COLOR_RESET}")

        canister_name = Path(template_path).stem
        args_dir = BASE_DIR / 'args'  # old '.tmp_args'
        args_dir.mkdir(exist_ok=True)

        output_file = args_dir / f"{canister_name}.candid"
        with open(output_file, 'w') as file:
            file.write(content)

        print(f"{COLOR_BOLD}{COLOR_YELLOW}Initialization arguments saved to: {output_file}{COLOR_RESET}")

    except Exception as e:
        print(f"{COLOR_BOLD}ERROR: FAILED TO PROCESS TEMPLATE\n{e}{COLOR_RESET}")
        exit(1)

def deploy_canister(canister_id, argument_file=None):
    """
    Creates, builds, and installs the canister. Cleans up if anything fails.

    Args:
        canister_id (str): The name of the canister (matches dfx.json 'canisters' key).
        argument_file (str, optional): Path to the .candid file for init args.

    Returns:
        bool: True if deployment succeeded fully, otherwise False.
    """
    def cleanup():
        print(f"{COLOR_YELLOW}Cleaning up canister '{canister_id}'...{COLOR_RESET}")
        run_command(f"dfx canister stop {canister_id}", desc=f"Stop canister {canister_id}")
        run_command(f"dfx canister delete {canister_id}", desc=f"Delete canister {canister_id}")

    # 1. Create
    if not run_command(f"dfx canister create {canister_id}", desc=f"Create canister {canister_id}"):
        cleanup()
        return False

    # 2. Build
    if not run_command(f"dfx build {canister_id}", desc=f"Build canister {canister_id}"):
        cleanup()
        return False

    # 3. Install
    if argument_file:
        install_cmd = f'dfx canister install {canister_id} --argument "$(cat {argument_file})"'
    else:
        install_cmd = f"dfx canister install {canister_id}"

    if not run_command(install_cmd, desc=f"Install canister {canister_id}"):
        cleanup()
        return False

    print(f"{COLOR_GREEN}Canister '{canister_id}' deployed successfully!{COLOR_RESET}")
    return True

def main():
    """
    Main test script entry point. Expects a single JSON argument
    with structure:
       {
         "canisters": {...},
         "selected_canister": "...name..."
       }
    """
    if len(sys.argv) != 2:
        print(f"{COLOR_RED}Usage: python3 helper_test.py '<canister_info_json>'{COLOR_RESET}")
        sys.exit(1)

    # Parse input JSON
    canister_info_json = sys.argv[1]
    canister_info = json.loads(canister_info_json)

    all_canisters = canister_info.get("canisters", {})
    selected_canister = canister_info.get("selected_canister")

    # Show canister info
    print(f"\n{COLOR_BOLD}Received Canister Information:{COLOR_RESET}\n")
    print(f"{COLOR_BOLD}{COLOR_YELLOW}All Canisters:{COLOR_RESET}")
    for name, info in all_canisters.items():
        print(f"  {COLOR_GREEN}Name: {name}{COLOR_RESET}")
        for key, value in info.items():
            print(f"    {COLOR_YELLOW}{key}:{COLOR_RESET} {value}")
        print()

    print(f"{COLOR_RED}Selected Canister: {selected_canister}{COLOR_RESET}\n")

    if selected_canister:
        # PHASE 1: Retrieve environment info
        owner_principal = get_principal()

        # PHASE 2: Write init args from template
        selected_info = all_canisters.get(selected_canister, {})
        template_path = selected_info.get("template_path")

        if not template_path or not os.path.exists(template_path):
            print(f"{COLOR_BOLD}ERROR: NO TEMPLATE FILE FOUND FOR {selected_canister}{COLOR_RESET}")
            sys.exit(1)

        variables = {"owner_principal": owner_principal}
        write_init_args(template_path, variables)

        # PHASE 3: Deployment test
        counters = {"total": 0, "success": 0, "failed": 0, "id": 1}
        arg_file = BASE_DIR / 'args' / f"{Path(template_path).stem}.candid"

        deploy_success = deploy_canister(selected_canister, argument_file=str(arg_file))

        validate_output(
            test_desc="Deploy the selected canister",
            actual="Success" if deploy_success else "Failed",
            expected="Success",
            counters=counters
        )

        # Final summary
        print(f"\n{COLOR_BOLD}{COLOR_BLINK}<<< TESTING COMPLETED >>>{COLOR_RESET}\n")
        print(f"{COLOR_GREEN}Tests Passed: {counters['success']}{COLOR_RESET}")
        print(f"{COLOR_RED}Tests Failed: {counters['failed']}{COLOR_RESET}")
        print(f"{COLOR_BOLD}{COLOR_YELLOW}Total Tests: {counters['total']}{COLOR_RESET}")

if __name__ == "__main__":
    main()

