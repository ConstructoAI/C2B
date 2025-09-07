"""
Script de diagnostic pour vérifier les variables d'environnement Hugging Face
Exécutez ce script dans votre Space pour identifier les variables disponibles
"""

import os
import streamlit as st

def check_environment():
    """Vérifie et affiche les variables d'environnement pour le débogage"""
    
    st.title("🔍 Diagnostic Environnement Hugging Face")
    
    # Variables importantes à vérifier
    important_vars = [
        'SPACE_ID',
        'SPACE_HOST', 
        'SPACE_AUTHOR_NAME',
        'SPACE_REPO_NAME',
        'SYSTEM',
        'USER',
        'HOME',
        'PATH',
        'PORT',
        'APP_URL',
        'RENDER'
    ]
    
    st.header("Variables d'environnement importantes:")
    
    found_vars = {}
    for var in important_vars:
        value = os.getenv(var)
        if value:
            found_vars[var] = value
            st.success(f"✅ **{var}**: `{value}`")
        else:
            st.warning(f"❌ **{var}**: Non défini")
    
    # Afficher toutes les variables d'environnement
    st.header("Toutes les variables d'environnement:")
    
    all_vars = dict(os.environ)
    
    # Filtrer les variables sensibles
    sensitive_keywords = ['KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'API']
    filtered_vars = {}
    
    for key, value in all_vars.items():
        # Masquer les valeurs potentiellement sensibles
        if any(keyword in key.upper() for keyword in sensitive_keywords):
            filtered_vars[key] = "***MASKED***"
        else:
            filtered_vars[key] = value
    
    # Trier et afficher
    for key in sorted(filtered_vars.keys()):
        st.code(f"{key}={filtered_vars[key]}")
    
    # Générer l'URL recommandée
    st.header("🔗 URL détectée pour votre application:")
    
    # Logique de détection identique à get_base_url()
    if os.getenv('APP_URL'):
        detected_url = os.getenv('APP_URL')
        st.info(f"URL personnalisée (APP_URL): **{detected_url}**")
    elif os.getenv('SPACE_ID') or os.getenv('SPACE_HOST'):
        space_host = os.getenv('SPACE_HOST')
        if space_host:
            detected_url = f"https://{space_host}"
            st.info(f"URL Hugging Face (SPACE_HOST): **{detected_url}**")
        else:
            space_id = os.getenv('SPACE_ID')
            if space_id:
                detected_url = f"https://huggingface.co/spaces/{space_id}"
                st.info(f"URL Hugging Face (SPACE_ID): **{detected_url}**")
            else:
                detected_url = 'https://huggingface.co/spaces/Sylvainleduc/C2B'
                st.info(f"URL par défaut: **{detected_url}**")
    else:
        detected_url = 'http://localhost:8501'
        st.warning(f"Mode local détecté: **{detected_url}**")
    
    # Recommandations
    st.header("📝 Recommandations:")
    
    if 'SPACE_HOST' in found_vars:
        st.success("✅ SPACE_HOST est défini - C'est la meilleure variable à utiliser")
    elif 'SPACE_ID' in found_vars:
        st.info("ℹ️ SPACE_ID est défini - Peut être utilisé comme fallback")
    else:
        st.error("""
        ⚠️ Aucune variable Hugging Face détectée!
        
        **Solutions possibles:**
        1. Définir la variable APP_URL dans les Settings de votre Space:
           - Allez dans Settings → Variables and secrets
           - Ajoutez: `APP_URL = https://huggingface.co/spaces/Sylvainleduc/C2B`
        
        2. Ou vérifiez que votre Space est bien déployé sur Hugging Face
        """)
    
    # Test de génération de lien
    st.header("🧪 Test de génération de lien:")
    
    test_token = "test-1234-5678-90ab"
    test_link = f"{detected_url}/?token={test_token}&type=heritage"
    
    st.code(test_link)
    
    if "localhost" in test_link:
        st.error("❌ Le lien utilise localhost - Il ne fonctionnera pas pour vos clients!")
    else:
        st.success("✅ Le lien semble correct pour un accès externe")

if __name__ == "__main__":
    check_environment()