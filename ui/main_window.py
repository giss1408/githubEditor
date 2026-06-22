# -*- coding: utf-8 -*-

"""
Fenêtre principale avec support GPG - Version complète
"""

import sys
import os
import re
import tempfile
import tarfile
import shutil
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTextEdit, QToolBar,
    QAction, QMessageBox, QStatusBar, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QProgressBar, QFileDialog, QApplication,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QTextBrowser, QFrame, QInputDialog, QMenu
)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QFont, QColor, QKeySequence, QPixmap, QPalette, QIcon

from .editor_widget import EditorWidget
from .dialogs import (
    LoginDialog, CommitDialog, ErrorDialog,
    GPGPasswordDialog, GPGEncryptDialog,
    SelectFileFromArchiveDialog
)
from utils.github_api import GitHubAPI, GitHubAPIError
from utils.file_manager import FileManager
from utils.gpg_handler import GPGHandler

# Styles modernes
MODERN_STYLES = """
QMainWindow {
    background-color: #0d1117;
}

QWidget {
    background-color: transparent;
    color: #c9d1d9;
}

QMenuBar {
    background-color: #161b22;
    color: #c9d1d9;
    border-bottom: 1px solid #30363d;
    padding: 5px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 5px 10px;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background-color: #21262d;
}

QToolBar {
    background-color: #161b22;
    border: none;
    border-bottom: 1px solid #30363d;
    spacing: 8px;
    padding: 8px 16px;
}

QToolBar QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    color: #c9d1d9;
    font-weight: 500;
}

QToolBar QToolButton:hover {
    background-color: #21262d;
}

QToolBar QToolButton:pressed {
    background-color: #30363d;
}

QTreeWidget {
    background-color: #0d1117;
    border: none;
    border-right: 1px solid #30363d;
    padding: 8px;
    outline: none;
}

QTreeWidget::item {
    padding: 8px 12px;
    border-radius: 6px;
    margin: 2px 0;
}

QTreeWidget::item:hover {
    background-color: #161b22;
}

QTreeWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

QTreeWidget::item:selected:hover {
    background-color: #1f6feb;
}

QTextEdit {
    background-color: #0d1117;
    border: none;
    color: #c9d1d9;
    font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
    font-size: 14px;
    line-height: 1.6;
    padding: 20px;
    selection-background-color: #1f6feb;
}

QTextEdit:focus {
    background-color: #0d1117;
}

QListWidget {
    background-color: #0d1117;
    border: none;
    border-left: 1px solid #30363d;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    padding: 12px 16px;
    border-radius: 6px;
    margin: 2px 0;
    background-color: transparent;
}

QListWidget::item:hover {
    background-color: #161b22;
}

QListWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

QPushButton {
    background-color: #1f6feb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #388bfd;
}

QPushButton:pressed {
    background-color: #1f6feb;
}

QPushButton:disabled {
    background-color: #21262d;
    color: #484f58;
}

QPushButton#secondaryBtn {
    background-color: #21262d;
    color: #c9d1d9;
}

QPushButton#secondaryBtn:hover {
    background-color: #30363d;
}

QPushButton#dangerBtn {
    background-color: #da3633;
}

QPushButton#dangerBtn:hover {
    background-color: #f85149;
}

QProgressBar {
    background-color: #161b22;
    border: none;
    border-radius: 4px;
    height: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 4px;
}

QScrollBar:vertical {
    background-color: #0d1117;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QLabel {
    color: #c9d1d9;
}

QLabel#title {
    font-size: 18px;
    font-weight: 700;
    color: #f0f6fc;
}

QLabel#subtitle {
    font-size: 13px;
    color: #8b949e;
}

QLabel#fileInfo {
    font-size: 14px;
    font-weight: 500;
    color: #f0f6fc;
}

QLabel#stats {
    font-size: 12px;
    color: #8b949e;
    font-family: 'Courier New', monospace;
}

QLabel#gpg_status {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
}

QStatusBar {
    background-color: #161b22;
    border-top: 1px solid #30363d;
    padding: 4px 16px;
}

QStatusBar QLabel {
    color: #8b949e;
    font-size: 12px;
}

QDialog {
    background-color: #0d1117;
}

QDialog QLabel {
    color: #c9d1d9;
}

QLineEdit, QTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px 12px;
    color: #c9d1d9;
    font-size: 14px;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #1f6feb;
}

QLineEdit::placeholder, QTextEdit::placeholder {
    color: #484f58;
}

QToolTip {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
}

QSplitter::handle {
    background-color: #30363d;
    width: 1px;
}

QSplitter::handle:hover {
    background-color: #484f58;
}
"""


