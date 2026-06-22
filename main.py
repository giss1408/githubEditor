#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub Document Editor - Application principale
Version avec tous les imports
"""

import sys
import os

# Imports PyQt5 complets
from PyQt5.QtWidgets import (
    QApplication, QSplashScreen, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QToolBar, QAction,
    QMessageBox, QStatusBar, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QProgressBar,
    QFileDialog, QDialog, QDialogButtonBox, QFormLayout,
    QLineEdit, QTextBrowser, QFrame, QScrollArea
)
from PyQt5.QtCore import (
    Qt, QTimer, QSettings, QPropertyAnimation,
    QEasingCurve, pyqtSignal, QRect
)
from PyQt5.QtGui import (
    QFont, QColor, QKeySequence, QPixmap, QPalette,
    QLinearGradient, QBrush, QIcon, QPainter
)

# Import du module principal
from ui.main_window import MainWindow

def main():
    """Point d'entrée principal"""
    app = QApplication(sys.argv)
    app.setApplicationName("GitHub Doc Editor")
    app.setOrganizationName("GitHubEditor")
    
    # Style moderne
    app.setStyle('Fusion')
    
    # Palette personnalisée
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(13, 17, 23))
    palette.setColor(QPalette.WindowText, QColor(201, 209, 217))
    palette.setColor(QPalette.Base, QColor(13, 17, 23))
    palette.setColor(QPalette.AlternateBase, QColor(22, 27, 34))
    palette.setColor(QPalette.ToolTipBase, QColor(22, 27, 34))
    palette.setColor(QPalette.ToolTipText, QColor(201, 209, 217))
    palette.setColor(QPalette.Text, QColor(201, 209, 217))
    palette.setColor(QPalette.Button, QColor(22, 27, 34))
    palette.setColor(QPalette.ButtonText, QColor(201, 209, 217))
    palette.setColor(QPalette.Highlight, QColor(31, 111, 235))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Charger le fichier de style
    try:
        style_path = os.path.join(os.path.dirname(__file__), 'resources', 'styles.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r') as f:
                app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("⚠️ Style file not found, using default style")
    
    # Splash screen
    splash = QSplashScreen()
    splash.setStyleSheet("""
        QSplashScreen {
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: 'Inter', sans-serif;
        }
    """)
    splash.show()
    splash.showMessage("🚀 Chargement de GitHub Doc Editor...", Qt.AlignHCenter | Qt.AlignBottom, QColor(201, 209, 217))
    QApplication.processEvents()
    
    # Créer la fenêtre principale
    window = MainWindow()
    
    # Fermer le splash après un délai
    QTimer.singleShot(1000, splash.close)
    
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()