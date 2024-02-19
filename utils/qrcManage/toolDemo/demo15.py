import sys

from PyQt5.QtGui import QTextBlockFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.init_ui()
    
    def init_ui(self):
        self.text_edit = QTextEdit()
        self.label = QLabel('指定位置：')
        
        self.position_input = QTextEdit()
        self.position_input.setMaximumHeight(30)
        
        self.move_button = QPushButton('移动光标')
        self.move_button.clicked.connect(self.move_cursor)
        
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(self.text_edit)
        
        position_layout = QHBoxLayout()
        position_layout.addWidget(self.label)
        position_layout.addWidget(self.position_input)
        position_layout.addWidget(self.move_button)
        
        central_layout.addLayout(position_layout)
        self.setCentralWidget(central_widget)
        
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('移动光标示例')
        self.show()
    
    def move_cursor(self):
        position_text = self.position_input.toPlainText()
        try:
            position = int(position_text)
            cursor = self.text_edit.textCursor()
            cursor.setPosition(position)
            # 启用可视导航，使光标变宽
            cursor.setVisualNavigation(True)
            # cursor.selectionStart()
            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()  # 设置焦点
            self.text_edit.setCursorWidth(5)
        except ValueError:
            print("请输入有效的位置")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = TextEditor()
    sys.exit(app.exec_())
