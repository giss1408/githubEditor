# -*- coding: utf-8 -*-

"""
Boîtes de dialogue - Version complète avec toutes les classes
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QFormLayout,
    QDialogButtonBox, QMessageBox, QTextBrowser,
    QApplication, QInputDialog, QCheckBox, QListWidget,
    QListWidgetItem, QSplitter
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QClipboard, QIcon


class LoginDialog(QDialog):
    """Boîte de dialogue de connexion GitHub"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Connexion à GitHub")
        self.setModal(True)
        self.setMinimumWidth(550)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🔐 Connexion à GitHub")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Entrez vos identifiants GitHub pour accéder à vos dépôts")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        # Formulaire
        form_layout = QFormLayout()
        
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("https://github.com/utilisateur/repo")
        self.repo_input.textChanged.connect(self.validate_input)
        self.repo_input.setToolTip("Exemple: https://github.com/giss1408/mon-repo")
        form_layout.addRow("📦 URL du dépôt:", self.repo_input)
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("ghp_xxxxxxxxxxxx")
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.textChanged.connect(self.validate_input)
        self.token_input.setToolTip("Token généré dans GitHub Settings → Developer settings")
        form_layout.addRow("🔑 Token d'accès:", self.token_input)
        
        layout.addLayout(form_layout)
        
        # Aide à la saisie
        self.help_label = QLabel()
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet("""
            color: #57606a; 
            font-size: 11px; 
            padding: 8px; 
            background-color: #f6f8fa; 
            border-radius: 4px;
        """)
        self.update_help_text()
        layout.addWidget(self.help_label)
        
        layout.addSpacing(10)
        
        # Note
        note = QLabel("💡 Créez un token avec les permissions 'repo' et 'workflow'")
        note.setStyleSheet("color: #57606a; font-size: 10px;")
        note.setWordWrap(True)
        layout.addWidget(note)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Valider initialement
        self.validate_input()
    
    def update_help_text(self):
        """Mettre à jour le texte d'aide"""
        repo_text = self.repo_input.text().strip()
        
        if not repo_text:
            self.help_label.setText(
                "💡 Exemples d'URL valides:\n"
                "• https://github.com/utilisateur/mon-repo\n"
                "• utilisateur/mon-repo\n\n"
                "⚠️ Important: Incluez le NOM DU DÉPÔT, pas seulement le nom d'utilisateur!"
            )
            self.help_label.setStyleSheet("""
                color: #57606a; 
                font-size: 11px; 
                padding: 8px; 
                background-color: #f6f8fa; 
                border-radius: 4px;
            """)
        elif 'github.com/' in repo_text and '/' not in repo_text.replace('https://github.com/', ''):
            self.help_label.setText(
                "⚠️ Vous avez entré un nom d'utilisateur mais pas de dépôt.\n\n"
                "Format correct: https://github.com/UTILISATEUR/NOM_DU_DÉPÔT\n"
                "Exemple: https://github.com/giss1408/mon-projet"
            )
            self.help_label.setStyleSheet("""
                color: #d73a49; 
                font-size: 11px; 
                padding: 8px; 
                background-color: #ffeef0; 
                border-radius: 4px;
            """)
        elif len(repo_text.split('/')) == 2 and not repo_text.startswith('http'):
            parts = repo_text.split('/')
            self.help_label.setText(
                f"✅ Format reconnu: {parts[0]}/{parts[1]}\n"
                f"L'URL complète sera: https://github.com/{parts[0]}/{parts[1]}"
            )
            self.help_label.setStyleSheet("""
                color: #22863a; 
                font-size: 11px; 
                padding: 8px; 
                background-color: #d4edda; 
                border-radius: 4px;
            """)
        else:
            self.help_label.setStyleSheet("""
                color: #57606a; 
                font-size: 11px; 
                padding: 8px; 
                background-color: #f6f8fa; 
                border-radius: 4px;
            """)
            self.help_label.setText(
                "ℹ️ Une fois connecté, vous pourrez:\n"
                "• Naviguer dans vos fichiers\n"
                "• Éditer des documents\n"
                "• Commiter vos modifications"
            )
    
    def validate_input(self):
        """Valider la saisie en temps réel"""
        repo = self.repo_input.text().strip()
        token = self.token_input.text().strip()
        
        is_valid = True
        
        if repo:
            if repo.startswith('https://github.com/') and '/' not in repo.replace('https://github.com/', ''):
                is_valid = False
            elif '/' in repo and not repo.startswith('http'):
                parts = repo.split('/')
                if len(parts) != 2:
                    is_valid = False
        else:
            is_valid = False
        
        button_box = self.findChild(QDialogButtonBox)
        if button_box:
            ok_button = button_box.button(QDialogButtonBox.Ok)
            if ok_button:
                ok_button.setEnabled(is_valid and len(token) > 10)
    
    def accept(self):
        """Valider la connexion"""
        repo = self.repo_input.text().strip()
        token = self.token_input.text().strip()
        
        if not repo or not token:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez remplir tous les champs")
            return
        
        if repo.startswith('https://github.com/') and '/' not in repo.replace('https://github.com/', ''):
            QMessageBox.warning(
                self,
                "⚠️ URL invalide",
                f"Vous avez entré un nom d'utilisateur, pas un dépôt.\n\n"
                f"Format correct: https://github.com/utilisateur/NOM_DU_DÉPÔT"
            )
            return
        
        if '/' in repo and not repo.startswith('http') and not repo.startswith('git@'):
            repo = f"https://github.com/{repo}"
        
        self.repo_input.setText(repo)
        super().accept()