class ModernCard(QFrame):
    """Widget carte moderne"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernCard")
        self.setStyleSheet("""
            QFrame#modernCard {
                background-color: #161b22;
                border-radius: 12px;
                border: 1px solid #30363d;
                padding: 16px;
            }
        """)
        self.card_layout = QVBoxLayout(self)
        self.card_layout.setContentsMargins(16, 16, 16, 16)
        self.card_layout.setSpacing(12)
        self.debug = True


class MainWindow(QMainWindow):
    """Fenêtre principale avec support GPG"""
    
    def __init__(self):
        super().__init__()
        
        # API et gestionnaires
        self.github_api = None
        self.file_manager = FileManager()
        self.gpg_handler = GPGHandler()

        self.debug = True
        
        # État de connexion
        self.is_connected = False
        self.connection_error = None
        self.current_token = None
        self.current_repo_url = None
        
        # Fichier courant
        self.current_file = None
        self.current_file_encrypted = False
        self.current_file_password = None
        self.current_file_sha = None
        
        # Attributs pour les archives TAR
        self.current_file_is_tar = False
        self.current_tar_files = []
        self.current_tar_temp_dir = None
        self.current_file_display_name = ""
        
        # Widgets UI
        self.progress_bar = None
        self.status_label = None
        self.connection_indicator = None
        self.file_tree = None
        self.editor = None
        self.history_list = None
        self.file_info_label = None
        self.file_size_label = None
        self.stats_label = None
        self.gpg_status_label = None
        self.btn_connect = None
        self.btn_save = None
        self.btn_commit = None
        self.btn_refresh = None
        self.btn_disconnect = None
        self.connection_status = None
        
        # Configuration de la fenêtre
        self.setWindowTitle("GitHub Doc Editor - GPG Support")
        self.setGeometry(100, 100, 1400, 850)
        self.setStyleSheet(MODERN_STYLES)
        
        # Initialisation
        self.init_ui()
        self.init_menu()
        
        # Connexion automatique après un court délai
        QTimer.singleShot(100, self.try_auto_connect)
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header()
        
        # Corps principal
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(2)
        content_layout.addWidget(main_splitter)
        
        # Panel gauche - Arborescence
        left_widget = self.create_file_tree_panel()
        main_splitter.addWidget(left_widget)
        
        # Panel central - Éditeur
        self.editor = EditorWidget()
        main_splitter.addWidget(self.editor)
        
        # Panel droit - Informations
        right_widget = self.create_info_panel()
        main_splitter.addWidget(right_widget)
        
        main_splitter.setSizes([280, 800, 320])
        
        main_layout.addWidget(content_widget)
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Créer un header moderne"""
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QWidget {
                background-color: #161b22;
                border-bottom: 1px solid #30363d;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(16)
        
        # Logo et titre
        logo_container = QHBoxLayout()
        logo_container.setSpacing(12)
        
        logo = QLabel("📄")
        logo.setStyleSheet("font-size: 28px;")
        logo_container.addWidget(logo)
        
        title_container = QVBoxLayout()
        title_container.setSpacing(2)
        
        title = QLabel("GitHub Doc Editor")
        title.setObjectName("title")
        title_container.addWidget(title)
        
        subtitle = QLabel("Éditeur de documents en ligne avec GPG")
        subtitle.setObjectName("subtitle")
        title_container.addWidget(subtitle)
        
        logo_container.addLayout(title_container)
        layout.addLayout(logo_container)
        
        layout.addStretch()
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        self.btn_connect = QPushButton("🔗 Connexion")
        self.btn_connect.clicked.connect(self.show_login_dialog)
        self.btn_connect.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(self.btn_connect)
        
        self.btn_save = QPushButton("💾 Sauvegarder")
        self.btn_save.clicked.connect(self.save_file)
        self.btn_save.setEnabled(False)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(self.btn_save)
        
        self.btn_commit = QPushButton("📤 Commiter")
        self.btn_commit.clicked.connect(self.commit_file)
        self.btn_commit.setEnabled(False)
        self.btn_commit.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(self.btn_commit)
        
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.clicked.connect(self.refresh_files)
        self.btn_refresh.setFixedSize(40, 40)
        self.btn_refresh.setToolTip("Rafraîchir")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(self.btn_refresh)
        
        self.btn_disconnect = QPushButton("🚪")
        self.btn_disconnect.clicked.connect(self.disconnect)
        self.btn_disconnect.setFixedSize(40, 40)
        self.btn_disconnect.setToolTip("Se déconnecter")
        self.btn_disconnect.setCursor(Qt.PointingHandCursor)
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setStyleSheet("""
            QPushButton {
                background-color: #da3633;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f85149;
            }
            QPushButton:disabled {
                background-color: #21262d;
                color: #484f58;
            }
        """)
        actions_layout.addWidget(self.btn_disconnect)
        
        layout.addLayout(actions_layout)
        
        # Status de connexion
        self.connection_status = QLabel("● Hors ligne")
        self.connection_status.setStyleSheet("""
            QLabel {
                color: #f85149;
                font-weight: 600;
                font-size: 12px;
                padding: 4px 12px;
                background-color: #1c1c1c;
                border-radius: 12px;
            }
        """)
        layout.addWidget(self.connection_status)
        
        # Ajouter le header au layout principal
        central_widget = self.centralWidget()
        if central_widget:
            central_widget.layout().insertWidget(0, header)
    
    def create_file_tree_panel(self):
        """Créer le panel d'arborescence"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(12)
        
        header = QLabel("📁 Fichiers")
        header.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 600;
                color: #8b949e;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        """)
        layout.addWidget(header)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setIndentation(12)
        self.file_tree.itemDoubleClicked.connect(self.on_file_double_clicked)
        layout.addWidget(self.file_tree)
        
        actions_container = QWidget()
        actions_container.setStyleSheet("""
            QWidget {
                background-color: #161b22;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(4, 4, 4, 4)
        actions_layout.setSpacing(6)
        
        btn_upload = QPushButton("📤 Upload")
        btn_upload.clicked.connect(self.upload_file)
        btn_upload.setMinimumHeight(36)
        btn_upload.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(btn_upload)
        
        btn_new_file = QPushButton("📄 Nouveau")
        btn_new_file.clicked.connect(self.create_new_file)
        btn_new_file.setMinimumHeight(36)
        btn_new_file.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(btn_new_file)
        
        layout.addWidget(actions_container)
        
        return panel
    
    def create_info_panel(self):
        """Créer le panel d'informations"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Fichier courant
        file_card = ModernCard()
        file_layout = file_card.card_layout
        
        file_header = QLabel("📄 Fichier courant")
        file_header.setStyleSheet("font-size: 12px; color: #8b949e; text-transform: uppercase; font-weight: 600;")
        file_layout.addWidget(file_header)
        
        self.file_info_label = QLabel("Aucun fichier ouvert")
        self.file_info_label.setObjectName("fileInfo")
        file_layout.addWidget(self.file_info_label)
        
        self.file_size_label = QLabel("")
        self.file_size_label.setObjectName("stats")
        file_layout.addWidget(self.file_size_label)
        
        self.gpg_status_label = QLabel("")
        self.gpg_status_label.setObjectName("gpg_status")
        file_layout.addWidget(self.gpg_status_label)
        
        layout.addWidget(file_card)
        
        # Statistiques
        stats_card = ModernCard()
        stats_layout = stats_card.card_layout
        
        stats_header = QLabel("📊 Statistiques")
        stats_header.setStyleSheet("font-size: 12px; color: #8b949e; text-transform: uppercase; font-weight: 600;")
        stats_layout.addWidget(stats_header)
        
        self.stats_label = QLabel("Lignes: 0\nMots: 0\nCaractères: 0")
        self.stats_label.setObjectName("stats")
        self.stats_label.setStyleSheet("font-family: 'Courier New', monospace; line-height: 1.6;")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_card)
        
        # Historique
        history_card = ModernCard()
        history_layout = history_card.card_layout
        
        history_header = QLabel("📜 Historique")
        history_header.setStyleSheet("font-size: 12px; color: #8b949e; text-transform: uppercase; font-weight: 600;")
        history_layout.addWidget(history_header)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                background-color: transparent;
                border-bottom: 1px solid #21262d;
            }
            QListWidget::item:hover {
                background-color: #161b22;
            }
        """)
        self.history_list.itemDoubleClicked.connect(self.show_commit_details)
        history_layout.addWidget(self.history_list)
        
        layout.addWidget(history_card)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #161b22;
                border: none;
                border-radius: 4px;
                height: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1f6feb;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        return panel
    
    def create_status_bar(self):
        """Créer une barre d'état"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("✅ Prêt")
        self.status_label.setStyleSheet("padding: 4px 8px;")
        self.status_bar.addWidget(self.status_label)
        
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setStyleSheet("color: #f85149; font-size: 12px; padding: 4px 8px;")
        self.status_bar.addPermanentWidget(self.connection_indicator)
        
        gpg_status = "🔐" if self.gpg_handler.gpg_available else "❌"
        gpg_label = QLabel(f"GPG: {gpg_status}")
        gpg_label.setStyleSheet("color: #484f58; padding: 4px 8px; font-size: 11px;")
        self.status_bar.addPermanentWidget(gpg_label)
        
        version_label = QLabel("v1.1.0")
        version_label.setStyleSheet("color: #484f58; padding: 4px 8px;")
        self.status_bar.addPermanentWidget(version_label)
    
    def init_menu(self):
        """Initialiser le menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("📁 Fichier")
        
        change_repo_action = QAction("🔄 Changer de dépôt", self)
        change_repo_action.triggered.connect(self.change_repository)
        change_repo_action.setShortcut("Ctrl+Shift+R")
        file_menu.addAction(change_repo_action)
        
        file_menu.addSeparator()
        
        disconnect_action = QAction("🚪 Se déconnecter", self)
        disconnect_action.triggered.connect(self.disconnect)
        disconnect_action.setShortcut("Ctrl+Shift+D")
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("❌ Quitter", self)
        quit_action.triggered.connect(self.close)
        quit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(quit_action)
        
        # Menu GPG
        gpg_menu = menubar.addMenu("🔐 GPG")
        
        check_gpg_action = QAction("🔍 Vérifier GPG", self)
        check_gpg_action.triggered.connect(self.check_gpg)
        gpg_menu.addAction(check_gpg_action)
        
        gpg_menu.addSeparator()
        
        encrypt_action = QAction("🔒 Chiffrer un fichier", self)
        encrypt_action.triggered.connect(self.encrypt_file_manual)
        encrypt_action.setShortcut("Ctrl+E")
        gpg_menu.addAction(encrypt_action)
        
        decrypt_action = QAction("🔓 Déchiffrer un fichier", self)
        decrypt_action.triggered.connect(self.decrypt_file_manual)
        decrypt_action.setShortcut("Ctrl+D")
        gpg_menu.addAction(decrypt_action)
        
        gpg_menu.addSeparator()
        
        create_archive_action = QAction("📦 Créer une archive chiffrée", self)
        create_archive_action.triggered.connect(self.create_encrypted_archive)
        gpg_menu.addAction(create_archive_action)
        
        extract_archive_action = QAction("📂 Extraire une archive chiffrée", self)
        extract_archive_action.triggered.connect(self.extract_encrypted_archive)
        gpg_menu.addAction(extract_archive_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("❓ Aide")
        
        quick_guide_action = QAction("📖 Guide rapide", self)
        quick_guide_action.triggered.connect(self.show_quick_guide)
        quick_guide_action.setShortcut("F1")
        help_menu.addAction(quick_guide_action)
        
        help_menu.addSeparator()
        
        gpg_help_action = QAction("🔐 Documentation GPG", self)
        gpg_help_action.triggered.connect(self.show_gpg_help)
        help_menu.addAction(gpg_help_action)
        
        shortcuts_action = QAction("⌨️ Raccourcis clavier", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("📖 À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    # === Méthodes de gestion de l'interface ===
    
    def update_connection_status(self, connected: bool, repo_url: str = ""):
        """Mettre à jour le statut de connexion"""
        if connected:
            self.connection_status.setText(f"● Connecté")
            self.connection_status.setStyleSheet("""
                QLabel {
                    color: #3fb950;
                    font-weight: 600;
                    font-size: 12px;
                    padding: 4px 12px;
                    background-color: #1c1c1c;
                    border-radius: 12px;
                }
            """)
            self.connection_indicator.setStyleSheet("color: #3fb950; font-size: 12px; padding: 4px 8px;")
            self.btn_connect.setText("🔗 Connecté")
            self.btn_connect.setEnabled(False)
            self.btn_save.setEnabled(True)
            self.btn_commit.setEnabled(True)
            self.btn_disconnect.setEnabled(True)
            self.btn_refresh.setEnabled(True)
        else:
            self.connection_status.setText("● Hors ligne")
            self.connection_status.setStyleSheet("""
                QLabel {
                    color: #f85149;
                    font-weight: 600;
                    font-size: 12px;
                    padding: 4px 12px;
                    background-color: #1c1c1c;
                    border-radius: 12px;
                }
            """)
            self.connection_indicator.setStyleSheet("color: #f85149; font-size: 12px; padding: 4px 8px;")
            self.btn_connect.setText("🔗 Connexion")
            self.btn_connect.setEnabled(True)
            self.btn_save.setEnabled(False)
            self.btn_commit.setEnabled(False)
            self.btn_disconnect.setEnabled(False)
            self.btn_refresh.setEnabled(False)
    
    def update_stats(self):
        """Mettre à jour les statistiques"""
        content = self.editor.get_content()
        lines = len(content.split('\n'))
        words = len(content.split()) if content.strip() else 0
        chars = len(content)
        
        self.stats_label.setText(f"Lignes: {lines}\nMots: {words}\nCaractères: {chars}")
    
    # === Méthodes de connexion ===
    
    def show_login_dialog(self):
        """Afficher la boîte de dialogue de connexion"""
        dialog = LoginDialog(self)
        dialog.setStyleSheet(MODERN_STYLES)
        
        settings = QSettings("GitHubEditor", "GitHubDocEditor")
        dialog.repo_input.setText(settings.value("repo_url", ""))
        dialog.token_input.setText(settings.value("token", ""))
        
        if dialog.exec_():
            token = dialog.token_input.text().strip()
            repo_url = dialog.repo_input.text().strip()
            
            repo_url = self._clean_repo_url(repo_url)
            if not repo_url:
                return
            
            self.connect_to_github(token, repo_url)
    
    def connect_to_github(self, token: str, repo_url: str):
        """Se connecter à GitHub"""
        try:
            if self.progress_bar:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
            self.status_label.setText("🔗 Connexion à GitHub...")
            QApplication.processEvents()
            
            self.github_api = GitHubAPI(token, repo_url)
            self.current_token = token
            self.current_repo_url = repo_url
            
            if self.progress_bar:
                self.progress_bar.setValue(30)
            
            success, message = self.github_api.test_connection()
            
            if self.progress_bar:
                self.progress_bar.setValue(70)
            
            if success:
                self.is_connected = True
                self.connection_error = None
                
                settings = QSettings("GitHubEditor", "GitHubDocEditor")
                settings.setValue("token", token)
                settings.setValue("repo_url", repo_url)
                
                self.update_connection_status(True, repo_url)
                self.status_label.setText(f"✅ Connecté à {repo_url}")
                
                self.refresh_files()
                self.load_history()
                
                if self.progress_bar:
                    self.progress_bar.setValue(100)
                
                QMessageBox.information(
                    self,
                    "✅ Connexion réussie",
                    f"Connecté avec succès à:\n\n"
                    f"📦 {self.github_api.owner}/{self.github_api.repo}\n"
                    f"👤 {self.github_api.owner}\n\n"
                    f"💡 Les fichiers .gpg seront automatiquement déchiffrés à l'ouverture."
                )
            else:
                raise GitHubAPIError(message)
            
        except GitHubAPIError as e:
            self.is_connected = False
            self.update_connection_status(False)
            self.status_label.setText("❌ Non connecté")
            
            error_msg = e.message
            if hasattr(e, 'suggestion') and e.suggestion:
                error_msg += f"\n\n💡 Suggestion:\n{e.suggestion}"
            
            QMessageBox.critical(self, "❌ Erreur de connexion", error_msg)
            
        except Exception as e:
            self.is_connected = False
            self.update_connection_status(False)
            self.status_label.setText("❌ Non connecté")
            
            QMessageBox.critical(
                self,
                "❌ Erreur inattendue",
                f"Une erreur s'est produite:\n\n{str(e)}"
            )
            
        finally:
            if self.progress_bar:
                self.progress_bar.setVisible(False)
    
    def disconnect(self):
        """Se déconnecter de GitHub"""
        if not self.is_connected:
            return
        
        reply = QMessageBox.question(
            self,
            "🚪 Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?\n\n"
            "Les modifications non commitées seront perdues.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Nettoyer les fichiers temporaires
            if hasattr(self, 'gpg_handler'):
                self.gpg_handler.cleanup()
            
            # Réinitialiser les attributs
            self.is_connected = False
            self.github_api = None
            self.current_token = None
            self.current_repo_url = None
            self.current_file = None
            self.current_file_encrypted = False
            self.current_file_password = None
            self.current_file_sha = None
            self.current_file_is_tar = False
            self.current_tar_files = []
            self.current_tar_temp_dir = None
            
            # Vider l'éditeur
            if self.editor:
                self.editor.clear()
            
            # Vider l'arbre des fichiers
            if self.file_tree:
                self.file_tree.clear()
            
            # Vider l'historique
            if self.history_list:
                self.history_list.clear()
            
            # Mettre à jour les labels
            if self.file_info_label:
                self.file_info_label.setText("Aucun fichier ouvert")
            if self.file_size_label:
                self.file_size_label.setText("")
            if self.stats_label:
                self.stats_label.setText("Lignes: 0\nMots: 0\nCaractères: 0")
            if self.gpg_status_label:
                self.gpg_status_label.setText("")
            
            # Mettre à jour le statut
            self.update_connection_status(False)
            self.status_label.setText("✅ Déconnecté")
            
            # Effacer les identifiants sauvegardés
            settings = QSettings("GitHubEditor", "GitHubDocEditor")
            settings.remove("token")
            settings.remove("repo_url")
            
            QMessageBox.information(
                self,
                "✅ Déconnexion réussie",
                "Vous avez été déconnecté avec succès."
            )
    
    def change_repository(self):
        """Changer de dépôt"""
        if not self.is_connected:
            QMessageBox.warning(
                self,
                "⚠️ Attention",
                "Vous n'êtes pas connecté.\n\n"
                "Cliquez sur 'Connexion' pour vous connecter."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "🔄 Changer de dépôt",
            "Voulez-vous vraiment changer de dépôt ?\n\n"
            "Les modifications non commitées seront perdues.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.disconnect()
            self.show_login_dialog()
    
    # === Méthodes de gestion des fichiers ===
    
    def refresh_files(self):
        """Rafraîchir la liste des fichiers"""
        if not self.is_connected or not self.github_api:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez vous connecter d'abord.")
            return
        
        try:
            if self.progress_bar:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
            self.status_label.setText("📂 Chargement des fichiers...")
            QApplication.processEvents()
            
            files = self.github_api.get_files()
            
            if self.progress_bar:
                self.progress_bar.setValue(50)
            
            self.file_tree.clear()
            
            if files:
                files.sort(key=lambda x: x['name'].lower())
                
                for file in files:
                    is_gpg = self.gpg_handler.is_gpg_file(file['name'])
                    is_tar = self.gpg_handler.is_tar_gpg(file['name'])
                    
                    if is_tar:
                        icon = "📦 "
                    elif is_gpg:
                        icon = "🔐 "
                    else:
                        icon = "📄 "
                    
                    item = QTreeWidgetItem(self.file_tree)
                    item.setText(0, f"{icon}{file['name']}")
                    item.setData(0, Qt.UserRole, file['path'])
                    item.setData(0, Qt.UserRole + 1, file['sha'])
                    item.setData(0, Qt.UserRole + 2, is_gpg)
                    
                    if is_tar:
                        item.setToolTip(0, f"📦 Archive chiffrée\n📂 {file['path']}")
                    elif is_gpg:
                        item.setToolTip(0, f"🔐 Fichier chiffré GPG\n📂 {file['path']}")
                    else:
                        item.setToolTip(0, f"📄 {file['name']}\n📂 {file['path']}")
                
                self.status_label.setText(f"✅ {len(files)} fichiers chargés")
            else:
                item = QTreeWidgetItem(self.file_tree)
                item.setText(0, "ℹ️ Aucun fichier")
                item.setFlags(Qt.NoItemFlags)
                self.status_label.setText("ℹ️ Aucun fichier trouvé")
            
            if self.progress_bar:
                self.progress_bar.setValue(100)
            
        except Exception as e:
            self.status_label.setText("❌ Erreur de chargement")
            QMessageBox.critical(self, "❌ Erreur", f"Erreur:\n\n{str(e)}")
            
        finally:
            if self.progress_bar:
                self.progress_bar.setVisible(False)
    
    def load_file(self, file_path: str):
        """Charger un fichier avec support GPG - Version corrigée"""
        if not self.is_connected or not self.github_api:
            return
        
        try:
            if self.progress_bar:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
            self.status_label.setText(f"📥 Chargement de {file_path}...")
            QApplication.processEvents()
            
            content_bytes, sha = self.github_api.get_file_content_binary(file_path)
            
            if self.progress_bar:
                self.progress_bar.setValue(50)
            
            is_gpg = self.gpg_handler.is_gpg_file(file_path)
            is_rg_gpg = self.gpg_handler.is_rg_gpg(file_path)
            is_tar_gpg = self.gpg_handler.is_tar_gpg(file_path)
            
            # Initialiser les variables
            content = ""
            is_archive = False
            files_content = []
            password = ""
            
            if is_gpg:
                dialog = GPGPasswordDialog(file_path, self)
                dialog.setStyleSheet(MODERN_STYLES)
                
                if dialog.exec_():
                    password = dialog.get_password()
                    
                    if self.progress_bar:
                        self.progress_bar.setValue(60)
                    
                    try:
                        # Cas spécifique: fichier .rg.gpg
                        if is_rg_gpg or is_tar_gpg:
                            if self.debug:
                                print(f"📦 Traitement du fichier .rg.gpg: {file_path}")
                            
                            files_content = self.gpg_handler.decrypt_rg_gpg(content_bytes, password)
                            
                            if self.progress_bar:
                                self.progress_bar.setValue(80)
                            
                            if files_content:
                                is_archive = True
                                self.current_file_password = password
                                self.current_file_encrypted = True
                                self.current_file_is_tar = True
                                self.current_tar_files = files_content
                                self.current_file = file_path
                                self.current_file_sha = sha
                                
                                # Afficher la boîte de sélection
                                select_dialog = SelectFileFromArchiveDialog(file_path, files_content, self)
                                select_dialog.setStyleSheet(MODERN_STYLES)
                                
                                if select_dialog.exec_():
                                    selected = select_dialog.get_selected_file()
                                    if selected:
                                        filename = selected['filename']
                                        content = selected['content']
                                        self.current_file_display_name = filename
                                        
                                        # Ne pas essayer de décoder, c'est déjà du texte
                                        self.editor.set_content(content)
                                        self.editor.set_file_path(f"{file_path} → {filename}")
                                        self.editor.set_sha(sha)
                                        self.editor.set_modified(False)
                                        
                                        self.file_info_label.setText(f"📄 {filename}")
                                        self.gpg_status_label.setText(f"🔐 {len(files_content)} fichier(s) dans l'archive")
                                        self.gpg_status_label.setStyleSheet("""
                                            QLabel {
                                                color: #3fb950;
                                                font-size: 11px;
                                                padding: 4px 8px;
                                                background-color: #1c1c1c;
                                                border-radius: 4px;
                                            }
                                        """)
                                        
                                        size = len(content)
                                        if size < 1024:
                                            size_str = f"{size} B"
                                        elif size < 1024 * 1024:
                                            size_str = f"{size/1024:.1f} KB"
                                        else:
                                            size_str = f"{size/(1024*1024):.1f} MB"
                                        self.file_size_label.setText(f"Taille: {size_str}")
                                        
                                        self.update_stats()
                                        if self.progress_bar:
                                            self.progress_bar.setValue(100)
                                        self.status_label.setText(f"✅ Fichier ouvert: {filename}")
                                        return
                                    else:
                                        if self.progress_bar:
                                            self.progress_bar.setVisible(False)
                                        return
                                else:
                                    if self.progress_bar:
                                        self.progress_bar.setVisible(False)
                                    return
                            else:
                                raise Exception("Aucun fichier trouvé dans l'archive")
                        
                        # Cas: .gpg simple (fichier texte)
                        else:
                            decrypted_bytes = self.gpg_handler.decrypt_file_binary(content_bytes, password)
                            
                            if self.progress_bar:
                                self.progress_bar.setValue(80)
                            
                            if decrypted_bytes is not None:
                                try:
                                    content = decrypted_bytes.decode('utf-8')
                                    self.current_file_password = password
                                    self.current_file_encrypted = True
                                    self.current_file_is_tar = False
                                    is_archive = False
                                except UnicodeDecodeError:
                                    QMessageBox.warning(
                                        self,
                                        "⚠️ Fichier binaire",
                                        f"Le fichier '{file_path}' est un fichier binaire.\n\n"
                                        f"Si c'est une archive .rg.gpg, elle devrait être ouverte automatiquement."
                                    )
                                    if self.progress_bar:
                                        self.progress_bar.setVisible(False)
                                    return
                            else:
                                raise Exception("Échec du déchiffrement")
                        
                    except Exception as e:
                        error_msg = str(e)
                        QMessageBox.critical(
                            self,
                            "❌ Erreur de déchiffrement",
                            f"Impossible de déchiffrer le fichier:\n\n{error_msg}\n\n"
                            f"Pour les fichiers .rg.gpg, assurez-vous que:\n"
                            f"• Le mot de passe est correct\n"
                            f"• Le fichier est une archive tar.gz chiffrée valide\n"
                            f"• Le fichier n'est pas corrompu\n\n"
                            f"Pour déchiffrer manuellement:\n"
                            f"gpg {file_path} && tar xzf {file_path.replace('.gpg', '')}"
                        )
                        if self.progress_bar:
                            self.progress_bar.setVisible(False)
                        return
                else:
                    if self.progress_bar:
                        self.progress_bar.setVisible(False)
                    return
            else:
                # Fichier normal - s'assurer que c'est du texte
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    QMessageBox.warning(
                        self,
                        "⚠️ Fichier binaire",
                        f"Le fichier '{file_path}' est un fichier binaire et ne peut pas être affiché."
                    )
                    if self.progress_bar:
                        self.progress_bar.setVisible(False)
                    return
            
            # Pour les fichiers normaux (non GPG) ou les fichiers GPG simples
            if not is_archive:
                self.current_file = file_path
                self.current_file_is_tar = False
                self.editor.set_content(content)
                self.editor.set_file_path(file_path)
                self.editor.set_sha(sha)
                self.editor.set_modified(False)
                
                self.file_info_label.setText(file_path)
                size = len(content)
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                self.file_size_label.setText(f"Taille: {size_str}")
                
                if is_gpg:
                    self.gpg_status_label.setText("🔐 Fichier déchiffré (GPG)")
                    self.gpg_status_label.setStyleSheet("""
                        QLabel {
                            color: #3fb950;
                            font-size: 11px;
                            padding: 4px 8px;
                            background-color: #1c1c1c;
                            border-radius: 4px;
                        }
                    """)
                else:
                    self.gpg_status_label.setText("📄 Fichier non chiffré")
                    self.gpg_status_label.setStyleSheet("""
                        QLabel {
                            color: #8b949e;
                            font-size: 11px;
                            padding: 4px 8px;
                            background-color: #1c1c1c;
                            border-radius: 4px;
                        }
                    """)
                
                self.update_stats()
                
                if self.progress_bar:
                    self.progress_bar.setValue(100)
                self.status_label.setText(f"✅ Fichier chargé: {file_path}")
            
        except Exception as e:
            self.status_label.setText("❌ Erreur de chargement")
            QMessageBox.critical(self, "❌ Erreur", f"Erreur:\n\n{str(e)}")
            
        finally:
            if self.progress_bar:
                self.progress_bar.setVisible(False)
    
    def save_file(self):
        """Sauvegarder le fichier localement"""
        if not self.current_file:
            QMessageBox.warning(self, "⚠️ Attention", "Aucun fichier ouvert.")
            return
        
        content = self.editor.get_content()
        self.editor.set_content(content)
        self.editor.set_modified(False)
        self.update_stats()
        
        self.status_label.setText(f"💾 Fichier sauvegardé: {self.current_file}")
        QMessageBox.information(self, "✅ Succès", "Fichier sauvegardé localement")
    
    def commit_file(self):
        """Commiter le fichier avec support .rg.gpg"""
        if not self.current_file:
            QMessageBox.warning(self, "⚠️ Attention", "Aucun fichier à commiter.")
            return
        
        if not self.is_connected or not self.github_api:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez vous connecter d'abord.")
            return
        
        dialog = CommitDialog(self)
        dialog.setStyleSheet(MODERN_STYLES)
        
        if dialog.exec_():
            commit_message = dialog.message_input.toPlainText().strip()
            if not commit_message:
                QMessageBox.warning(self, "⚠️ Attention", "Veuillez entrer un message de commit")
                return
            
            try:
                if self.progress_bar:
                    self.progress_bar.setVisible(True)
                    self.progress_bar.setValue(0)
                self.status_label.setText("📤 Commit en cours...")
                QApplication.processEvents()
                
                # Récupérer le contenu actuel de l'éditeur
                current_content = self.editor.get_content()
                sha = self.editor.get_sha()
                
                if self.progress_bar:
                    self.progress_bar.setValue(30)
                
                # Si c'est une archive .rg.gpg
                if self.current_file_is_tar:
                    if self.progress_bar:
                        self.progress_bar.setValue(50)
                    
                    # Mettre à jour le fichier dans l'archive
                    current_filename = self.file_info_label.text()
                    # Enlever le préfixe "📄 " si présent
                    if current_filename.startswith("📄 "):
                        current_filename = current_filename[2:]
                    
                    # Enlever le préfixe du chemin si présent
                    if " → " in current_filename:
                        current_filename = current_filename.split(" → ")[-1]
                    
                    if self.debug:
                        print(f"📝 Mise à jour du fichier: {current_filename}")
                    
                    updated = False
                    for i, (fname, fcontent) in enumerate(self.current_tar_files):
                        if fname == current_filename:
                            self.current_tar_files[i] = (fname, current_content)
                            updated = True
                            if self.debug:
                                print(f"   ✅ Fichier mis à jour: {fname}")
                            break
                    
                    if not updated:
                        # Si le fichier n'est pas trouvé, l'ajouter
                        self.current_tar_files.append((current_filename, current_content))
                        if self.debug:
                            print(f"   ✅ Nouveau fichier ajouté: {current_filename}")
                    
                    if self.progress_bar:
                        self.progress_bar.setValue(60)
                    
                    # Recompresser et rechiffrer en .rg.gpg
                    if self.debug:
                        print(f"🔒 Recompression et rechiffrement de l'archive...")
                    
                    encrypted_content = self.gpg_handler.encrypt_rg_gpg(
                        self.current_tar_files,
                        self.current_file_password
                    )
                    
                    # Convertir en string pour l'upload
                    content_to_commit = encrypted_content.decode('latin-1')
                    
                    if self.progress_bar:
                        self.progress_bar.setValue(70)
                
                # Si le fichier est un simple .gpg chiffré
                elif self.current_file_encrypted:
                    if self.progress_bar:
                        self.progress_bar.setValue(50)
                    
                    reply = QMessageBox.question(
                        self,
                        "🔐 Rechiffrer le fichier",
                        "Voulez-vous rechiffrer le fichier avec le même mot de passe ?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        password = self.current_file_password
                    else:
                        encrypt_dialog = GPGEncryptDialog(self.current_file, self)
                        encrypt_dialog.setStyleSheet(MODERN_STYLES)
                        if encrypt_dialog.exec_():
                            password = encrypt_dialog.get_password()
                            self.current_file_password = password
                        else:
                            raise Exception("Chiffrement annulé")
                    
                    if not password:
                        raise Exception("Mot de passe requis")
                    
                    encrypted_content = self.gpg_handler.encrypt_file(current_content, password)
                    content_to_commit = encrypted_content.decode('latin-1')
                    
                    if self.progress_bar:
                        self.progress_bar.setValue(70)
                
                else:
                    # Fichier normal non chiffré
                    content_to_commit = current_content
                
                # Commiter le fichier
                if self.debug:
                    print(f"📤 Commit du fichier: {self.current_file}")
                    print(f"📊 Taille du contenu: {len(content_to_commit)} caractères")
                
                result = self.github_api.commit_file(
                    self.current_file,
                    content_to_commit,
                    commit_message,
                    sha
                )
                
                if self.progress_bar:
                    self.progress_bar.setValue(90)
                
                if result:
                    self.editor.set_modified(False)
                    self.status_label.setText(f"✅ Commit réussi: {self.current_file}")
                    self.load_history()
                    self.refresh_files()
                    
                    # Nettoyer les fichiers temporaires
                    self.gpg_handler.cleanup()
                    
                    QMessageBox.information(
                        self,
                        "✅ Succès",
                        f"Fichier commit avec succès!\n\n"
                        f"📝 {self.current_file}\n"
                        f"💬 {commit_message}\n"
                        f"🔐 {'Archive .rg.gpg' if self.current_file_is_tar else 'Chiffré' if self.current_file_encrypted else 'Non chiffré'}"
                    )
                else:
                    QMessageBox.warning(self, "❌ Erreur", "Échec du commit")
                
                if self.progress_bar:
                    self.progress_bar.setValue(100)
                
            except Exception as e:
                self.status_label.setText("❌ Erreur de commit")
                QMessageBox.critical(self, "❌ Erreur", f"Erreur:\n\n{str(e)}")
                
            finally:
                if self.progress_bar:
                    self.progress_bar.setVisible(False)
    
    def on_file_double_clicked(self, item, column):
        """Ouvrir un fichier par double-clic"""
        file_path = item.data(0, Qt.UserRole)
        if file_path:
            self.load_file(file_path)
    
    def upload_file(self):
        """Télécharger un fichier"""
        if not self.is_connected or not self.github_api:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez vous connecter d'abord.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "📤 Sélectionner un fichier",
            "",
            "Tous les fichiers (*.*)"
        )
        
        if file_path:
            try:
                if self.progress_bar:
                    self.progress_bar.setVisible(True)
                    self.progress_bar.setValue(0)
                self.status_label.setText("📤 Téléchargement en cours...")
                QApplication.processEvents()
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                if self.progress_bar:
                    self.progress_bar.setValue(30)
                
                file_name = os.path.basename(file_path)
                try:
                    content_str = content.decode('utf-8')
                except UnicodeDecodeError:
                    content_str = content.decode('latin-1')
                
                result = self.github_api.upload_file(file_name, content_str)
                
                if self.progress_bar:
                    self.progress_bar.setValue(100)
                
                if result:
                    self.status_label.setText(f"✅ Fichier téléchargé: {file_name}")
                    QMessageBox.information(self, "✅ Succès", f"Fichier téléchargé!")
                    self.refresh_files()
                else:
                    QMessageBox.warning(self, "❌ Erreur", "Échec du téléchargement")
                
            except Exception as e:
                QMessageBox.critical(self, "❌ Erreur", f"Erreur:\n\n{str(e)}")
            finally:
                if self.progress_bar:
                    self.progress_bar.setVisible(False)
    
    def create_new_file(self):
        """Créer un nouveau fichier avec option GPG"""
        if not self.is_connected or not self.github_api:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez vous connecter d'abord.")
            return
        
        file_name, ok = QInputDialog.getText(self, "📄 Nouveau fichier", "Nom du fichier:")
        if ok and file_name:
            try:
                encrypt = QMessageBox.question(
                    self,
                    "🔐 Chiffrer le fichier ?",
                    f"Voulez-vous chiffrer le fichier '{file_name}' avec GPG ?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                content = ""
                
                if encrypt == QMessageBox.Yes:
                    if not self.gpg_handler.gpg_available:
                        QMessageBox.warning(self, "⚠️ Attention", "GPG n'est pas installé.")
                        return
                    
                    dialog = GPGEncryptDialog(file_name, self)
                    dialog.setStyleSheet(MODERN_STYLES)
                    
                    if dialog.exec_():
                        password = dialog.get_password()
                        encrypted_content = self.gpg_handler.encrypt_file("", password)
                        content = encrypted_content.decode('latin-1')
                        file_name = f"{file_name}.gpg"
                    else:
                        return
                
                result = self.github_api.upload_file(file_name, content, f"Création de {file_name}")
                
                if result:
                    self.status_label.setText(f"✅ Fichier créé: {file_name}")
                    self.refresh_files()
                    QMessageBox.information(self, "✅ Succès", f"Fichier {file_name} créé!")
                else:
                    QMessageBox.warning(self, "❌ Erreur", "Échec de la création")
                
            except Exception as e:
                QMessageBox.critical(self, "❌ Erreur", f"Erreur:\n\n{str(e)}")
    
    def load_history(self):
        """Charger l'historique des commits"""
        if not self.is_connected or not self.github_api:
            return
        
        try:
            commits = self.github_api.get_commits()
            self.history_list.clear()
            
            if commits:
                for commit in commits[:20]:
                    item = QListWidgetItem()
                    date = commit['date'][:10] if len(commit['date']) > 10 else commit['date']
                    item.setText(f"🔖 {commit['sha'][:7]} - {commit['message'][:40]}")
                    item.setToolTip(f"Auteur: {commit['author']}\nDate: {date}\nMessage: {commit['message']}")
                    item.setData(Qt.UserRole, commit)
                    self.history_list.addItem(item)
            else:
                item = QListWidgetItem("ℹ️ Aucun commit")
                self.history_list.addItem(item)
            
        except Exception as e:
            print(f"Erreur historique: {str(e)}")
    
    def show_commit_details(self, item):
        """Afficher les détails d'un commit"""
        commit = item.data(Qt.UserRole)
        if commit:
            details = f"""
            📌 Détails du commit
            
            🔖 SHA: {commit['sha']}
            👤 Auteur: {commit['author']}
            📅 Date: {commit['date']}
            💬 Message: {commit['message']}
            """
            QMessageBox.information(self, "📋 Détails du commit", details)
    
    # === Méthodes GPG ===
    
    def check_gpg(self):
        """Vérifier l'installation de GPG"""
        if self.gpg_handler.gpg_available:
            QMessageBox.information(
                self,
                "✅ GPG disponible",
                "GPG est installé et disponible.\n\n"
                "Vous pouvez déchiffrer et chiffrer des fichiers .gpg"
            )
        else:
            QMessageBox.warning(
                self,
                "❌ GPG non trouvé",
                "GPG n'est pas installé.\n\n"
                "Installez GPG avec:\n"
                "• macOS: brew install gnupg\n"
                "• Ubuntu: sudo apt-get install gnupg\n"
                "• Windows: https://www.gnupg.org/download/"
            )
    
    def encrypt_file_manual(self):
        """Chiffrer manuellement un fichier"""
        if not self.is_connected or not self.github_api:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez vous connecter d'abord.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "🔒 Sélectionner un fichier à chiffrer",
            "",
            "Tous les fichiers (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                dialog = GPGEncryptDialog(os.path.basename(file_path), self)
                dialog.setStyleSheet(MODERN_STYLES)
                
                if dialog.exec_():
                    password = dialog.get_password()
                    encrypted_content = self.gpg_handler.encrypt_file(content, password)
                    
                    file_name = os.path.basename(file_path)
                    gpg_file_name = f"{file_name}.gpg"
                    
                    result = self.github_api.upload_file(
                        gpg_file_name,
                        encrypted_content.decode('latin-1'),
                        f"Chiffrement de {file_name}"
                    )
                    
                    if result:
                        self.status_label.setText(f"✅ Fichier chiffré: {gpg_file_name}")
                        self.refresh_files()
                        QMessageBox.information(self, "✅ Succès", f"Fichier chiffré avec succès!\n\n🔐 {gpg_file_name}")
                    else:
                        QMessageBox.warning(self, "❌ Erreur", "Échec du chiffrement")
                
            except Exception as e:
                QMessageBox.critical(self, "❌ Erreur", f"Erreur:\n\n{str(e)}")
    
    def decrypt_file_manual(self):
        """Déchiffrer manuellement un fichier"""
        if not self.is_connected or not self.github_api:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez vous connecter d'abord.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "🔓 Sélectionner un fichier à déchiffrer",
            "",
            "Fichiers GPG (*.gpg *.asc)"
        )
        
        if file_path and (file_path.endswith('.gpg') or file_path.endswith('.asc')):
            try:
                with open(file_path, 'rb') as f:
                    encrypted_content = f.read()
                
                dialog = GPGPasswordDialog(os.path.basename(file_path), self)
                dialog.setStyleSheet(MODERN_STYLES)
                
                if dialog.exec_():
                    password = dialog.get_password()
                    decrypted_bytes = self.gpg_handler.decrypt_file_binary(encrypted_content, password)
                    
                    if decrypted_bytes:
                        try:
                            decrypted_text = decrypted_bytes.decode('utf-8')
                            save_path, _ = QFileDialog.getSaveFileName(
                                self,
                                "💾 Sauvegarder le fichier déchiffré",
                                file_path[:-4] if file_path.endswith('.gpg') else file_path[:-4],
                                "Tous les fichiers (*.*)"
                            )
                            if save_path:
                                with open(save_path, 'w', encoding='utf-8') as f:
                                    f.write(decrypted_text)
                                QMessageBox.information(self, "✅ Succès", f"Fichier déchiffré avec succès!\n\n📄 {save_path}")
                        except UnicodeDecodeError:
                            save_path, _ = QFileDialog.getSaveFileName(
                                self,
                                "💾 Sauvegarder le fichier déchiffré",
                                file_path[:-4],
                                "Tous les fichiers (*.*)"
                            )
                            if save_path:
                                with open(save_path, 'wb') as f:
                                    f.write(decrypted_bytes)
                                QMessageBox.information(self, "✅ Succès", f"Fichier binaire déchiffré avec succès!\n\n📄 {save_path}")
                    
            except Exception as e:
                QMessageBox.critical(self, "❌ Erreur", f"Erreur:\n\n{str(e)}")
    
    def create_encrypted_archive(self):
        """Créer une archive chiffrée"""
        if not self.is_connected or not self.github_api:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez vous connecter d'abord.")
            return
        
        if not self.gpg_handler.gpg_available:
            QMessageBox.warning(self, "⚠️ Attention", "GPG n'est pas installé.")
            return
        
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "📁 Sélectionner un dossier à archiver",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not folder_path:
            return
        
        archive_name, ok = QInputDialog.getText(
            self,
            "📦 Nom de l'archive",
            "Entrez le nom de l'archive (sans extension):",
            QLineEdit.Normal,
            os.path.basename(folder_path)
        )
        
        if not ok or not archive_name:
            return
        
        try:
            if self.progress_bar:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
            self.status_label.setText("📦 Création de l'archive...")
            QApplication.processEvents()
            
            temp_dir = tempfile.mkdtemp()
            tar_path = os.path.join(temp_dir, f"{archive_name}.tar")
            
            if self.progress_bar:
                self.progress_bar.setValue(20)
            
            with tarfile.open(tar_path, 'w:gz') as tar:
                tar.add(folder_path, arcname=os.path.basename(folder_path))
            
            if self.progress_bar:
                self.progress_bar.setValue(40)
            
            with open(tar_path, 'rb') as f:
                tar_content = f.read()
            
            if self.progress_bar:
                self.progress_bar.setValue(60)
            
            encrypt_dialog = GPGEncryptDialog(f"{archive_name}.tar", self)
            encrypt_dialog.setStyleSheet(MODERN_STYLES)
            
            if encrypt_dialog.exec_():
                password = encrypt_dialog.get_password()
                
                if self.progress_bar:
                    self.progress_bar.setValue(70)
                
                encrypted_content = self.gpg_handler.encrypt_file(tar_content, password)
                
                if self.progress_bar:
                    self.progress_bar.setValue(80)
                
                gpg_filename = f"{archive_name}.tar.gpg"
                result = self.github_api.upload_file(
                    gpg_filename,
                    encrypted_content.decode('latin-1'),
                    f"Ajout de l'archive {gpg_filename}"
                )
                
                if self.progress_bar:
                    self.progress_bar.setValue(100)
                
                if result:
                    self.status_label.setText(f"✅ Archive créée: {gpg_filename}")
                    self.refresh_files()
                    QMessageBox.information(
                        self,
                        "✅ Succès",
                        f"Archive chiffrée créée avec succès!\n\n"
                        f"📦 {gpg_filename}\n"
                        f"📂 Contenu: {os.path.basename(folder_path)}"
                    )
                else:
                    QMessageBox.warning(self, "❌ Erreur", "Échec de l'upload")
            
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Erreur:\n\n{str(e)}")
        finally:
            if self.progress_bar:
                self.progress_bar.setVisible(False)
    
    def extract_encrypted_archive(self):
        """Extraire une archive chiffrée"""
        if not self.is_connected or not self.github_api:
            QMessageBox.warning(self, "⚠️ Attention", "Veuillez vous connecter d'abord.")
            return
        
        if not self.gpg_handler.gpg_available:
            QMessageBox.warning(self, "⚠️ Attention", "GPG n'est pas installé.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "🔓 Sélectionner une archive à extraire",
            "",
            "Archives GPG (*.tar.gpg *.rg.gpg *.tgz.gpg)"
        )
        
        if not file_path:
            return
        
        try:
            if self.progress_bar:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
            self.status_label.setText("🔓 Extraction de l'archive...")
            QApplication.processEvents()
            
            with open(file_path, 'rb') as f:
                encrypted_content = f.read()
            
            if self.progress_bar:
                self.progress_bar.setValue(20)
            
            dialog = GPGPasswordDialog(os.path.basename(file_path), self)
            dialog.setStyleSheet(MODERN_STYLES)
            
            if dialog.exec_():
                password = dialog.get_password()
                
                if self.progress_bar:
                    self.progress_bar.setValue(40)
                
                files_content = self.gpg_handler.decrypt_tar_gpg(encrypted_content, password)
                
                if self.progress_bar:
                    self.progress_bar.setValue(70)
                
                if files_content:
                    extract_dir = QFileDialog.getExistingDirectory(
                        self,
                        "📂 Sélectionner le dossier de destination",
                        "",
                        QFileDialog.ShowDirsOnly
                    )
                    
                    if extract_dir:
                        for filename, content in files_content:
                            file_path_out = os.path.join(extract_dir, filename)
                            os.makedirs(os.path.dirname(file_path_out), exist_ok=True)
                            
                            try:
                                with open(file_path_out, 'w', encoding='utf-8') as f:
                                    f.write(content)
                            except:
                                with open(file_path_out, 'wb') as f:
                                    f.write(content.encode('latin-1'))
                        
                        if self.progress_bar:
                            self.progress_bar.setValue(100)
                        
                        QMessageBox.information(
                            self,
                            "✅ Succès",
                            f"Archive extraite avec succès!\n\n"
                            f"📦 {len(files_content)} fichier(s) extrait(s)\n"
                            f"📂 {extract_dir}"
                        )
                        
                        self.status_label.setText(f"✅ Archive extraite dans {extract_dir}")
                    else:
                        self.status_label.setText("❌ Extraction annulée")
                else:
                    QMessageBox.warning(self, "❌ Erreur", "Aucun fichier trouvé dans l'archive")
            
        except Exception as e:
            self.status_label.setText("❌ Erreur d'extraction")
            QMessageBox.critical(self, "❌ Erreur", f"Erreur:\n\n{str(e)}")
        finally:
            if self.progress_bar:
                self.progress_bar.setVisible(False)
    
    # === Méthodes d'aide ===
    
    def show_quick_guide(self):
        """Afficher le guide rapide"""
        guide = """
<h2>📖 Guide rapide - GitHub Doc Editor</h2>
<br>

<h3>🔐 Gestion des fichiers GPG</h3>

<p><b>1. Ouvrir un fichier .gpg</b></p>
<ul>
    <li>Double-cliquez sur le fichier dans l'arborescence</li>
    <li>Entrez le mot de passe GPG</li>
    <li>Le contenu s'affiche dans l'éditeur</li>
</ul>

<p><b>2. Ouvrir une archive .tar.gpg ou .rg.gpg</b></p>
<ul>
    <li>Double-cliquez sur l'archive</li>
    <li>Entrez le mot de passe GPG</li>
    <li>Une liste des fichiers s'affiche</li>
    <li>Double-cliquez sur un fichier pour l'éditer</li>
</ul>

<p><b>3. Modifier et commiter</b></p>
<ul>
    <li>Modifiez le contenu dans l'éditeur</li>
    <li>Cliquez sur "Commiter"</li>
    <li>Le fichier est automatiquement rechiffré</li>
    <li>Pour les archives, elles sont recompressées et rechiffrées</li>
</ul>

<p><b>4. Créer un nouveau fichier chiffré</b></p>
<ul>
    <li>Menu GPG → Chiffrer un fichier</li>
    <li>Sélectionnez un fichier</li>
    <li>Entrez un mot de passe</li>
    <li>Le fichier est chiffré et uploadé</li>
</ul>

<p><b>5. Créer une archive chiffrée</b></p>
<ul>
    <li>Menu GPG → Créer une archive chiffrée</li>
    <li>Sélectionnez un dossier</li>
    <li>Entrez un mot de passe</li>
    <li>L'archive est créée et uploadée</li>
</ul>

<br>
<p>💡 <b>Conseils :</b></p>
<ul>
    <li>Utilisez des mots de passe forts</li>
    <li>Conservez vos mots de passe en sécurité</li>
    <li>Les fichiers .rg.gpg sont des archives tar.gz chiffrées</li>
</ul>
"""
        QMessageBox.about(self, "📖 Guide rapide", guide)
    
    def show_gpg_help(self):
        """Afficher la documentation GPG"""
        gpg_help = """
<h2>🔐 Documentation GPG</h2>
<br>

<h3>📦 Types de fichiers supportés</h3>

<p><b>Fichiers .gpg simples</b></p>
<ul>
    <li>Fichiers texte chiffrés avec GPG</li>
    <li>Déchiffrés automatiquement à l'ouverture</li>
    <li>Rechiffrés automatiquement au commit</li>
</ul>

<p><b>Archives .tar.gpg et .rg.gpg</b></p>
<ul>
    <li>Archives tar.gz chiffrées avec GPG</li>
    <li>Extraction automatique des fichiers</li>
    <li>Édition des fichiers individuels</li>
    <li>Recompression et rechiffrement au commit</li>
</ul>

<br>

<h3>🔧 Installation de GPG</h3>

<p><b>macOS (Homebrew) :</b></p>
<pre style="background-color: #161b22; padding: 10px; border-radius: 4px; color: #c9d1d9;">
brew install gnupg
</pre>

<p><b>Ubuntu/Debian :</b></p>
<pre style="background-color: #161b22; padding: 10px; border-radius: 4px; color: #c9d1d9;">
sudo apt-get install gnupg
</pre>

<p><b>Windows :</b></p>
<ul>
    <li>Télécharger depuis : https://www.gnupg.org/download/</li>
    <li>Installer GPG4Win</li>
</ul>

<br>

<h3>🔑 Commandes GPG utiles</h3>

<p><b>Chiffrer un fichier :</b></p>
<pre style="background-color: #161b22; padding: 10px; border-radius: 4px; color: #c9d1d9;">
gpg --symmetric --cipher-algo AES256 fichier.txt
</pre>

<p><b>Déchiffrer un fichier :</b></p>
<pre style="background-color: #161b22; padding: 10px; border-radius: 4px; color: #c9d1d9;">
gpg --decrypt fichier.txt.gpg > fichier.txt
</pre>

<p><b>Créer une archive chiffrée :</b></p>
<pre style="background-color: #161b22; padding: 10px; border-radius: 4px; color: #c9d1d9;">
tar -czf archive.tar dossier/
gpg --symmetric --cipher-algo AES256 archive.tar
rm archive.tar
</pre>
"""
        QMessageBox.about(self, "🔐 Documentation GPG", gpg_help)
    
    def show_shortcuts(self):
        """Afficher les raccourcis clavier"""
        shortcuts = """
<h2>⌨️ Raccourcis clavier</h2>
<br>

<table style="width: 100%; border-collapse: collapse;">
    <tr style="border-bottom: 1px solid #30363d;">
        <th style="text-align: left; padding: 8px;">Raccourci</th>
        <th style="text-align: left; padding: 8px;">Action</th>
    </tr>
    <tr style="border-bottom: 1px solid #21262d;">
        <td style="padding: 8px;"><b>Ctrl+S</b></td>
        <td style="padding: 8px;">Sauvegarder le fichier localement</td>
    </tr>
    <tr style="border-bottom: 1px solid #21262d;">
        <td style="padding: 8px;"><b>Ctrl+Shift+C</b></td>
        <td style="padding: 8px;">Commiter vers GitHub</td>
    </tr>
    <tr style="border-bottom: 1px solid #21262d;">
        <td style="padding: 8px;"><b>Ctrl+Shift+R</b></td>
        <td style="padding: 8px;">Changer de dépôt</td>
    </tr>
    <tr style="border-bottom: 1px solid #21262d;">
        <td style="padding: 8px;"><b>Ctrl+Shift+D</b></td>
        <td style="padding: 8px;">Se déconnecter</td>
    </tr>
    <tr style="border-bottom: 1px solid #21262d;">
        <td style="padding: 8px;"><b>Ctrl+E</b></td>
        <td style="padding: 8px;">Chiffrer un fichier</td>
    </tr>
    <tr style="border-bottom: 1px solid #21262d;">
        <td style="padding: 8px;"><b>Ctrl+D</b></td>
        <td style="padding: 8px;">Déchiffrer un fichier</td>
    </tr>
    <tr style="border-bottom: 1px solid #21262d;">
        <td style="padding: 8px;"><b>Ctrl+Q</b></td>
        <td style="padding: 8px;">Quitter l'application</td>
    </tr>
    <tr style="border-bottom: 1px solid #21262d;">
        <td style="padding: 8px;"><b>F1</b></td>
        <td style="padding: 8px;">Guide rapide</td>
    </tr>
</table>
"""
        QMessageBox.about(self, "⌨️ Raccourcis clavier", shortcuts)
    
    def show_about(self):
        """Afficher la boîte À propos"""
        gpg_status = "✅ Disponible" if self.gpg_handler.gpg_available else "❌ Non installé"
        
        about_text = f"""
<h2>📖 GitHub Doc Editor</h2>
<p><b>Version 1.1.0</b></p>
<br>
<p>Éditeur de documents en ligne avec synchronisation GitHub</p>
<p>et support complet des fichiers GPG</p>
<br>
<p><b>🔐 Support GPG :</b> {gpg_status}</p>
<br>
<p><b>✨ Fonctionnalités :</b></p>
<ul>
    <li>🔗 Connexion sécurisée à GitHub</li>
    <li>📝 Édition de fichiers en temps réel</li>
    <li>🔓 Déchiffrement GPG automatique</li>
    <li>🔒 Chiffrement avant commit</li>
    <li>📦 Support des archives .tar.gpg et .rg.gpg</li>
    <li>📂 Extraction automatique des archives</li>
    <li>💾 Sauvegarde automatique</li>
    <li>🎨 Interface moderne</li>
</ul>
<br>
<p>Développé avec ❤️ en Python/PyQt5</p>
"""
        QMessageBox.about(self, "📖 À propos", about_text)
    
    # === Méthodes utilitaires ===
    
    def _clean_repo_url(self, url: str) -> str:
        """Nettoyer l'URL du dépôt"""
        url = url.strip()
        
        if url.startswith('https://github.com/') and '/' not in url.replace('https://github.com/', ''):
            QMessageBox.warning(
                self,
                "⚠️ URL invalide",
                f"Format correct: https://github.com/utilisateur/NOM_DU_DÉPÔT"
            )
            return ""
        
        if '/' in url and not url.startswith('http') and not url.startswith('git@'):
            parts = url.split('/')
            if len(parts) == 2:
                return f"https://github.com/{url}"
        
        if url.endswith('.git'):
            url = url[:-4]
        
        if url.startswith('git@'):
            url = url.replace('git@github.com:', 'https://github.com/')
        
        match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
        if not match:
            return ""
        
        return url
    
    def try_auto_connect(self):
        """Essayer de se connecter automatiquement"""
        try:
            settings = QSettings("GitHubEditor", "GitHubDocEditor")
            token = settings.value("token", "")
            repo_url = settings.value("repo_url", "")
            
            if token and repo_url:
                repo_url = self._clean_repo_url(repo_url)
                if repo_url:
                    self.connect_to_github(token, repo_url)
        except Exception as e:
            print(f"Erreur de connexion automatique: {e}")