@echo off
rem =====================================================
rem Script to run .nyunda files (Windows)
rem =====================================================
rem Usage Examples:
rem
rem 1. Run a file with clean output:
rem    run.bat examples\factorial.nyunda
rem
rem 2. Run with a detailed performance report:
rem    run.bat examples\fibonacci.nyunda --verbose
rem
rem 3. Run with verbose report but disable an optimization:
rem    run.bat examples\factorial.nyunda --verbose --no-dp
rem
rem 4. Run the internal demo (if no file is provided):
rem    run.bat
rem =====================================================

rem Pass all script arguments (flags and filepath) directly to the Python interpreter.
python main.py %*
