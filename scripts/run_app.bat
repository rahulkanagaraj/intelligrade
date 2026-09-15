@echo off
echo =======================================================
echo   IntelliGrade Classifier - Air-Gapped Launch Script
echo =======================================================
cd /d "%~dp0\.."
echo Starting Streamlit Dashboard...
python -m streamlit run app.py
pause