class CommitDialog(QDialog):
    """Boîte de dialogue de commit"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📤 Commiter les modifications")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("📤 Commiter les modifications")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        desc = QLabel("Entrez un message descriptif pour ce commit")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #8b949e;")
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("💬 Message de commit:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Description des modifications...")
        self.message_input.setMaximumHeight(100)
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px;
                color: #c9d1d9;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #1f6feb;
            }
        """)
        layout.addWidget(self.message_input)
        
        suggestions = QLabel("💡 Suggestions: 'Mise à jour du document' ou 'Ajout du fichier X'")
        suggestions.setStyleSheet("color: #57606a; font-size: 10px;")
        suggestions.setWordWrap(True)
        layout.addWidget(suggestions)
        
        layout.addSpacing(10)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton[text="OK"] {
                background-color: #1f6feb;
                color: white;
            }
            QPushButton[text="OK"]:hover {
                background-color: #388bfd;
            }
            QPushButton[text="Cancel"] {
                background-color: #21262d;
                color: #c9d1d9;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #30363d;
            }
        """)
        layout.addWidget(button_box)
    
    def accept(self):
        message = self.message_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez entrer un message de commit")
            return
        super().accept()


class ErrorDialog(QDialog):
    """Boîte de dialogue d'erreur détaillée"""
    
    def __init__(self, error_message: str, parent=None, details: str = None):
        super().__init__(parent)
        self.setWindowTitle("❌ Erreur")
        self.setModal(True)
        self.setMinimumWidth(550)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("❌ Une erreur est survenue")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        error_label = QLabel(error_message)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("""
            color: #d73a49; 
            padding: 10px; 
            background-color: #ffeef0; 
            border-radius: 4px;
            font-weight: bold;
        """)
        layout.addWidget(error_label)
        
        if details:
            details_label = QLabel("🔍 Détails techniques:")
            details_label.setFont(QFont("Arial", 10, QFont.Bold))
            details_label.setStyleSheet("margin-top: 10px;")
            layout.addWidget(details_label)
            
            details_text = QTextBrowser()
            details_text.setPlainText(details)
            details_text.setMaximumHeight(150)
            details_text.setStyleSheet("""
                background-color: #f6f8fa; 
                border: 1px solid #d0d7de; 
                border-radius: 4px;
                padding: 5px;
                font-family: monospace;
                font-size: 11px;
            """)
            layout.addWidget(details_text)
        
        suggestions = QLabel(
            "💡 Suggestions:\n"
            "• Vérifiez votre connexion internet\n"
            "• Assurez-vous que le token est valide\n"
            "• Vérifiez que l'URL du dépôt est correcte"
        )
        suggestions.setWordWrap(True)
        suggestions.setStyleSheet("""
            color: #57606a; 
            font-size: 11px; 
            padding: 10px; 
            background-color: #f0f6fc; 
            border-radius: 4px;
            margin-top: 10px;
        """)
        layout.addWidget(suggestions)
        
        button_layout = QHBoxLayout()
        
        copy_button = QPushButton("📋 Copier l'erreur")
        copy_button.clicked.connect(lambda: self.copy_error(error_message, details))
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #30363d;
            }
        """)
        button_layout.addWidget(copy_button)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #1f6feb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388bfd;
            }
        """)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def copy_error(self, error_message: str, details: str = None):
        clipboard = QApplication.clipboard()
        text = f"Erreur: {error_message}\n"
        if details:
            text += f"\nDétails:\n{details}"
        clipboard.setText(text)
        QMessageBox.information(self, "📋 Copié", "L'erreur a été copiée dans le presse-papiers.")


