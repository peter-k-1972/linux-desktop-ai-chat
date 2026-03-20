"""
Einfaches Hell/Dunkel-Theme. Keine Neon-Farben, maximale Lesbarkeit.
"""


def get_stylesheet(theme: str) -> str:
    """Liefert das Stylesheet für light oder dark."""
    if theme == "light":
        return _light_stylesheet()
    return _dark_stylesheet()


def _light_stylesheet() -> str:
    # Klare, lesbare Farben
    bg = "#f0f0f0"
    surface = "#ffffff"
    fg = "#1a1a1a"
    muted = "#555555"
    border = "#cccccc"
    border_medium = "#999999"
    accent = "#2563eb"
    accent_hover = "#1d4ed8"
    input_bg = "#ffffff"
    hover_bg = "#e8e8e8"
    selected_bg = "#e0e8f0"

    return f"""
    QMainWindow {{
        background-color: {bg};
        color: {fg};
    }}

    QWidget#chatWidget {{
        background-color: {bg};
    }}

    QLabel {{
        color: {fg};
        font-size: 14px;
    }}

    QPushButton {{
        background-color: {surface};
        color: {fg};
        border: 1px solid {border};
        padding: 10px 18px;
        font-size: 14px;
        font-weight: 500;
        border-radius: 12px;
    }}

    QPushButton:hover {{
        background-color: {hover_bg};
        border: 1px solid {border_medium};
    }}

    QPushButton:pressed {{
        background-color: #d0d0d0;
    }}

    #sendButton {{
        background-color: {accent};
        border: none;
        border-radius: 12px;
        font-weight: 700;
        color: white;
        padding: 8px 20px;
    }}

    #sendButton:hover {{
        background-color: {accent_hover};
    }}

    #settingsSaveBtn {{
        background-color: {accent};
        border: none;
        color: white;
        font-weight: 700;
    }}

    #settingsSaveBtn:hover {{
        background-color: {accent_hover};
    }}

    #chatView {{
        background-color: transparent;
        border: none;
        padding: 20px;
        color: {fg};
    }}

    #chatComposer {{
        background-color: {bg};
        border-top: 1px solid {border};
    }}

    #composerContainer {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 20px;
        padding: 4px;
    }}

    #composerHint {{
        color: {muted};
        font-size: 11px;
        padding: 4px 0 8px 0;
    }}

    #inputContainer {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 20px;
        margin: 6px 20px 12px 20px;
    }}

    #chatInput {{
        background: transparent;
        border: none;
        color: {fg};
        padding: 12px 14px;
        font-size: 15px;
        selection-background-color: {accent};
    }}

    QComboBox {{
        background-color: {input_bg};
        border: 1px solid {border};
        border-radius: 12px;
        color: {fg};
        padding: 8px 14px;
        min-height: 38px;
        font-weight: 500;
    }}

    QComboBox:hover {{
        border: 1px solid {border_medium};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 34px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {fg};
        margin-right: 12px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {surface};
        border: 1px solid {border};
        color: {fg};
        selection-background-color: {accent};
        selection-color: white;
        border-radius: 8px;
        padding: 8px;
    }}

    QCheckBox {{
        color: {fg};
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {border_medium};
        background-color: {surface};
    }}

    QCheckBox::indicator:checked {{
        background-color: {accent};
        border-color: {accent};
    }}

    QLineEdit {{
        background-color: {input_bg};
        border: 1px solid {border};
        border-radius: 12px;
        color: {fg};
        padding: 12px 16px;
        font-size: 14px;
    }}

    QLineEdit:focus {{
        border: 1px solid {accent};
    }}

    QListWidget, QTreeWidget {{
        background-color: transparent;
        border: none;
        color: {fg};
        padding: 10px;
    }}

    QListWidget::item, QTreeWidget::item {{
        padding: 14px;
        border-radius: 12px;
        background-color: transparent;
        margin-bottom: 4px;
        color: {fg};
    }}

    QListWidget::item:hover, QTreeWidget::item:hover {{
        background-color: {hover_bg};
        color: {fg};
    }}

    QListWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {selected_bg};
        border: 1px solid {accent};
        color: {fg};
        font-weight: 600;
    }}

    QDialog {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 12px;
    }}

    QSpinBox, QDoubleSpinBox {{
        background-color: {input_bg};
        border: 1px solid {border};
        border-radius: 8px;
        color: {fg};
        padding: 6px;
        min-height: 32px;
    }}

    QToolBar {{
        background-color: {bg};
        border-bottom: 1px solid {border};
        padding: 10px 20px;
    }}

    #chatScrollArea {{
        background-color: transparent;
        border: none;
    }}

    #chatContainer {{
        background-color: transparent;
        max-width: 1200px;
    }}

    #projectChatListWidget {{
        background-color: {bg};
    }}

    #backBtn {{
        background-color: {accent};
        border: none;
        border-radius: 12px;
        font-weight: 700;
        color: white;
        padding: 12px 20px;
    }}

    #backBtn:hover {{
        background-color: {accent_hover};
    }}

    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 10px;
    }}

    QScrollBar::handle:vertical {{
        background: {border_medium};
        min-height: 40px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {fg};
    }}

    QMenu {{
        background-color: {surface};
        border: 1px solid {border};
        color: {fg};
        border-radius: 8px;
        padding: 8px;
    }}

    QMenu::item {{
        padding: 10px 28px;
        border-radius: 6px;
    }}

    QMenu::item:selected {{
        background-color: {accent};
        color: white;
    }}

    #sidebarWidget {{
        background-color: {bg};
        border-right: 1px solid {border};
        min-width: 300px;
    }}

    #newChatBtn {{
        background-color: {accent};
        border: none;
        border-radius: 12px;
        font-weight: 700;
        color: white;
        padding: 14px;
        font-size: 15px;
    }}

    #newChatBtn:hover {{
        background-color: {accent_hover};
    }}

    #saveChatBtn {{
        min-width: 50px;
        padding: 12px;
        border-radius: 12px;
    }}

    #overkillButton:checked {{
        background-color: {accent};
        border: none;
        color: white;
    }}

    #searchEdit {{
        background-color: {input_bg};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 10px 14px;
    }}

    QDockWidget {{
        titlebar-close-icon: none;
        titlebar-normal-icon: none;
        border: none;
    }}

    QDockWidget::title {{
        background-color: {bg};
        padding: 12px 16px;
        color: {muted};
        font-size: 12px;
        font-weight: bold;
    }}

    QFormLayout QLabel {{
        color: {fg};
        font-weight: 500;
    }}

    QTreeView {{
        background-color: transparent;
        border: none;
        color: {fg};
        padding: 8px;
    }}

    QTreeView::item {{
        padding: 10px 8px;
    }}

    QTreeView::item:hover {{
        background-color: {hover_bg};
    }}

    QTreeView::item:selected {{
        background-color: {selected_bg};
        border: 1px solid {accent};
    }}

    QStatusBar {{
        background-color: {bg};
        color: {muted};
        border-top: 1px solid {border};
    }}

    QTabBar::tab {{
        background: transparent;
        padding: 10px 15px;
        color: {muted};
        font-weight: 600;
        font-size: 11px;
    }}

    QTabBar::tab:selected {{
        color: {fg};
        border-bottom: 2px solid {accent};
    }}

    QTabWidget::pane {{
        border: none;
    }}

    #projectHeaderLabel {{
        font-size: 18px;
        font-weight: 700;
        color: {fg};
    }}

    #chatSidePanel {{
        background-color: #f5f5f5;
        border-left: 1px solid {border};
    }}

    #modelSettingsPanel, #promptManagerPanel {{
        background: transparent;
    }}
    """


