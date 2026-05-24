def get_main_style():
    return """
    /* Global Styles */
    QMainWindow, QWidget {
        background-color: #f0f2f5;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
        color: #1c1e21;
    }

    /* Professional Cards */
    QGroupBox, QFrame#login_card, QFrame#search_card {
        background-color: #ffffff;
        border: 1px solid #dddfe2;
        border-radius: 12px;
        padding: 15px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top right;
        padding: 0 15px;
        color: #1877f2;
        font-weight: bold;
        font-size: 16px;
    }

    /* Buttons - Modern & Large */
    QPushButton {
        background-color: #1877f2;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 15px;
    }

    QPushButton:hover {
        background-color: #166fe5;
    }

    QPushButton#checkout_btn {
        background-color: #42b72a;
        font-size: 18px;
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

    /* Modern Inputs */
    QLineEdit, QSpinBox, QComboBox {
        background-color: #f5f6f7;
        border: 1px solid #dddfe2;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
        color: #1c1e21;
    }

    QLineEdit:focus {
        border: 1px solid #1877f2;
        background-color: #ffffff;
    }

    /* Tables - Clean & Professional */
    QTableWidget {
        background-color: white;
        border: 1px solid #dddfe2;
        border-radius: 8px;
        gridline-color: #f0f2f5;
        selection-background-color: #e7f3ff;
        selection-color: #1877f2;
    }

    QHeaderView::section {
        background-color: #f5f6f7;
        color: #4b4f56;
        padding: 12px;
        border: none;
        border-bottom: 2px solid #dddfe2;
        font-weight: bold;
        font-size: 13px;
    }

    /* Tabs */
    QTabWidget::pane {
        border: none;
        background: transparent;
    }

    QTabBar::tab {
        background: transparent;
        color: #606770;
        padding: 15px 30px;
        font-weight: bold;
        font-size: 15px;
        border-bottom: 3px solid transparent;
    }

    QTabBar::tab:selected {
        color: #1877f2;
        border-bottom: 3px solid #1877f2;
    }

    QTabBar::tab:hover {
        background: #ebedf0;
        border-radius: 8px;
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
        font-size: 28px;
        font-weight: bold;
    }
    """