class GPGPasswordDialog(QDialog):
    """Dialogue pour entrer le mot de passe GPG"""
    
    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Déchiffrement GPG")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        # Icône et titre
        title_layout = QHBoxLayout()
        icon_label = QLabel("🔐")
        icon_label.setStyleSheet("font-size: 32px;")
        title_layout.addWidget(icon_label)
        
        title_text = QLabel(f"Déchiffrer {filename}")
        title_text.setFont(QFont("Arial", 14, QFont.Bold))
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        layout.addSpacing(10)
        
        # Description
        desc = QLabel(
            f"Le fichier '{filename}' est chiffré avec GPG.\n"
            "Entrez le mot de passe pour le déchiffrer."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #8b949e; padding: 4px;")
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        # Mot de passe
        form_layout = QFormLayout()
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Entrez le mot de passe GPG...")
        self.password_input.setMinimumHeight(35)
        self.password_input.returnPressed.connect(self.accept)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px 12px;
                color: #c9d1d9;
                font-size: 14px;
                font-family: 'Courier New', monospace;
            }
            QLineEdit:focus {
                border-color: #1f6feb;
            }
        """)
        form_layout.addRow("🔑 Mot de passe:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Afficher le mot de passe
        self.show_password_check = QCheckBox("👁️ Afficher le mot de passe")
        self.show_password_check.stateChanged.connect(self.toggle_password_visibility)
        self.show_password_check.setStyleSheet("color: #8b949e;")
        layout.addWidget(self.show_password_check)
        
        layout.addSpacing(10)
        
        # Information sur le fichier
        info_label = QLabel("💡 Le fichier sera déchiffré temporairement pour l'édition")
        info_label.setStyleSheet("color: #57606a; font-size: 10px; padding: 8px; background-color: #161b22; border-radius: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.try_button = QPushButton("🔓 Déchiffrer")
        self.try_button.clicked.connect(self.accept)
        self.try_button.setDefault(True)
        self.try_button.setMinimumHeight(40)
        self.try_button.setStyleSheet("""
            QPushButton {
                background-color: #1f6feb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388bfd;
            }
        """)
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #30363d;
            }
        """)
        
        button_layout.addWidget(self.try_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Focus sur le champ mot de passe
        QTimer.singleShot(100, self.password_input.setFocus)
    
    def toggle_password_visibility(self, state):
        """Basculer la visibilité du mot de passe"""
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def get_password(self) -> str:
        """Obtenir le mot de passe saisi"""
        return self.password_input.text().strip()
    
    def accept(self):
        """Valider le dialogue"""
        password = self.get_password()
        if not password:
            QMessageBox.warning(
                self,
                "⚠️ Attention",
                "Veuillez entrer un mot de passe."
            )
            return
        
        super().accept()


class GPGEncryptDialog(QDialog):
    """Dialogue pour le chiffrement GPG"""
    
    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Chiffrement GPG")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🔐 Chiffrer le fichier")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        desc = QLabel(
            f"Le fichier '{filename}' sera chiffré avec GPG.\n"
            "Entrez un mot de passe pour le chiffrement."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #8b949e; padding: 4px;")
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        # Mot de passe
        form_layout = QFormLayout()
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Entrez un mot de passe...")
        self.password_input.setMinimumHeight(35)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px 12px;
                color: #c9d1d9;
                font-size: 14px;
                font-family: 'Courier New', monospace;
            }
            QLineEdit:focus {
                border-color: #1f6feb;
            }
        """)
        form_layout.addRow("🔑 Mot de passe:", self.password_input)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Confirmez le mot de passe...")
        self.confirm_input.setMinimumHeight(35)
        self.confirm_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px 12px;
                color: #c9d1d9;
                font-size: 14px;
                font-family: 'Courier New', monospace;
            }
            QLineEdit:focus {
                border-color: #1f6feb;
            }
        """)
        form_layout.addRow("✅ Confirmation:", self.confirm_input)
        
        layout.addLayout(form_layout)
        
        # Afficher le mot de passe
        self.show_password_check = QCheckBox("👁️ Afficher les mots de passe")
        self.show_password_check.stateChanged.connect(self.toggle_password_visibility)
        self.show_password_check.setStyleSheet("color: #8b949e;")
        layout.addWidget(self.show_password_check)
        
        layout.addSpacing(10)
        
        # Information sur le chiffrement
        info_label = QLabel(
            "🔒 Le fichier sera chiffré avec AES256 (chiffrement symétrique)\n"
            "⚠️ Conservez bien votre mot de passe !"
        )
        info_label.setStyleSheet("color: #57606a; font-size: 10px; padding: 8px; background-color: #161b22; border-radius: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.encrypt_button = QPushButton("🔒 Chiffrer")
        self.encrypt_button.clicked.connect(self.accept)
        self.encrypt_button.setDefault(True)
        self.encrypt_button.setMinimumHeight(40)
        self.encrypt_button.setStyleSheet("""
            QPushButton {
                background-color: #1f6feb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388bfd;
            }
        """)
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #30363d;
            }
        """)
        
        button_layout.addWidget(self.encrypt_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        QTimer.singleShot(100, self.password_input.setFocus)
    
    def toggle_password_visibility(self, state):
        """Basculer la visibilité des mots de passe"""
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.confirm_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setEchoMode(QLineEdit.Password)
    
    def get_password(self) -> str:
        """Obtenir le mot de passe"""
        return self.password_input.text().strip()
    
    def accept(self):
        """Valider le dialogue"""
        password = self.get_password()
        confirm = self.confirm_input.text().strip()
        
        if not password:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez entrer un mot de passe.")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "⚠️ Attention", "Les mots de passe ne correspondent pas.")
            return
        
        if len(password) < 4:
            QMessageBox.warning(self, "⚠️ Attention", "Le mot de passe doit faire au moins 4 caractères.")
            return
        
        super().accept()


class SelectFileFromArchiveDialog(QDialog):
    """Dialogue pour sélectionner un fichier dans une archive"""
    
    def __init__(self, archive_name: str, files: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"📦 Sélectionner un fichier - {archive_name}")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.files = files
        self.selected_file = None
        
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel(f"📦 Fichiers dans {archive_name}")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Double-cliquez sur un fichier pour l'ouvrir dans l'éditeur")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #8b949e;")
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        # Liste des fichiers
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #161b22;
            }
            QListWidget::item:selected {
                background-color: #1f6feb;
                color: #ffffff;
            }
        """)
        self.file_list.itemDoubleClicked.connect(self.select_file)
        
        # Ajouter les fichiers à la liste
        for filename, content in files:
            item = QListWidgetItem()
            size = len(content)
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            
            item.setText(f"📄 {filename} ({size_str})")
            item.setData(Qt.UserRole, filename)
            item.setData(Qt.UserRole + 1, content)
            self.file_list.addItem(item)
        
        layout.addWidget(self.file_list)
        
        # Informations
        info_label = QLabel(f"💡 {len(files)} fichier(s) dans l'archive")
        info_label.setStyleSheet("color: #57606a; font-size: 10px;")
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        open_button = QPushButton("📂 Ouvrir sélection")
        open_button.clicked.connect(self.open_selected)
        open_button.setDefault(True)
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #1f6feb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #388bfd;
            }
        """)
        button_layout.addWidget(open_button)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.reject)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #30363d;
            }
        """)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def open_selected(self):
        """Ouvrir le fichier sélectionné"""
        current_item = self.file_list.currentItem()
        if current_item:
            self.selected_file = {
                'filename': current_item.data(Qt.UserRole),
                'content': current_item.data(Qt.UserRole + 1)
            }
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "⚠️ Attention",
                "Veuillez sélectionner un fichier dans la liste."
            )
    
    def select_file(self, item):
        """Sélectionner un fichier par double-clic"""
        self.selected_file = {
            'filename': item.data(Qt.UserRole),
            'content': item.data(Qt.UserRole + 1)
        }
        self.accept()
    
    def get_selected_file(self):
        """Obtenir le fichier sélectionné"""
        return self.selected_file