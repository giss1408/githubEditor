# -*- coding: utf-8 -*-

"""
Gestionnaire de fichiers locaux
"""

import os
import json
import hashlib
from typing import Optional, Dict
from datetime import datetime

class FileManager:
    """Gestionnaire de fichiers pour l'application"""
    
    def __init__(self, cache_dir: str = ".github_editor_cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "file_cache.json")
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """S'assurer que le répertoire de cache existe"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache(self) -> Dict:
        """Obtenir le cache actuel"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self, cache: Dict):
        """Sauvegarder le cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    
    def save_file_locally(self, path: str, content: str) -> str:
        """Sauvegarder un fichier localement"""
        cache = self._get_cache()
        
        # Générer un hash du contenu
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Sauvegarder dans le cache
        cache[path] = {
            'content': content,
            'hash': content_hash,
            'last_modified': datetime.now().isoformat()
        }
        
        self._save_cache(cache)
        
        # Sauvegarder dans un fichier local
        local_path = os.path.join(self.cache_dir, path.replace('/', '_'))
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return local_path
    
    def load_local_file(self, path: str) -> Optional[str]:
        """Charger un fichier local"""
        cache = self._get_cache()
        
        if path in cache:
            return cache[path]['content']
        
        # Essayer de charger depuis le fichier local
        local_path = os.path.join(self.cache_dir, path.replace('/', '_'))
        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        return None
    
    def get_file_hash(self, path: str) -> Optional[str]:
        """Obtenir le hash d'un fichier"""
        cache = self._get_cache()
        if path in cache:
            return cache[path]['hash']
        return None
    
    def is_file_modified(self, path: str, current_content: str) -> bool:
        """Vérifier si un fichier a été modifié"""
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()
        stored_hash = self.get_file_hash(path)
        
        return current_hash != stored_hash
    
    def get_unsaved_files(self) -> list:
        """Obtenir la liste des fichiers non sauvegardés"""
        cache = self._get_cache()
        unsaved = []
        
        for path, data in cache.items():
            # Vérifier si le fichier existe toujours
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if self.is_file_modified(path, content):
                    unsaved.append(path)
        
        return unsaved