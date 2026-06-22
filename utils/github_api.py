# -*- coding: utf-8 -*-

"""
Interface améliorée avec l'API GitHub
"""

import requests
import base64
import re
import json
from typing import Dict, List, Tuple, Optional
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout

class GitHubAPIError(Exception):
    """Exception personnalisée pour les erreurs GitHub API"""
    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

class GitHubAPI:
    """Client pour l'API GitHub avec gestion d'erreurs améliorée"""
    
    def __init__(self, token: str, repo_url: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHubDocEditor/1.0"
        })
        
        # Extraire owner et repo de l'URL
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if match:
            self.owner = match.group(1)
            self.repo = match.group(2)
        else:
            raise ValueError(f"URL de dépôt invalide: {repo_url}")
        
        # Tester le token immédiatement
        self._validate_token()
    
    def _validate_token(self):
        """Valider le token GitHub"""
        try:
            response = self.session.get(
                f"{self.base_url}/user",
                timeout=10
            )
            
            if response.status_code == 401:
                raise GitHubAPIError(
                    "Token invalide ou expiré. Vérifiez votre token.",
                    status_code=401
                )
            elif response.status_code == 403:
                raise GitHubAPIError(
                    "Token insuffisant. Assurez-vous d'avoir les permissions 'repo' et 'workflow'.",
                    status_code=403
                )
            elif response.status_code == 404:
                raise GitHubAPIError(
                    "Dépôt non trouvé. Vérifiez l'URL.",
                    status_code=404
                )
            response.raise_for_status()
            
        except ConnectionError:
            raise GitHubAPIError(
                "Erreur de connexion. Vérifiez votre connexion internet."
            )
        except Timeout:
            raise GitHubAPIError(
                "Délai de connexion dépassé. Vérifiez votre connexion internet."
            )
        except HTTPError as e:
            raise GitHubAPIError(
                f"Erreur HTTP: {str(e)}",
                status_code=e.response.status_code if e.response else None
            )
        except RequestException as e:
            raise GitHubAPIError(f"Erreur de requête: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                      params: Optional[Dict] = None) -> Dict:
        """Effectuer une requête vers l'API GitHub avec gestion d'erreurs"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f"Méthode non supportée: {method}")
            
            # Vérifier les codes d'erreur spécifiques
            if response.status_code == 401:
                raise GitHubAPIError(
                    "Token invalide ou expiré. Veuillez vous reconnecter.",
                    status_code=401,
                    response=response
                )
            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                if 'rate limit' in str(error_data).lower():
                    raise GitHubAPIError(
                        "Limite de requêtes API dépassée. Attendez quelques minutes.",
                        status_code=403,
                        response=response
                    )
                else:
                    raise GitHubAPIError(
                        f"Permission insuffisante: {error_data.get('message', 'Vérifiez vos permissions')}",
                        status_code=403,
                        response=response
                    )
            elif response.status_code == 404:
                raise GitHubAPIError(
                    f"Ressource non trouvée: {endpoint}",
                    status_code=404,
                    response=response
                )
            elif response.status_code == 422:
                error_data = response.json() if response.content else {}
                raise GitHubAPIError(
                    f"Erreur de validation: {error_data.get('message', 'Données invalides')}",
                    status_code=422,
                    response=response
                )
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except GitHubAPIError:
            raise
        except ConnectionError:
            raise GitHubAPIError(
                "Erreur de connexion réseau. Vérifiez votre connexion internet."
            )
        except Timeout:
            raise GitHubAPIError(
                "Délai de connexion dépassé. Le serveur GitHub ne répond pas."
            )
        except HTTPError as e:
            error_msg = f"Erreur HTTP {e.response.status_code}: "
            try:
                error_data = e.response.json()
                error_msg += error_data.get('message', str(e))
            except:
                error_msg += str(e)
            raise GitHubAPIError(error_msg, status_code=e.response.status_code)
        except RequestException as e:
            raise GitHubAPIError(f"Erreur de requête: {str(e)}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """Tester la connexion à GitHub avec message détaillé"""
        try:
            # Tester l'accès au dépôt
            endpoint = f"/repos/{self.owner}/{self.repo}"
            self._make_request("GET", endpoint)
            
            # Tester les permissions d'écriture
            endpoint = f"/repos/{self.owner}/{self.repo}/contents/test_permissions"
            try:
                self._make_request("GET", endpoint)
            except GitHubAPIError as e:
                if e.status_code == 404:
                    # Pas grave, le fichier n'existe pas
                    pass
                elif e.status_code == 403:
                    return False, "Permissions insuffisantes. Assurez-vous d'avoir les permissions 'repo'."
            
            return True, "Connexion réussie"
            
        except GitHubAPIError as e:
            return False, f"Erreur: {e.message}"
        except Exception as e:
            return False, f"Erreur inattendue: {str(e)}"
    
    def get_files(self, path: str = "") -> List[Dict]:
        """Obtenir la liste des fichiers du dépôt"""
        endpoint = f"/repos/{self.owner}/{self.repo}/contents/{path}" if path else f"/repos/{self.owner}/{self.repo}/contents"
        
        try:
            response = self._make_request("GET", endpoint)
            
            # Si c'est un fichier unique
            if isinstance(response, dict) and 'content' in response:
                return [response]
            
            # Si c'est une liste de fichiers
            if isinstance(response, list):
                return [item for item in response if item['type'] == 'file']
            
            return []
            
        except GitHubAPIError as e:
            if e.status_code == 404:
                return []  # Dossier vide ou inexistant
            raise
    
    def get_file_content(self, path: str) -> Tuple[str, str]:
        """Obtenir le contenu d'un fichier"""
        endpoint = f"/repos/{self.owner}/{self.repo}/contents/{path}"
        response = self._make_request("GET", endpoint)
        
        try:
            # Décoder le contenu base64
            content = base64.b64decode(response['content']).decode('utf-8')
            sha = response['sha']
            return content, sha
        except KeyError:
            raise GitHubAPIError("Réponse invalide du serveur")
        except UnicodeDecodeError:
            raise GitHubAPIError("Le fichier n'est pas un fichier texte valide")
    
    def commit_file(self, path: str, content: str, message: str, sha: str) -> bool:
        """Commiter un fichier"""
        endpoint = f"/repos/{self.owner}/{self.repo}/contents/{path}"
        
        try:
            # Encoder en base64
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            data = {
                "message": message,
                "content": encoded_content,
                "sha": sha
            }
            
            response = self._make_request("PUT", endpoint, data)
            return 'content' in response
            
        except GitHubAPIError as e:
            if e.status_code == 409:
                raise GitHubAPIError(
                    "Le fichier a été modifié sur GitHub. Rafraîchissez et réessayez."
                )
            raise
    
    def upload_file(self, path: str, content: str, message: Optional[str] = None) -> bool:
        """Télécharger un nouveau fichier"""
        if not message:
            message = f"Ajout de {path}"
        
        try:
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            data = {
                "message": message,
                "content": encoded_content
            }
            
            endpoint = f"/repos/{self.owner}/{self.repo}/contents/{path}"
            response = self._make_request("PUT", endpoint, data)
            return 'content' in response
            
        except GitHubAPIError as e:
            if e.status_code == 422:
                raise GitHubAPIError(
                    "Un fichier avec ce nom existe déjà. Utilisez commit pour le modifier."
                )
            raise
    
    def get_commits(self, limit: int = 20) -> List[Dict]:
        """Obtenir l'historique des commits"""
        endpoint = f"/repos/{self.owner}/{self.repo}/commits"
        params = {"per_page": limit}
        
        try:
            commits = self._make_request("GET", endpoint, params=params)
            
            result = []
            for commit in commits:
                result.append({
                    'sha': commit['sha'],
                    'message': commit['commit']['message'],
                    'author': commit['commit']['author']['name'],
                    'date': commit['commit']['author']['date']
                })
            
            return result
            
        except GitHubAPIError as e:
            if e.status_code == 404:
                return []  # Pas de commits
            raise

    def get_file_content_binary(self, path: str) -> Tuple[bytes, str]:
        """
        Obtenir le contenu binaire d'un fichier
        
        Args:
            path: Chemin du fichier
            
        Returns:
            Tuple (contenu_bytes, sha)
        """
        endpoint = f"/repos/{self.owner}/{self.repo}/contents/{path}"
        response = self._make_request("GET", endpoint)
        
        try:
            # Décoder le contenu base64 en bytes (binaire)
            content_bytes = base64.b64decode(response['content'])
            sha = response['sha']
            return content_bytes, sha
        except KeyError:
            raise GitHubAPIError("Réponse invalide du serveur")
        except Exception as e:
            raise GitHubAPIError(f"Erreur lors de la lecture du fichier: {str(e)}")