@echo off
git checkout -b seed_fixes > branch_log.txt 2>&1
if %errorlevel% neq 0 (
    echo Branch might exist, trying checkout... >> branch_log.txt
    git checkout seed_fixes >> branch_log.txt 2>&1
)
echo DONE >> branch_log.txt
