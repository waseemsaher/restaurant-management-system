def get_main_style():
    return """
    /* Global Styles */
    QMainWindow, QWidget {
        background-color: #f0f2f5;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 13px;
        color: #1c1e21;
    }

    /* Professional Cards */
    QGroupBox, QFrame#login_card, QFrame#search_card {
        background-color: #ffffff;
        border: 1px solid #dddfe2;
        border-radius: 10px;
        padding: 10px;
        margin-top: 4px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top right;
        padding: 0 10px;
        color: #1877f2;
        font-weight: bold;
        font-size: 13px;
    }

    /* Buttons - Modern */
    QPushButton {
        background-color: #1877f2;
        color: white;
        border: none;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
        min-height: 28px;
    }

    QPushButton:hover {
        background-color: #166fe5;
    }

    QPushButton#checkout_btn {
        background-color: #42b72a;
        font-size: 15px;
        min-height: 36px;
    }
    
    QPushButton#checkout_btn:hover {
        background-color: #36a420;
    }

    QPushButton#clear_btn {
        background-color: #f02849;
    }
    
    QPushButton#clear_btn:hover {
        background-color: #d82242;
    }

    /* Modern Inputs - removed max-width so they fill available space */
    QLineEdit, QSpinBox, QComboBox, QDoubleSpinBox, QDateEdit {
        background-color: #f5f6f7;
        border: 1px solid #dddfe2;
        border-radius: 6px;
        padding: 6px 8px;
        font-size: 13px;
        color: #1c1e21;
        min-height: 28px;
    }

    QLineEdit:focus {
        border: 1px solid #1877f2;
        background-color: #ffffff;
    }

    /* Tables - Clean & Professional */
    QTableWidget {
        background-color: white;
        border: 1px solid #dddfe2;
        border-radius: 6px;
        gridline-color: #f0f2f5;
        selection-background-color: #e7f3ff;
        selection-color: #1877f2;
        font-size: 13px;
    }

    QHeaderView::section {
        background-color: #f5f6f7;
        color: #4b4f56;
        padding: 6px 8px;
        border: none;
        border-bottom: 2px solid #dddfe2;
        font-weight: bold;
        font-size: 12px;
    }

    /* Tabs */
    QTabWidget::pane {
        border: none;
        background: transparent;
    }

    QTabBar::tab {
        background: transparent;
        color: #606770;
        padding: 8px 18px;
        font-weight: bold;
        font-size: 13px;
        border-bottom: 3px solid transparent;
    }

    QTabBar::tab:selected {
        color: #1877f2;
        border-bottom: 3px solid #1877f2;
    }

    QTabBar::tab:hover {
        background: #ebedf0;
        border-radius: 6px;
    }

    /* Scroll Areas */
    QScrollArea {
        border: none;
        background: transparent;
    }

    /* Labels in forms */
    QLabel {
        padding: 1px 0px;
    }

    /* Form layouts */
    QFormLayout {
        margin: 4px;
    }
    """

def get_login_style():
    return """
    #login_card {
        border: 1px solid #dddfe2;
        border-radius: 12px;
    }
    #login_title {
        color: #1c1e21;
        font-size: 24px;
        font-weight: bold;
    }
    """
