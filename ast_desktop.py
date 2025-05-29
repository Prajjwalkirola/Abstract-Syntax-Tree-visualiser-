import sys
import os
import subprocess
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QComboBox, QListWidget, QListWidgetItem,
    QStackedWidget, QMessageBox, QSizePolicy, QGroupBox, QSpacerItem
)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor, QLinearGradient, QBrush
from PyQt5.QtCore import Qt
import json

BACKEND_DIR = os.path.join(os.path.dirname(__file__), 'backend')
HISTORY_DIR = os.path.join(BACKEND_DIR, 'history')
SOURCE_FILE = os.path.join(BACKEND_DIR, 'source.py')
AST_FILE = os.path.join(BACKEND_DIR, 'ast.json')
TREE_FILE = os.path.join(BACKEND_DIR, 'ast_output.png')

STEPS = [
    ("Start", "Start"),
    ("User Action", "User Action"),
    ("Entity", "Entity"),
    ("Confirmation", "Confirmation")
]

class ASTDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AST Visualizer - Desktop App (Flowchart UI)")
        self.setGeometry(100, 100, 1300, 800)
        self.setMinimumSize(1000, 700)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        self.apply_theme()

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e3f2fd, stop:1 #b3c6e7);
                border: none;
                border-radius: 16px;
                padding: 12px 0 12px 0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 20px;
                color: #222;
            }
            QListWidget::item {
                padding: 16px 12px;
                margin: 6px 8px;
                border-radius: 10px;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4A90E2, stop:1 #50E3C2);
                color: #fff;
                font-weight: bold;
                border-radius: 10px;
            }
        """)
        for step, label in STEPS:
            item = QListWidgetItem(label)
            item.setFont(QFont("Segoe UI", 16))
            self.sidebar.addItem(item)
        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self.switch_step)
        self.layout.addWidget(self.sidebar)

        # Main area (stacked widget)
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        # Step widgets
        self.start_widget = self.create_start_widget()
        self.user_action_widget = self.create_user_action_widget()
        self.entity_widget = self.create_entity_widget()
        self.confirmation_widget = self.create_confirmation_widget()

        self.stack.addWidget(self.start_widget)
        self.stack.addWidget(self.user_action_widget)
        self.stack.addWidget(self.entity_widget)
        self.stack.addWidget(self.confirmation_widget)

        self.refresh_history()
        if self.history_combo.count() > 0:
            self.load_history_entry(0)

    def apply_theme(self):
        # Set a modern, attractive palette
        palette = QPalette()
        base_color = QColor("#f4faff")
        accent_color = QColor("#4A90E2")
        group_bg = QColor("#e3f2fd")
        palette.setColor(QPalette.Window, base_color)
        palette.setColor(QPalette.Base, QColor("#f8faff"))
        palette.setColor(QPalette.AlternateBase, QColor("#e3f2fd"))
        palette.setColor(QPalette.Text, QColor("#222"))
        palette.setColor(QPalette.Button, accent_color)
        palette.setColor(QPalette.ButtonText, QColor("#fff"))
        self.setPalette(palette)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f4faff, stop:1 #e3f2fd);
            }
            QLabel {
                color: #222;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                background: #e3f2fd;
                border: 2px solid #4A90E2;
                border-radius: 10px;
                margin-top: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: #1976d2;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 15px;
                border-radius: 8px;
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4A90E2, stop:1 #50E3C2);
                color: #fff;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #50E3C2, stop:1 #4A90E2);
            }
            QComboBox, QListWidget, QTextEdit {
                font-family: 'Consolas', 'Segoe UI', monospace;
                font-size: 15px;
            }
            QListWidget::item:selected {
                background: #b3e5fc;
                color: #1976d2;
            }
            QScrollBar:vertical {
                background: #e3f2fd;
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #4A90E2;
                min-height: 20px;
                border-radius: 6px;
            }
        """)

    def switch_step(self, idx):
        self.stack.setCurrentIndex(idx)
        if idx == 2:
            self.update_entity_widget()
        if idx == 3:
            self.update_confirmation_widget()

    def create_start_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        label = QLabel("<b>Start</b><br>Enter your code below:")
        label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(label)
        self.history_combo = QComboBox()
        self.history_combo.setStyleSheet("padding: 6px; font-size: 14px;")
        self.history_combo.currentIndexChanged.connect(self.load_history_entry)
        layout.addWidget(self.history_combo)
        # Add+ button styled like Process & Visualize AST button
        add_btn = QPushButton("Add +")
        add_btn.setObjectName("addButton")
        add_btn.setToolTip("Clear editor to enter new code")
        add_btn.setStyleSheet("""
            QPushButton#addButton {
                padding: 8px 16px;
                font-size: 14px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4A90E2, stop:1 #50E3C2);
                color: #fff;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton#addButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #50E3C2, stop:1 #4A90E2);
                color: #fff;
            }
        """)
        add_btn.clicked.connect(self.clear_code_editor)
        layout.addWidget(add_btn)
        code_group = QGroupBox("Code Editor")
        code_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        code_layout = QVBoxLayout(code_group)
        self.code_edit = QTextEdit()
        self.code_edit.setFont(QFont("Consolas", 13))
        self.code_edit.setStyleSheet("padding: 10px; background: #f8faff; border-radius: 6px;")
        code_layout.addWidget(self.code_edit)
        layout.addWidget(code_group)
        self.process_btn = QPushButton("Process  Visualize AST")
        self.process_btn.setObjectName("processButton")
        self.process_btn.setStyleSheet("""
            QPushButton#processButton {
                padding: 10px 20px;
                font-size: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4A90E2, stop:1 #50E3C2);
                color: white;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton#processButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #50E3C2, stop:1 #4A90E2);
                color: #fff;
            }
        """)
        self.process_btn.clicked.connect(self.process_code)
        layout.addWidget(self.process_btn)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return widget

    def create_user_action_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        label = QLabel("<b>User Action</b><br>Code history:")
        label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(label)
        group = QGroupBox("History List")
        group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        group_layout = QVBoxLayout(group)
        self.user_action_list = QListWidget()
        self.user_action_list.setStyleSheet("font-size: 14px; padding: 6px;")
        group_layout.addWidget(self.user_action_list)
        layout.addWidget(group)
        # Load button
        load_btn = QPushButton("Load Selected History")
        load_btn.setObjectName("loadHistoryBtn")
        load_btn.setToolTip("Load the selected code history entry")
        load_btn.setStyleSheet("""
            QPushButton#loadHistoryBtn {
                padding: 8px 16px;
                font-size: 14px;
                background: #1976d2;
                color: #fff;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton#loadHistoryBtn:hover {
                background: #1565c0;
                color: #fff;
                border: 2px solid #64b5f6;
            }
        """)
        load_btn.clicked.connect(self.load_selected_history)
        layout.addWidget(load_btn)
        # Delete button
        delete_btn = QPushButton("Delete Selected History")
        delete_btn.setObjectName("deleteHistoryBtn")
        delete_btn.setToolTip("Delete the selected code history entry")
        delete_btn.setStyleSheet("""
            QPushButton#deleteHistoryBtn {
                padding: 8px 16px;
                font-size: 14px;
                background: #d32f2f;
                color: #fff;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton#deleteHistoryBtn:hover {
                background: #b71c1c;
                color: #fff;
                border: 2px solid #ff5252;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_history)
        layout.addWidget(delete_btn)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return widget

    def create_entity_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        label = QLabel("<b>Entity</b><br>Operators and Functions:")
        label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(label)
        group = QGroupBox("Entities")
        group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        group_layout = QVBoxLayout(group)
        self.entity_text = QTextEdit()
        self.entity_text.setReadOnly(True)
        self.entity_text.setFont(QFont("Consolas", 12))
        self.entity_text.setStyleSheet("padding: 10px; background: #f8faff; border-radius: 6px;")
        group_layout.addWidget(self.entity_text)
        layout.addWidget(group)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return widget

    def create_confirmation_widget(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(32)
        left = QVBoxLayout()
        right = QVBoxLayout()
        right.setSpacing(24)
        # Add a container widget for the right pane to control its size and padding
        right_container = QWidget()
        right_container.setStyleSheet("""
            background: #f4faff;
            border-radius: 24px;
            margin: 30px 30px 30px 30px;
            padding: 30px 30px 30px 30px;
        """)
        right_container_layout = QVBoxLayout(right_container)
        right_container_layout.setSpacing(24)
        right_container_layout.setContentsMargins(20, 20, 20, 20)
        # Left panel widgets
        left.addWidget(QLabel("<b>Code</b>"))
        self.confirm_code = QTextEdit()
        self.confirm_code.setReadOnly(True)
        self.confirm_code.setFont(QFont("Consolas", 12))
        self.confirm_code.setStyleSheet("padding: 10px; background: #f8faff; border-radius: 6px;")
        left.addWidget(self.confirm_code)
        left.addWidget(QLabel("<b>AST (JSON)</b>"))
        self.confirm_ast = QTextEdit()
        self.confirm_ast.setReadOnly(True)
        self.confirm_ast.setFont(QFont("Consolas", 11))
        self.confirm_ast.setStyleSheet("padding: 10px; background: #f8faff; border-radius: 6px;")
        left.addWidget(self.confirm_ast)
        # Right panel widgets
        right_container_layout.addWidget(QLabel("<b>AST Tree</b>"))
        self.confirm_tree = QLabel("AST Tree will appear here.")
        self.confirm_tree.setAlignment(Qt.AlignCenter)
        self.confirm_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Remove min/max size constraints so it fills the pane
        self.confirm_tree.setStyleSheet("""
            background: #f8faff;
            border-radius: 16px;
            margin: 0px 0px 0px 0px;
            padding: 30px 30px 30px 30px;
        """)
        self.confirm_tree.mousePressEvent = self.enlarge_ast_image
        right_container_layout.addWidget(self.confirm_tree, stretch=1)
        self.confirm_nodes = QLabel("Number of AST Nodes: 0")
        self.confirm_nodes.setAlignment(Qt.AlignCenter)
        self.confirm_nodes.setStyleSheet("background: #e3f2fd; border-radius: 6px; margin: 10px; padding: 10px; font-weight: bold;")
        right_container_layout.addWidget(self.confirm_nodes)
        self.timing_label = QLabel("AST Generation Time: 0.0s")
        self.timing_label.setAlignment(Qt.AlignCenter)
        self.timing_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4A90E2, stop:1 #50E3C2);
            color: white;
            border-radius: 6px;
            margin: 10px;
            padding: 10px;
            font-weight: bold;
            font-size: 14px;
        """)
        right_container_layout.addWidget(self.timing_label)
        layout.addLayout(left, 2)
        layout.addWidget(right_container, 1)
        return widget

    def enlarge_ast_image(self, event):
        if os.path.exists(TREE_FILE):
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
            dlg = QDialog(self)
            dlg.setWindowTitle("AST Tree - Full View")
            dlg.setMinimumSize(900, 700)
            vbox = QVBoxLayout(dlg)
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(TREE_FILE)
            img_label.setPixmap(pixmap.scaled(850, 650, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            vbox.addWidget(img_label)
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dlg.accept)
            vbox.addWidget(close_btn)
            dlg.exec_()

    def refresh_history(self):
        self.history_combo.clear()
        self.user_action_list.clear()
        if not os.path.exists(HISTORY_DIR):
            os.makedirs(HISTORY_DIR)
        files = sorted([f for f in os.listdir(HISTORY_DIR) if f.endswith('.py')], reverse=True)
        for f in files:
            self.history_combo.addItem(f)
            # Add item with tooltip preview
            item = QListWidgetItem(f)
            file_path = os.path.join(HISTORY_DIR, f)
            preview = ""
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    preview = file.read()
            lines = preview.splitlines()
            if len(lines) > 20:
                preview = '\n'.join(lines[:20]) + '\n...'
            if len(preview) > 500:
                preview = preview[:500] + '\n...'
            item.setToolTip(preview)
            self.user_action_list.addItem(item)
        # If no history, clear code editor, entity panel, and confirmation widget
        if len(files) == 0:
            self.code_edit.clear()
            self.entity_text.clear()
            self.update_confirmation_widget()

    def load_history_entry(self, idx):
        files = sorted([f for f in os.listdir(HISTORY_DIR) if f.endswith('.py')], reverse=True)
        if 0 <= idx < len(files):
            file_path = os.path.join(HISTORY_DIR, files[idx])
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            self.code_edit.setPlainText(code)
            self.process_code(load_only=True)

    def process_code(self, load_only=False):
        code = self.code_edit.toPlainText()
        with open(SOURCE_FILE, 'w', encoding='utf-8') as f:
            f.write(code)
        # Check for valid Python syntax and undefined variables
        try:
            compile(code, '<string>', 'exec')
        except (SyntaxError, NameError) as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Error: {e}\nNo lexical analysis or parsing will be performed.")
            msg_box.exec_()
            return
        if not load_only:
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(os.path.join(HISTORY_DIR, f'source_{timestamp}.py'), 'w', encoding='utf-8') as f:
                f.write(code)
            self.refresh_history()
            self.history_combo.setCurrentIndex(0)
        try:
            start_time = time.time()
            subprocess.run([sys.executable, 'lexer.py'], cwd=BACKEND_DIR, check=True)
            subprocess.run([sys.executable, 'parser.py'], cwd=BACKEND_DIR, check=True)
            subprocess.run([sys.executable, 'ast_visualizer.py'], cwd=BACKEND_DIR, check=True)
            end_time = time.time()
            self.timing_label.setText(f"AST Generation Time: {end_time - start_time:.3f}s")
        except subprocess.CalledProcessError as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Pipeline Error")
            msg_box.setText(f"Error running pipeline: {e}")
            msg_box.exec_()
            return
        self.update_entity_widget()
        self.update_confirmation_widget()

    def update_entity_widget(self):
        code = self.code_edit.toPlainText()
        if not code.strip():
            self.entity_text.setPlainText("")
            return
        tokens_file = os.path.join(BACKEND_DIR, 'tokens.json')
        if os.path.exists(tokens_file):
            with open(tokens_file, 'r', encoding='utf-8') as f:
                tokens = json.load(f)
            operators = set()
            functions = set()
            for i, token in enumerate(tokens):
                if token[0] == "OPERATOR":
                    operators.add(token[1])
                if token[0] == "IDENTIFIER":
                    if i + 1 < len(tokens) and tokens[i + 1][0] == "SEPARATOR" and tokens[i + 1][1] == "(":
                        functions.add(token[1])
            text = f"Operators: {sorted(list(operators))}\n\nFunctions: {sorted(list(functions))}"
            self.entity_text.setPlainText(text)
        else:
            self.entity_text.setPlainText("No tokens.json found.")

    def update_confirmation_widget(self):
        code = self.code_edit.toPlainText()
        has_history = self.history_combo.count() > 0
        if not code.strip() and not has_history:
            self.confirm_code.setPlainText("")
            self.confirm_ast.setPlainText("No recent data present.")
            self.confirm_tree.clear()
            self.confirm_tree.setText("No recent data present.")
            self.confirm_nodes.setText("Number of AST Nodes: 0")
            self.timing_label.setText("AST Generation Time: 0.0s")
            return
        self.confirm_code.setPlainText(code)
        if os.path.exists(AST_FILE):
            try:
                with open(AST_FILE, 'r', encoding='utf-8') as f:
                    ast_content = f.read()
                    self.confirm_ast.setPlainText(ast_content)
                    # Count the number of nodes in the AST JSON
                    try:
                        ast_data = json.loads(ast_content)
                        if isinstance(ast_data, dict) and "body" in ast_data:
                            node_count = len(ast_data["body"])
                        else:
                            node_count = 0
                        self.confirm_nodes.setText(f"Number of AST Nodes: {node_count}")
                    except json.JSONDecodeError:
                        self.confirm_nodes.setText("Number of AST Nodes: Error parsing JSON")
            except Exception as e:
                self.confirm_ast.setPlainText(f"Error reading AST file: {str(e)}")
                self.confirm_nodes.setText("Number of AST Nodes: Error")
        else:
            self.confirm_ast.setPlainText("AST JSON not found.")
            self.confirm_nodes.setText("Number of AST Nodes: 0")
        if os.path.exists(TREE_FILE):
            self.confirm_tree.clear()
            pixmap = QPixmap()
            for _ in range(3):
                pixmap = QPixmap(TREE_FILE)
                if not pixmap.isNull():
                    break
                time.sleep(0.1)
            if not pixmap.isNull():
                label_width = self.confirm_tree.width()
                label_height = self.confirm_tree.height()
                self.confirm_tree.setPixmap(
                    pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            else:
                self.confirm_tree.setText("AST Tree image could not be loaded.")
        else:
            self.confirm_tree.setText("AST Tree image not found.")

    def clear_code_editor(self):
        self.code_edit.clear()

    def delete_selected_history(self):
        item = self.user_action_list.currentItem()
        if item:
            file_name = item.text()
            file_path = os.path.join(HISTORY_DIR, file_name)
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "Delete History", f"Are you sure you want to delete '{file_name}'?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    os.remove(file_path)
                    # Also delete related JSON and PNG if they exist
                    base, _ = os.path.splitext(file_name)
                    json_path = os.path.join(HISTORY_DIR, base + ".json")
                    png_path = os.path.join(HISTORY_DIR, base + ".png")
                    if os.path.exists(json_path):
                        os.remove(json_path)
                    if os.path.exists(png_path):
                        os.remove(png_path)
                    self.refresh_history()
                    QMessageBox.information(self, "Delete History", f"'{file_name}' deleted successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete file: {e}")

    def load_selected_history(self):
        item = self.user_action_list.currentItem()
        if item:
            file_name = item.text()
            file_path = os.path.join(HISTORY_DIR, file_name)
            from PyQt5.QtWidgets import QMessageBox
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                self.code_edit.setPlainText(code)
                self.process_code(load_only=True)
                QMessageBox.information(self, "Load History", f"'{file_name}' loaded successfully.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ASTDesktopApp()
    window.show()
    sys.exit(app.exec_()) 