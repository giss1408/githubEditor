# -*- coding: utf-8 -*-

"""
Widget d'édition de texte avec coloration syntaxique - Version corrigée
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QTextDocument, QRegularExpressionValidator

import re


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter pour Python - Version corrigée"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Définir les règles de coloration
        self.highlighting_rules = []
        
        # Mots-clés Python
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue',
            'def', 'del', 'elif', 'else', 'except', 'exec',
            'finally', 'for', 'from', 'global', 'if', 'import',
            'in', 'is', 'lambda', 'not', 'or', 'pass', 'print',
            'raise', 'return', 'try', 'while', 'with', 'yield',
            'True', 'False', 'None', 'self', 'super'
        ]
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 0, 255))  # Bleu
        keyword_format.setFontWeight(QFont.Bold)
        
        for word in keywords:
            # Utiliser QRegularExpression pour une meilleure compatibilité
            pattern = QRegularExpression(r'\b' + word + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Chaînes de caractères
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(0, 128, 0))  # Vert
        
        # Chaînes avec guillemets doubles
        pattern = QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"')
        self.highlighting_rules.append((pattern, string_format))
        
        # Chaînes avec guillemets simples
        pattern = QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'")
        self.highlighting_rules.append((pattern, string_format))
        
        # Commentaires
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))  # Gris
        comment_format.setFontItalic(True)
        
        pattern = QRegularExpression(r'#[^\n]*')
        self.highlighting_rules.append((pattern, comment_format))
        
        # Nombres
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(255, 0, 0))  # Rouge
        
        pattern = QRegularExpression(r'\b[0-9]+\b')
        self.highlighting_rules.append((pattern, number_format))
        
        # Nombres décimaux
        pattern = QRegularExpression(r'\b[0-9]+\.[0-9]+\b')
        self.highlighting_rules.append((pattern, number_format))
        
        # Décorateurs (@...)
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor(128, 0, 128))  # Violet
        
        pattern = QRegularExpression(r'@\w+')
        self.highlighting_rules.append((pattern, decorator_format))
        
        # Classes (nom après class)
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(0, 128, 128))  # Teal
        class_format.setFontWeight(QFont.Bold)
        
        pattern = QRegularExpression(r'\bclass\s+(\w+)')
        self.highlighting_rules.append((pattern, class_format))
        
        # Fonctions (nom après def)
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(0, 128, 128))  # Teal
        function_format.setFontWeight(QFont.Bold)
        
        pattern = QRegularExpression(r'\bdef\s+(\w+)')
        self.highlighting_rules.append((pattern, function_format))
        
    def highlightBlock(self, text):
        """Appliquer la coloration syntaxique à un bloc"""
        # Parcourir toutes les règles
        for pattern, format in self.highlighting_rules:
            # Utiliser QRegularExpression pour la correspondance
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class EditorWidget(QWidget):
    """Widget d'édition de texte avec fonctionnalités avancées"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.sha = None
        self.modified = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface du widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils de l'éditeur
        toolbar = QHBoxLayout()
        
        self.file_label = QLabel("📄 Aucun fichier ouvert")
        toolbar.addWidget(self.file_label)
        
        # Stats en temps réel
        self.stats_label = QLabel("Lignes: 0 | Mots: 0 | Caractères: 0")
        self.stats_label.setAlignment(Qt.AlignRight)
        toolbar.addWidget(self.stats_label)
        
        layout.addLayout(toolbar)
        
        # Éditeur de texte
        self.text_edit = QTextEdit()
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.text_edit.setFont(QFont("Courier New", 12))
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)
        
        # Activer le syntax highlighting par défaut (Python)
        self.highlighter = PythonHighlighter(self.text_edit.document())
        
        layout.addWidget(self.text_edit)
        
    def set_content(self, content: str):
        """Définir le contenu de l'éditeur"""
        self.text_edit.setText(content)
        self.modified = False
        self.update_stats()
        self.update_status()
        
    def get_content(self) -> str:
        """Obtenir le contenu de l'éditeur"""
        return self.text_edit.toPlainText()
    
    def set_file_path(self, path: str):
        """Définir le chemin du fichier"""
        self.file_path = path
        self.file_label.setText(f"📄 {path}")
        
        # Détecter le type de fichier pour le highlighting
        if path.endswith('.py'):
            self.highlighter = PythonHighlighter(self.text_edit.document())
        else:
            # Désactiver le highlighting pour les autres fichiers
            self.highlighter = None
        
        self.update_stats()
        
    def set_sha(self, sha: str):
        """Définir le SHA du fichier"""
        self.sha = sha
        
    def get_sha(self) -> str:
        """Obtenir le SHA du fichier"""
        return self.sha
    
    def set_modified(self, modified: bool):
        """Définir l'état de modification"""
        self.modified = modified
        self.update_status()
        
    def is_modified(self) -> bool:
        """Vérifier si le fichier a été modifié"""
        return self.modified
    
    def on_text_changed(self):
        """Gérer le changement de texte"""
        if not self.modified:
            self.modified = True
            self.update_status()
        
        self.update_stats()
        
    def update_status(self):
        """Mettre à jour le statut"""
        if self.modified:
            self.file_label.setStyleSheet("color: orange; font-weight: bold;")
            self.file_label.setText(f"📄 {self.file_path} ⚠️ Modifié")
        else:
            self.file_label.setStyleSheet("color: green;")
            self.file_label.setText(f"📄 {self.file_path} ✅ Sauvegardé")
            
    def update_stats(self):
        """Mettre à jour les statistiques"""
        content = self.text_edit.toPlainText()
        lines = len(content.split('\n'))
        words = len(content.split()) if content.strip() else 0
        chars = len(content)
        
        self.stats_label.setText(f"Lignes: {lines} | Mots: {words} | Caractères: {chars}")
            
    def clear(self):
        """Effacer l'éditeur"""
        self.text_edit.clear()
        self.file_path = None
        self.sha = None
        self.modified = False
        self.file_label.setText("📄 Aucun fichier ouvert")
        self.file_label.setStyleSheet("")
        self.update_stats()
        
    def search_text(self, text: str, case_sensitive: bool = False) -> bool:
        """Rechercher du texte dans l'éditeur"""
        flags = QTextDocument.FindFlags()
        if case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        
        cursor = self.text_edit.textCursor()
        cursor = self.text_edit.document().find(text, cursor, flags)
        
        if not cursor.isNull():
            self.text_edit.setTextCursor(cursor)
            return True
        return False
    
    def replace_text(self, search_text: str, replace_text: str, case_sensitive: bool = False) -> int:
        """Remplacer du texte dans l'éditeur"""
        flags = QTextDocument.FindFlags()
        if case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        
        cursor = self.text_edit.textCursor()
        cursor.beginEditBlock()
        
        # Remplacer toutes les occurrences
        count = 0
        while True:
            cursor = self.text_edit.document().find(search_text, cursor, flags)
            if cursor.isNull():
                break
            cursor.insertText(replace_text)
            count += 1
        
        cursor.endEditBlock()
        return count
    
    def zoom_in(self):
        """Zoomer dans l'éditeur"""
        font = self.text_edit.font()
        font.setPointSize(font.pointSize() + 1)
        self.text_edit.setFont(font)
    
    def zoom_out(self):
        """Zoomer hors de l'éditeur"""
        font = self.text_edit.font()
        new_size = max(8, font.pointSize() - 1)
        font.setPointSize(new_size)
        self.text_edit.setFont(font)
    
    def set_font_size(self, size: int):
        """Définir la taille de la police"""
        font = self.text_edit.font()
        font.setPointSize(size)
        self.text_edit.setFont(font)
    
    def get_font_size(self) -> int:
        """Obtenir la taille de la police"""
        return self.text_edit.font().pointSize()