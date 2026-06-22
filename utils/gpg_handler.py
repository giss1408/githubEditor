# -*- coding: utf-8 -*-

"""
Gestionnaire GPG pour le chiffrement/déchiffrement des fichiers .rg.gpg
Avec diagnostic avancé et gestion d'erreurs
"""

import subprocess
import tempfile
import os
import shutil
import tarfile
import base64
from typing import Optional, Tuple, Union, List


class GPGHandler:
    """Gestionnaire des opérations GPG pour .rg.gpg"""
    
    def __init__(self):
        self.debug = True
        self.gpg_available = self._check_gpg_available()
        self.temp_dir = None
        self.gpg_version = self._get_gpg_version()
    
    def _check_gpg_available(self) -> bool:
        try:
            result = subprocess.run(
                ['gpg', '--version'], 
                capture_output=True, 
                check=True,
                text=True
            )
            if self.debug:
                print(f"✅ GPG disponible: {result.stdout.splitlines()[0] if result.stdout else 'Version inconnue'}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ GPG non trouvé")
            return False
    
    def _get_gpg_version(self) -> str:
        try:
            result = subprocess.run(
                ['gpg', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.splitlines()[0] if result.stdout else "Version inconnue"
        except:
            return "Version inconnue"
    
    def decrypt_rg_gpg(self, encrypted_content: bytes, password: str) -> List[Tuple[str, str]]:
        """
        Déchiffrer un fichier .rg.gpg avec diagnostic avancé
        """
        if not self.gpg_available:
            raise Exception("GPG n'est pas installé")
        
        if not encrypted_content:
            raise Exception("Le fichier est vide ou corrompu")
        
        # Diagnostic du fichier
        if self.debug:
            print(f"🔍 Diagnostic du fichier:")
            print(f"   - Taille: {len(encrypted_content)} octets")
            print(f"   - Version GPG: {self.gpg_version}")
            print(f"   - Premiers octets: {encrypted_content[:20].hex()}")
            
            # Vérifier si c'est un fichier GPG valide
            if encrypted_content[:2] == b'\x85\x02':
                print("   - Format: GPG packet (version 2)")
            elif encrypted_content[:2] == b'\x99\x04':
                print("   - Format: GPG packet (version 4)")
            elif encrypted_content[:2] == b'\x8c\x0d':
                print("   - Format: GPG packet (version 13)")
            else:
                print("   - Format: Inconnu ou corrompu")
        
        self.temp_dir = tempfile.mkdtemp(prefix='gpg_editor_')
        if self.debug:
            print(f"📁 Répertoire temporaire: {self.temp_dir}")
        
        try:
            # Écrire le contenu chiffré
            gpg_path = os.path.join(self.temp_dir, 'mesNotes.rg.gpg')
            with open(gpg_path, 'wb') as f:
                f.write(encrypted_content)
            
            # Essayer plusieurs méthodes de déchiffrement
            methods = [
                self._decrypt_with_output,
                self._decrypt_stdout,
                self._decrypt_with_pinentry,
                self._decrypt_with_old_format
            ]
            
            output_path = None
            last_error = None
            
            for i, method in enumerate(methods, 1):
                if self.debug:
                    print(f"\n🔓 Tentative {i}/{len(methods)}...")
                try:
                    result = method(gpg_path, password, self.temp_dir)
                    if result and os.path.exists(result) and os.path.getsize(result) > 0:
                        output_path = result
                        if self.debug:
                            print(f"   ✅ Méthode {i} réussie!")
                        break
                except Exception as e:
                    last_error = str(e)
                    if self.debug:
                        print(f"   ❌ Méthode {i} échouée: {e}")
                    continue
            
            if not output_path:
                raise Exception(f"❌ Toutes les méthodes ont échoué. Dernière erreur: {last_error}")
            
            # Extraire l'archive
            return self._extract_tar_archive(output_path)
            
        except Exception as e:
            raise Exception(f"❌ Erreur: {str(e)}")
    
    def _decrypt_with_output(self, gpg_path: str, password: str, temp_dir: str) -> Optional[str]:
        """Méthode 1: gpg --decrypt --output"""
        output_path = os.path.join(temp_dir, 'mesNotes.rg')
        cmd = [
            'gpg',
            '--batch',
            '--passphrase', password,
            '--no-symkey-cache',
            '--decrypt',
            '--output', output_path,
            gpg_path
        ]
        
        if self.debug:
            print(f"   Commande: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        
        # Vérifier si un autre fichier a été créé
        for f in os.listdir(temp_dir):
            if f.endswith('.rg') and not f.endswith('.gpg'):
                return os.path.join(temp_dir, f)
        
        return None
    
    def _decrypt_stdout(self, gpg_path: str, password: str, temp_dir: str) -> Optional[str]:
        """Méthode 2: gpg --decrypt avec stdout redirigé"""
        cmd = [
            'gpg',
            '--batch',
            '--passphrase', password,
            '--no-symkey-cache',
            '--decrypt',
            gpg_path
        ]
        
        if self.debug:
            print(f"   Commande: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout and len(result.stdout) > 0:
            output_path = os.path.join(temp_dir, 'mesNotes.rg')
            with open(output_path, 'wb') as f:
                f.write(result.stdout)
            return output_path
        
        return None
    
    def _decrypt_with_pinentry(self, gpg_path: str, password: str, temp_dir: str) -> Optional[str]:
        """Méthode 3: Avec pinentry-mode loopback"""
        output_path = os.path.join(temp_dir, 'mesNotes.rg')
        cmd = [
            'gpg',
            '--batch',
            '--passphrase', password,
            '--no-symkey-cache',
            '--pinentry-mode', 'loopback',
            '--decrypt',
            '--output', output_path,
            gpg_path
        ]
        
        if self.debug:
            print(f"   Commande: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        
        return None
    
    def _decrypt_with_old_format(self, gpg_path: str, password: str, temp_dir: str) -> Optional[str]:
        """Méthode 4: Avec --rfc1991 pour le format ancien"""
        output_path = os.path.join(temp_dir, 'mesNotes.rg')
        cmd = [
            'gpg',
            '--batch',
            '--passphrase', password,
            '--no-symkey-cache',
            '--rfc1991',
            '--decrypt',
            '--output', output_path,
            gpg_path
        ]
        
        if self.debug:
            print(f"   Commande: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        
        return None
    
    def _extract_tar_archive(self, tar_path: str) -> List[Tuple[str, str]]:
        """Extraire une archive tar"""
        extract_dir = os.path.join(os.path.dirname(tar_path), 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        
        if self.debug:
            print(f"📦 Extraction de l'archive tar...")
        
        extracted = False
        
        # Méthode 1: tarfile avec gzip
        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
            extracted = True
            if self.debug:
                print("   ✅ Extraction avec tarfile (gzip)")
        except Exception as e:
            if self.debug:
                print(f"   ⚠️ tarfile gzip échoué: {e}")
        
        # Méthode 2: tarfile sans compression
        if not extracted:
            try:
                with tarfile.open(tar_path, 'r') as tar:
                    tar.extractall(extract_dir)
                extracted = True
                if self.debug:
                    print("   ✅ Extraction avec tarfile (sans compression)")
            except Exception as e:
                if self.debug:
                    print(f"   ⚠️ tarfile sans compression échoué: {e}")
        
        # Méthode 3: commande tar externe
        if not extracted:
            try:
                cmd_tar = ['tar', '-xzf', tar_path, '-C', extract_dir]
                result_tar = subprocess.run(cmd_tar, capture_output=True, text=True)
                if result_tar.returncode == 0:
                    extracted = True
                    if self.debug:
                        print("   ✅ Extraction avec tar externe (gzip)")
                else:
                    cmd_tar = ['tar', '-xf', tar_path, '-C', extract_dir]
                    result_tar = subprocess.run(cmd_tar, capture_output=True, text=True)
                    if result_tar.returncode == 0:
                        extracted = True
                        if self.debug:
                            print("   ✅ Extraction avec tar externe (sans compression)")
            except Exception as e:
                if self.debug:
                    print(f"   ⚠️ tar externe échoué: {e}")
        
        if not extracted:
            raise Exception("❌ Impossible d'extraire l'archive tar")
        
        # Lire les fichiers extraits
        files_content = []
        for root, dirs, filenames in os.walk(extract_dir):
            for file in filenames:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, extract_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    files_content.append((relative_path, content))
                    if self.debug:
                        print(f"   ✅ {relative_path} ({len(content)} caractères)")
                except UnicodeDecodeError:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    files_content.append((relative_path, content.decode('latin-1')))
                    if self.debug:
                        print(f"   ✅ {relative_path} (fichier binaire)")
        
        if not files_content:
            raise Exception("❌ Aucun fichier trouvé dans l'archive")
        
        if self.debug:
            print(f"\n✅ Succès! {len(files_content)} fichier(s) extrait(s)")
        
        return files_content
    
    def encrypt_rg_gpg(self, files_content: List[Tuple[str, str]], password: str) -> bytes:
        """
        Chiffrer des fichiers en .rg.gpg
        Commandes: tar czf mesNotes.rg mesNotes/ && gpg --no-symkey-cache --cipher-algo AES256 -c mesNotes.rg
        """
        if not self.gpg_available:
            raise Exception("GPG n'est pas installé")
        
        try:
            temp_dir = tempfile.mkdtemp(prefix='gpg_encrypt_')
            if self.debug:
                print(f"📁 Répertoire temporaire: {temp_dir}")
            
            # Créer les fichiers
            if self.debug:
                print("📝 Création des fichiers...")
            
            for filename, content in files_content:
                file_path = os.path.join(temp_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    if self.debug:
                        print(f"   ✅ {filename}")
                except:
                    with open(file_path, 'wb') as f:
                        f.write(content.encode('latin-1'))
                    if self.debug:
                        print(f"   ✅ {filename} (binaire)")
            
            # Créer l'archive tar
            tar_name = 'mesNotes.rg'
            tar_path = os.path.join(temp_dir, tar_name)
            
            if self.debug:
                print(f"📦 Création de l'archive tar...")
            
            with tarfile.open(tar_path, 'w:gz') as tar:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file == tar_name or file.endswith('.gpg'):
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        tar.add(file_path, arcname=arcname)
                        if self.debug:
                            print(f"   ✅ Ajout: {arcname}")
            
            if not os.path.exists(tar_path):
                raise Exception("❌ L'archive tar n'a pas été créée")
            
            tar_size = os.path.getsize(tar_path)
            if self.debug:
                print(f"📊 Taille de l'archive: {tar_size} octets")
            
            # Chiffrer l'archive
            if self.debug:
                print(f"🔒 Chiffrement GPG...")
            
            # Utiliser la commande complète
            cmd = [
                'gpg',
                '--batch',
                '--passphrase', password,
                '--no-symkey-cache',
                '--cipher-algo', 'AES256',
                '-c',
                tar_path
            ]
            
            if self.debug:
                print(f"🔑 Commande: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if self.debug:
                if result.stdout:
                    print(f"📝 Sortie GPG: {result.stdout}")
                if result.stderr:
                    print(f"⚠️ Erreur GPG: {result.stderr}")
            
            if result.returncode != 0:
                raise Exception(f"❌ Erreur GPG: {result.stderr}")
            
            # Lire le fichier chiffré
            gpg_path = os.path.join(temp_dir, 'mesNotes.rg.gpg')
            
            if not os.path.exists(gpg_path):
                for f in os.listdir(temp_dir):
                    if f.endswith('.gpg'):
                        gpg_path = os.path.join(temp_dir, f)
                        break
                else:
                    raise Exception("❌ Le fichier chiffré n'a pas été créé")
            
            with open(gpg_path, 'rb') as f:
                encrypted_content = f.read()
            
            if self.debug:
                print(f"✅ Chiffrement réussi ({len(encrypted_content)} octets)")
            
            shutil.rmtree(temp_dir)
            
            return encrypted_content
            
        except Exception as e:
            raise Exception(f"❌ Erreur lors du chiffrement: {str(e)}")
    
    def decrypt_file_binary(self, encrypted_content: bytes, password: str) -> Optional[bytes]:
        """Déchiffrer un contenu GPG simple"""
        if not self.gpg_available:
            raise Exception("GPG n'est pas installé")
        
        if not encrypted_content:
            raise Exception("Le fichier est vide ou corrompu")
        
        try:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.gpg') as temp_in:
                temp_in.write(encrypted_content)
                temp_in_path = temp_in.name
            
            output_path = temp_in_path.replace('.gpg', '.decrypted')
            
            cmd = [
                'gpg',
                '--batch',
                '--passphrase', password,
                '--no-symkey-cache',
                '--output', output_path,
                '--decrypt',
                temp_in_path
            ]
            
            if self.debug:
                print(f"🔓 Déchiffrement simple...")
                print(f"🔑 Commande: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                error_msg = result.stderr
                if 'Bad passphrase' in error_msg:
                    raise Exception("❌ Mot de passe incorrect")
                else:
                    raise Exception(f"❌ Erreur GPG: {error_msg}")
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                with open(output_path, 'rb') as f:
                    decrypted_data = f.read()
                
                os.unlink(temp_in_path)
                os.unlink(output_path)
                
                if self.debug:
                    print(f"✅ Déchiffrement réussi ({len(decrypted_data)} octets)")
                return decrypted_data
            else:
                raise Exception("❌ Le fichier déchiffré est vide")
            
        except Exception as e:
            raise Exception(f"Erreur lors du déchiffrement: {str(e)}")
    
    def encrypt_file(self, content: Union[str, bytes], password: str) -> bytes:
        """Chiffrer un fichier simple"""
        if not self.gpg_available:
            raise Exception("GPG n'est pas installé")
        
        try:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_in:
                if isinstance(content, str):
                    temp_in.write(content.encode('utf-8'))
                else:
                    temp_in.write(content)
                temp_in_path = temp_in.name
            
            output_path = f"{temp_in_path}.gpg"
            
            cmd = [
                'gpg',
                '--batch',
                '--passphrase', password,
                '--no-symkey-cache',
                '-c',
                '--cipher-algo', 'AES256',
                '--output', output_path,
                temp_in_path
            ]
            
            if self.debug:
                print(f"🔒 Chiffrement simple...")
                print(f"🔑 Commande: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f"Erreur GPG: {result.stderr}")
            
            if os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    encrypted_content = f.read()
                
                os.unlink(temp_in_path)
                os.unlink(output_path)
                
                if self.debug:
                    print(f"✅ Chiffrement réussi ({len(encrypted_content)} octets)")
                return encrypted_content
            else:
                raise Exception("Le fichier chiffré n'a pas été créé")
            
        except Exception as e:
            raise Exception(f"Erreur lors du chiffrement: {str(e)}")
    
    def is_gpg_file(self, filename: str) -> bool:
        return filename.endswith('.gpg') or filename.endswith('.asc')
    
    def is_rg_gpg(self, filename: str) -> bool:
        return filename.endswith('.rg.gpg')
    
    def is_tar_gpg(self, filename: str) -> bool:
        return filename.endswith('.tar.gpg') or filename.endswith('.tgz.gpg')
    
    def get_file_type(self, filename: str) -> str:
        if filename.endswith('.rg.gpg'):
            return 'rg_gpg'
        elif filename.endswith('.tar.gpg') or filename.endswith('.tgz.gpg'):
            return 'tar_gpg'
        elif filename.endswith('.gpg') or filename.endswith('.asc'):
            return 'gpg'
        return 'unknown'
    
    def cleanup(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                if self.debug:
                    print(f"🧹 Nettoyage du répertoire temporaire: {self.temp_dir}")
            except Exception as e:
                if self.debug:
                    print(f"⚠️ Erreur lors du nettoyage: {e}")
            self.temp_dir = None