#!/bin/bash

# Start the test and retrieve the test execution ID
test_response=$(aws lexv2-models start-test-execution \
    --test-set-id M1CLOBRPZH \
    --target "botAliasTarget={botId=V2V5BO42CC,botAliasId=TSTALIASID,localeId=en_US}" \
    --api-mode Streaming \
    --test-execution-modality Text)

# Extract the test execution ID from the response
test_execution_id=$(echo $test_response | jq -r '.testExecutionId')

# Check if the test execution ID is not empty
if [[ -n "$test_execution_id" ]]; then
    echo "Test execution started with ID: $test_execution_id"
else
    echo "Failed to start test execution!"
    exit 1
fi

# Loop until the test execution status is either Completed or Failed
while true; do
    # Retrieve the test execution status
    test_execution_status=$(aws lexv2-models describe-test-execution --test-execution-id $test_execution_id | jq -r '.testExecutionStatus')
    
    # Check if the test execution status is Completed or Failed
    if [[ "$test_execution_status" == "Completed" ]]; then
        echo "$test_execution_status"
        break
    elif [[ "$test_execution_status" == "Failed" ]]; then
        echo "Failed"
        exit 1
    else
        echo "Test execution status: $test_execution_status"
    fi
done
