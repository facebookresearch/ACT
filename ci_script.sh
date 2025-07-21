# Copyright (c) Meta Platforms, Inc. and affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/bin/bash

# CI script to ensure minimal stability

# ensure that the ACT model binary initializes and minimally runs properly
python -m act.act_model

# ensure CI tests are stable

# Get the directory path from the current script location
TEST_DIR=$(dirname "$0")/act/tests

# Check if the test directory exists
if [ ! -d "$TEST_DIR" ]; then
  echo "Test directory not found: $TEST_DIR"
  exit 1
fi

# Find all Python files in the test directory and convert them to module paths
MODULES=()
for file in "$TEST_DIR"/*.py; do
  # Convert the file path to a module path (e.g., act/tests/test_file.py -> act.tests.test_file)
  module=${file#$TEST_DIR/}
  module=${module%.py}
  module=${module//\//.}
  MODULES+=("act.tests.$module")
done

# Run the tests using python -m unittest
python -m unittest "${MODULES[@]}"

# Ensure the README.md command works
python -m act.act_model -m act/boms/dellr740.yaml

# Ensure help function works as advertised in README.md
python -m act.act_model --help
