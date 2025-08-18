@echo off
echo Demarrage du Systeme d'Approbation de Soumissions Entreprises...
echo.
echo Installation/verification des dependances...
py -m pip install -r requirements.txt

echo.
echo Initialisation de la base de donnees...
py init_db_approbation.py

echo.
echo Lancement de l'application Streamlit...
py -m streamlit run app.py

pause