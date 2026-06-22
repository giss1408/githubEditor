#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de débogage pour la connexion GitHub
"""

import sys
import requests
import base64
import re
from typing import Optional

def test_github_connection(token: str, repo_url: str) -> bool:
    """Tester la connexion à GitHub avec des détails"""
    
    print("🔍 Test de connexion à GitHub...")
    print("=" * 50)
    
    # Extraire owner et repo
    match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
    if not match:
        print("❌ URL de dépôt invalide")
        print(f"   Format attendu: https://github.com/utilisateur/repo")
        print(f"   Reçu: {repo_url}")
        return False
    
    owner = match.group(1)
    repo = match.group(2)
    print(f"📦 Dépôt: {owner}/{repo}")
    
    # Tester le token
    print("\n🔑 Test du token...")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHubDocEditor/1.0"
    }
    
    try:
        # Tester le token
        response = requests.get(
            "https://api.github.com/user",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Token valide pour l'utilisateur: {user_data.get('login')}")
        elif response.status_code == 401:
            print("❌ Token invalide ou expiré")
            print("   Générez un nouveau token avec les permissions 'repo' et 'workflow'")
            return False
        elif response.status_code == 403:
            print("❌ Token insuffisant")
            print("   Assurez-vous d'avoir les permissions 'repo' et 'workflow'")
            return False
        else:
            print(f"❌ Erreur inattendue: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
        
        # Tester l'accès au dépôt
        print(f"\n📂 Test d'accès au dépôt {owner}/{repo}...")
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ Dépôt accessible: {repo_data.get('full_name')}")
            print(f"   🌿 Branche par défaut: {repo_data.get('default_branch')}")
            print(f"   📝 Description: {repo_data.get('description', 'Aucune description')}")
        elif response.status_code == 404:
            print(f"❌ Dépôt non trouvé: {owner}/{repo}")
            print("   Vérifiez que le dépôt existe et que vous avez les droits d'accès")
            return False
        elif response.status_code == 403:
            print(f"❌ Accès refusé au dépôt")
            print("   Vérifiez les permissions du token")
            return False
        else:
            print(f"❌ Erreur inattendue: {response.status_code}")
            return False
        
        # Tester la lecture des fichiers
        print("\n📄 Test de lecture des fichiers...")
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            files = response.json()
            file_count = len([f for f in files if f['type'] == 'file'])
            print(f"✅ Fichiers trouvés: {file_count}")
            if file_count > 0:
                print("   📋 Premier fichier:")
                first_file = next(f for f in files if f['type'] == 'file')
                print(f"      - {first_file['name']} ({first_file['size']} octets)")
        elif response.status_code == 404:
            print("ℹ️ Le dépôt est vide ou le chemin n'existe pas")
        else:
            print(f"❌ Erreur lors de la lecture des fichiers: {response.status_code}")
        
        # Tester l'écriture (avec un fichier temporaire)
        print("\n✏️ Test d'écriture (création d'un fichier temporaire)...")
        test_content = "Test de connexion GitHub Document Editor"
        encoded_content = base64.b64encode(test_content.encode('utf-8')).decode('utf-8')
        
        test_file = ".github_editor_test.txt"
        data = {
            "message": "Test de connexion",
            "content": encoded_content
        }
        
        response = requests.put(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{test_file}",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ Test d'écriture réussi!")
            
            # Supprimer le fichier de test
            print("\n🗑️ Nettoyage du fichier de test...")
            sha = response.json()['content']['sha']
            delete_data = {
                "message": "Suppression du fichier de test",
                "sha": sha
            }
            
            delete_response = requests.delete(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{test_file}",
                headers=headers,
                json=delete_data,
                timeout=10
            )
            
            if delete_response.status_code == 200:
                print("✅ Nettoyage terminé")
            else:
                print(f"⚠️ Nettoyage échoué: {delete_response.status_code}")
                print(f"   Supprimez manuellement le fichier {test_file}")
                
        elif response.status_code == 422:
            # Le fichier existe peut-être déjà
            print("ℹ️ Le fichier de test existe déjà, test d'écriture non concluant")
        else:
            print(f"❌ Test d'écriture échoué: {response.status_code}")
            print(f"   {response.text[:200]}")
            print("   Assurez-vous que le token a les permissions d'écriture")
        
        print("\n" + "=" * 50)
        print("✅ Test de connexion terminé avec succès!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion réseau")
        print("   Vérifiez votre connexion internet")
        return False
    except requests.exceptions.Timeout:
        print("❌ Délai de connexion dépassé")
        print("   Le serveur GitHub ne répond pas")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return False

def main():
    """Fonction principale de débogage"""
    print("🐞 Script de débogage GitHub Connection")
    print("=" * 50)
    
    # Demander les identifiants
    token = input("\n🔑 Entrez votre token GitHub: ").strip()
    if not token:
        print("❌ Token requis")
        return 1
    
    repo_url = input("📦 Entrez l'URL du dépôt: ").strip()
    if not repo_url:
        print("❌ URL du dépôt requise")
        return 1
    
    print()
    success = test_github_connection(token, repo_url)
    
    if success:
        print("\n✨ La connexion fonctionne! Vous pouvez utiliser l'application.")
        return 0
    else:
        print("\n❌ La connexion a échoué. Vérifiez les erreurs ci-dessus.")
        return 1

if __name__ == "__main__":
    sys.exit(main())