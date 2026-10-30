@echo off
title Image Processing Toolkit
echo Starting Image Processing Toolkit...
py main.py
if %ERRORLEVEL% NEQ 0 (
    python main.py
)
pause