def _dark_stylesheet() -> str:
    # Dunkles Theme mit gutem Kontrast
    bg = "#2d2d2d"
    surface = "#3d3d3d"
    fg = "#e8e8e8"
    muted = "#a0a0a0"
    border = "#505050"
    border_medium = "#606060"
    accent = "#4a90d9"
    accent_hover = "#5a9ee8"
    input_bg = "#3d3d3d"
    hover_bg = "#4a4a4a"
    selected_bg = "#3d5a80"

    return f"""
    QMainWindow {{
        background-color: {bg};
        color: {fg};
    }}

    QWidget#chatWidget {{
        background-color: {bg};
    }}

    QLabel {{
        color: {fg};
        font-size: 14px;
    }}

    QPushButton {{
        background-color: {surface};
        color: {fg};
        border: 1px solid {border};
        padding: 10px 18px;
        font-size: 14px;
        font-weight: 500;
        border-radius: 12px;
    }}

    QPushButton:hover {{
        background-color: {hover_bg};
        border: 1px solid {border_medium};
    }}

    QPushButton:pressed {{
        background-color: #505050;
    }}

    #sendButton {{
        background-color: {accent};
        border: none;
        border-radius: 12px;
        font-weight: 700;
        color: white;
        padding: 8px 20px;
    }}

    #sendButton:hover {{
        background-color: {accent_hover};
    }}

    #settingsSaveBtn {{
        background-color: {accent};
        border: none;
        color: white;
        font-weight: 700;
    }}

    #settingsSaveBtn:hover {{
        background-color: {accent_hover};
    }}

    #chatView {{
        background-color: transparent;
        border: none;
        padding: 20px;
        color: {fg};
    }}

    #chatComposer {{
        background-color: {bg};
        border-top: 1px solid {border};
    }}

    #composerContainer {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 20px;
        padding: 4px;
    }}

    #composerHint {{
        color: {muted};
        font-size: 11px;
        padding: 4px 0 8px 0;
    }}

    #inputContainer {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 20px;
        margin: 6px 20px 12px 20px;
    }}

    #chatInput {{
        background: transparent;
        border: none;
        color: {fg};
        padding: 12px 14px;
        font-size: 15px;
        selection-background-color: {accent};
    }}

    QComboBox {{
        background-color: {input_bg};
        border: 1px solid {border};
        border-radius: 12px;
        color: {fg};
        padding: 8px 14px;
        min-height: 38px;
        font-weight: 500;
    }}

    QComboBox:hover {{
        border: 1px solid {border_medium};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 34px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {fg};
        margin-right: 12px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {surface};
        border: 1px solid {border};
        color: {fg};
        selection-background-color: {accent};
        selection-color: white;
        border-radius: 8px;
        padding: 8px;
    }}

    QCheckBox {{
        color: {fg};
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {border_medium};
        background-color: {surface};
    }}

    QCheckBox::indicator:checked {{
        background-color: {accent};
        border-color: {accent};
    }}

    QLineEdit {{
        background-color: {input_bg};
        border: 1px solid {border};
        border-radius: 12px;
        color: {fg};
        padding: 12px 16px;
        font-size: 14px;
    }}

    QLineEdit:focus {{
        border: 1px solid {accent};
    }}

    QListWidget, QTreeWidget {{
        background-color: transparent;
        border: none;
        color: {fg};
        padding: 10px;
    }}

    QListWidget::item, QTreeWidget::item {{
        padding: 14px;
        border-radius: 12px;
        background-color: transparent;
        margin-bottom: 4px;
        color: {fg};
    }}

    QListWidget::item:hover, QTreeWidget::item:hover {{
        background-color: {hover_bg};
        color: {fg};
    }}

    QListWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {selected_bg};
        border: 1px solid {accent};
        color: {fg};
        font-weight: 600;
    }}

    QDialog {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 12px;
    }}

    QSpinBox, QDoubleSpinBox {{
        background-color: {input_bg};
        border: 1px solid {border};
        border-radius: 8px;
        color: {fg};
        padding: 6px;
        min-height: 32px;
    }}

    QToolBar {{
        background-color: {bg};
        border-bottom: 1px solid {border};
        padding: 10px 20px;
    }}

    #chatScrollArea {{
        background-color: transparent;
        border: none;
    }}

    #chatContainer {{
        background-color: transparent;
        max-width: 1200px;
    }}

    #projectChatListWidget {{
        background-color: {bg};
    }}

    #backBtn {{
        background-color: {accent};
        border: none;
        border-radius: 12px;
        font-weight: 700;
        color: white;
        padding: 12px 20px;
    }}

    #backBtn:hover {{
        background-color: {accent_hover};
    }}

    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 10px;
    }}

    QScrollBar::handle:vertical {{
        background: {border_medium};
        min-height: 40px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {fg};
    }}

    QMenu {{
        background-color: {surface};
        border: 1px solid {border};
        color: {fg};
        border-radius: 8px;
        padding: 8px;
    }}

    QMenu::item {{
        padding: 10px 28px;
        border-radius: 6px;
    }}

    QMenu::item:selected {{
        background-color: {accent};
        color: white;
    }}

    #sidebarWidget {{
        background-color: {bg};
        border-right: 1px solid {border};
        min-width: 300px;
    }}

    #newChatBtn {{
        background-color: {accent};
        border: none;
        border-radius: 12px;
        font-weight: 700;
        color: white;
        padding: 14px;
        font-size: 15px;
    }}

    #newChatBtn:hover {{
        background-color: {accent_hover};
    }}

    #saveChatBtn {{
        min-width: 50px;
        padding: 12px;
        border-radius: 12px;
    }}

    #overkillButton:checked {{
        background-color: {accent};
        border: none;
        color: white;
    }}

    #searchEdit {{
        background-color: {input_bg};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 10px 14px;
    }}

    QDockWidget {{
        titlebar-close-icon: none;
        titlebar-normal-icon: none;
        border: none;
    }}

    QDockWidget::title {{
        background-color: {bg};
        padding: 12px 16px;
        color: {muted};
        font-size: 12px;
        font-weight: bold;
    }}

    QFormLayout QLabel {{
        color: {fg};
        font-weight: 500;
    }}

    QTreeView {{
        background-color: transparent;
        border: none;
        color: {fg};
        padding: 8px;
    }}

    QTreeView::item {{
        padding: 10px 8px;
    }}

    QTreeView::item:hover {{
        background-color: {hover_bg};
    }}

    QTreeView::item:selected {{
        background-color: {selected_bg};
        border: 1px solid {accent};
    }}

    QStatusBar {{
        background-color: {bg};
        color: {muted};
        border-top: 1px solid {border};
    }}

    QTabBar::tab {{
        background: transparent;
        padding: 10px 15px;
        color: {muted};
        font-weight: 600;
        font-size: 11px;
    }}

    QTabBar::tab:selected {{
        color: {fg};
        border-bottom: 2px solid {accent};
    }}

    QTabWidget::pane {{
        border: none;
    }}

    #projectHeaderLabel {{
        font-size: 18px;
        font-weight: 700;
        color: {fg};
    }}

    #chatSidePanel {{
        background-color: #2d2d2d;
        border-left: 1px solid {border};
    }}

    #modelSettingsPanel, #promptManagerPanel {{
        background: transparent;
    }}
    """


def get_theme_colors(theme: str) -> dict:
    """Farben für Komponenten mit inline-Styles (MessageWidget, ChatWidget, etc.)."""
    if theme == "light":
        return {
            "fg": "#1a1a1a",
            "muted": "#555555",
            "accent": "#2563eb",
            "top_bar_bg": "#f5f5f5",
            "top_bar_border": "#cccccc",
        }
    return {
        "fg": "#e8e8e8",
        "muted": "#a0a0a0",
        "accent": "#4a90d9",
        "top_bar_bg": "#353535",
        "top_bar_border": "#505050",
    }


# Legacy-Kompatibilität
class ModernStyle:
    """Legacy-Attribute für Komponenten, die noch darauf zugreifen."""
    FG_COLOR = "#e8e8e8"
    MUTED_COLOR = "#a0a0a0"
    ACCENT_PRIMARY = "#4a90d9"
