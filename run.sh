#!/bin/bash
# =====================================================
# Script to run .nyunda files (Unix/Linux/macOS)
# To make it executable, run: chmod +x run.sh
# =====================================================
# Usage Examples:
#
# 1. Run a file with clean output:
#    ./run.sh examples/factorial.nyunda
#
# 2. Run with a detailed performance report:
#    ./run.sh examples/fibonacci.nyunda --verbose
#
# 3. Run with verbose report but disable an optimization:
#    ./run.sh examples/factorial.nyunda --verbose --no-greedy
#
# 4. Run the internal demo (if no file is provided):
#    ./run.sh
# =====================================================

# Pass all script arguments (flags and filepath) directly to the Python interpreter.
python3 main.py "$@"

