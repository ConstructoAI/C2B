@echo off
title Configuration Nouvelle Entreprise
echo ========================================================
echo   CONFIGURATION NOUVELLE ENTREPRISE
echo ========================================================
echo.
echo Ce script vous aide a configurer le portail pour une nouvelle entreprise.
echo.

echo ETAPES:
echo 1. Editez le fichier config_entreprise_unique.py
echo 2. Modifiez les informations de l'entreprise
echo 3. Changez le mot de passe par defaut
echo 4. Relancez run.bat
echo.

echo Ouverture du fichier de configuration...
notepad config_entreprise_unique.py

echo.
echo INFORMATIONS A MODIFIER:
echo - nom_entreprise: Nom de votre entreprise
echo - numero_rbq: Votre numero RBQ (si applicable)  
echo - nom_contact: Nom du contact principal
echo - email: Email de connexion de l'entreprise
echo - telephone: Numero de telephone
echo - adresse, ville, code_postal: Coordonnees
echo - mot_de_passe: CHANGEZ "entreprise123" pour la securite
echo - domaines_expertise: Vos specialites
echo - description_entreprise: Description detaillee
echo.

set /p continuer="Appuyez sur Entree apres avoir modifie le fichier..."

echo.
echo Verification de la nouvelle configuration...
py config_entreprise_unique.py

if %errorlevel% equ 0 (
    echo.
    echo Configuration validee ! Vous pouvez maintenant lancer run.bat
    echo.
    set /p lancer="Voulez-vous lancer le portail maintenant ? (o/n): "
    if /i "%lancer%"=="o" (
        call run.bat
    )
) else (
    echo.
    echo ERREUR dans la configuration. Verifiez le fichier et reessayez.
)

pause