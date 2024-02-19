import json
import sys
import traceback

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


def format_json(text, indent=True):
    try:
        data = json.loads(text)
    except json.decoder.JSONDecodeError as e:
        return (e.lineno, e.colno, e.pos), False
    else:
        text = json.dumps(data, indent=indent, ensure_ascii=False)
        return text, True


class MainUi(QWidget):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        self.start()
    
    def start(self):
        self.resize(640, 480)
        self.text_edit = QTextEdit()
        self.pb_format = QPushButton('格式化')
        self.main_layout.addWidget(self.text_edit)
        self.main_layout.addWidget(self.pb_format)
        self.pb_format.clicked.connect(self.slot_to_format)
        self.text_edit.setText(
                """{"os_crypt":{"audit_enabled":true,"encrypted_key":"RFBBUEkBAAAA0Iyd3wEV0RGMegDAT8KX6wEAAACmkTbmRa7WT4Xf3JvL2LKOEAAAABIAAABDAGgAcgBvAG0AaQB1AG0AAAAQZgAAAAEAACAAAAAKK0HcZutM1RtUI2ojD7aiZz1LV1kief1ykPhI8W+l6gAAAAAOgAAAAAIAACAAAAA9GjC/rZpzY2LPE/fOkkEbb5HtMKHmQvDY1v10aRjvUDAAAAB6FYgQqQKC2rTVebP8GXR14j9Uab9CmE8q/Vn23gKHiVKWl31MpqhdK0uBhMBKK1lAAAAAfewPH1WD+ke8droSLmJH7oKUCJ5VbSmeBpHP7JtUx/8S/c2FFdh9tbR6kuF7ob2JAlRfRHJeAyO26dTgOt29XA=="},"profile_network_context_service":{"http_cache_finch_experiment_groups":"None None None None"},"updateclientdata":{"apps":{"oimompecagnajdejgnnjijobebaeigek":{"cohort":"1:1zdx:","cohorthint":"Chrome 106+","cohortname":"Chrome 106+","dlrc":6232,"fp":"1.2903aec9f77378fa19280af8ff89294fb9ce2caf8e0092c69e19973c0a9cc6fe","installdate":5958,"pf":"decda75c-4451-4cbd-b4ff-68f38393bfeb","pv":"4.10.2710.0"}}}}""")
        self.text_edit.setCursorWidth(2)
    
    def slot_to_format(self):
        text = self.text_edit.toPlainText()
        text, ok = format_json(text, indent=4)
        self.text_edit.setFocus()
        if not ok:
            self.cursor_to(*text)
            return
        self.text_edit.setText(text)
    
    def cursor_to(self, row, col, pos):
        cursor: QTextCursor = self.text_edit.textCursor()
        # cursor.movePosition(QTextCursor.Start)
        # cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, row - 1)
        # cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, col - 1)
        cursor.setPosition(pos)
        self.text_edit.setTextCursor(cursor)


if __name__ == '__main__':
    """
    Main run
    """
    
    app = QApplication(sys.argv)
    
    ui = MainUi()
    ui.show()
    
    sys.exit(app.exec_())

