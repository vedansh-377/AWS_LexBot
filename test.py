import subprocess
import json
import time

def start_test_execution():
    # Start the test and retrieve the test execution ID
    command = [
        "aws",
        "lexv2-models",
        "start-test-execution",
        "--test-set-id",
        "M1CLOBRPZH",
        "--target",
        "botAliasTarget={botId=V2V5BO42CC,botAliasId=TSTALIASID,localeId=en_US}",
        "--api-mode",
        "Streaming",
        "--test-execution-modality",
        "Text"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    response = json.loads(result.stdout)
    test_execution_id = response.get("testExecutionId")

    if not test_execution_id:
        print("Failed to start test execution!")
        return None

    print(f"Test execution started with ID: {test_execution_id}")
    return test_execution_id

def get_test_execution_status(test_execution_id):
    while True:
        # Retrieve the test execution status
        command = [
            "aws",
            "lexv2-models",
            "describe-test-execution",
            "--test-execution-id",
            test_execution_id
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        response = json.loads(result.stdout)
        test_execution_status = response.get("testExecutionStatus")

        # Check if the test execution status is Completed or Failed
        if test_execution_status == "Completed":
            print("Completed")
            return "Completed"
        elif test_execution_status == "Failed":
            print("Failed")
            return "Failed"
        else:
            print(f"Test execution status: {test_execution_status}")
            time.sleep(5)  # Wait for 5 seconds before checking again

# Main function
def main():
    test_execution_id = start_test_execution()
    if test_execution_id:
        return get_test_execution_status(test_execution_id)
    else:
        return "Failed to start test execution!"

if __name__ == "__main__":
    final_status = main()
    print(f"::set-output name=final_status::{final_status}")
