@echo off
title PORTAIL C2B DE L'ENTREPRISE - Construction Excellence Quebec Inc.
echo ========================================================
echo   PORTAIL C2B DE L'ENTREPRISE
echo   Client a Entreprise - Construction
echo ========================================================
echo.

echo [1/4] Verification de la configuration entreprise...
py config_entreprise_unique.py
if %errorlevel% neq 0 (
    echo ERREUR: Probleme de configuration entreprise
    echo Veuillez verifier config_entreprise_unique.py
    pause
    exit /b 1
)

echo.
echo [2/4] Installation/verification des dependances...
py -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERREUR: Impossible d'installer les dependances
    pause
    exit /b 1
)

echo.
echo [3/4] Initialisation de la base de donnees mono-entreprise...
py init_db_approbation.py
if %errorlevel% neq 0 (
    echo ERREUR: Echec initialisation base de donnees
    pause
    exit /b 1
)

echo.
echo [4/4] Lancement du portail Streamlit...
echo.
echo ========================================================
echo   PORTAIL PRET !
echo   Acces: http://localhost:8501
echo   
echo   Connexions:
echo   - Entreprise: alex@constructionexcellence.ca / entreprise123
echo   - Clients: *.ca / demo123  
echo   - Admin: admin123
echo ========================================================
echo.

py -m streamlit run app.py

echo.
echo Application fermee.
pause