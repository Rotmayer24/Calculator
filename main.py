from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QListWidget, QAbstractItemView
from PyQt5.QtCore import Qt
from function import calculate_expression
import json
import os
import math
from fractions import Fraction
from PyQt5 import QtCore as qtcore

HISTORY_FILE = "history.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setGeometry(100, 100, 400, 650)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.label = QLabel("0")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label.setStyleSheet("font-size: 24px; color: #fff; background: #222; padding: 10px; border-radius: 5px;")
        self.main_layout.addWidget(self.label)

        self.line_edit = QLineEdit()
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.line_edit.setReadOnly(True)
        self.line_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.line_edit.setStyleSheet("font-size: 20px; color: #fff; background: #333; padding: 8px; border-radius: 5px;")
        self.main_layout.addWidget(self.line_edit)

        # Сетка кнопок
        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)

        buttons = [
            ('C', 0, 0), ('Back', 0, 1), ('%', 0, 2), ('/', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('*', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0), ('History', 4, 1), ('.', 4, 2), ('=', 4, 3),
            ('Расширенное', 5, 0, 1, 4)
        ]

        self.button_map = {}
        for btn in buttons:
            if len(btn) == 5:
                text, row, col, rowspan, colspan = btn
            else:
                text, row, col = btn
                rowspan, colspan = 1, 1
            button = QPushButton(text)
            button.setFixedSize(70 * colspan, 50 * rowspan)
            button.setStyleSheet(
                """
                QPushButton {
                    font-size: 18px;
                    background: #444;
                    color: #fff;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:pressed {
                    background: #666;
                }
                """
            )
            self.grid_layout.addWidget(button, row, col, rowspan, colspan)
            self.button_map[text] = button

        # Привязка сигналов
        self.button_map['C'].clicked.connect(self.button_clear_clicked)
        self.button_map['Back'].clicked.connect(self.button_backspace_clicked)
        self.button_map['='].clicked.connect(self.button_equal_clicked)
        self.button_map['%'].clicked.connect(self.button_percent_clicked)
        self.button_map['History'].clicked.connect(self.button_history_clicked)
        self.button_map['.'].clicked.connect(self.input_dot)
        self.button_map['Расширенное'].clicked.connect(self.toggle_advanced_panel)
        for n in '0123456789':
            self.button_map[n].clicked.connect(lambda _, x=n: self.input_number(x))
        for op in ['+', '-', '*', '/']:
            self.button_map[op].clicked.connect(lambda _, x=op: self.input_operator(x))

        # Тёмная тема для всего окна
        self.setStyleSheet("""
            QWidget {
                background: #222;
            }
        """)

        # Панель расширенных функций (скрыта по умолчанию)
        self.advanced_panel = QWidget()
        self.advanced_layout = QGridLayout()
        self.advanced_panel.setLayout(self.advanced_layout)
        self.main_layout.addWidget(self.advanced_panel)
        self.advanced_panel.setVisible(False)

        adv_buttons = [
            ('(', 0, 0), (')', 0, 1), ('^', 0, 2), ('Fraction', 0, 3),
            ('sqrt', 1, 0), ('pow', 1, 1), ('sin', 1, 2), ('cos', 1, 3),
            ('tan', 2, 0), ('log', 2, 1), ('exp', 2, 2), ('pi', 2, 3),
            ('e', 3, 0)
        ]
        for text, row, col in adv_buttons:
            button = QPushButton(text)
            button.setFixedSize(70, 50)
            button.setStyleSheet(
                """
                QPushButton {
                    font-size: 16px;
                    background: #555;
                    color: #fff;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:pressed {
                    background: #888;
                }
                """
            )
            button.clicked.connect(lambda _, t=text: self.insert_advanced_func(t))
            self.advanced_layout.addWidget(button, row, col)

        self.reset()
        self.ensure_history_file()

    def ensure_history_file(self):
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w") as f:
                json.dump([], f)

    def add_to_history(self, expression, result):
        self.ensure_history_file()
        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)
        history.append({"expression": expression, "result": result})
        with open(HISTORY_FILE, "w") as file:
            json.dump(history, file, ensure_ascii=False, indent=2)

    def reset(self):
        self.current_input = ""
        self.line_edit.setText("")
        self.label.setText("0")

    def input_number(self, num):
        self.current_input += num
        self.line_edit.setText(self.current_input)

    def input_operator(self, op):
        if self.current_input and self.current_input[-1] not in "+-*/.%^":
            self.current_input += op
            self.line_edit.setText(self.current_input)

    def input_dot(self):
        if not self.current_input or not self.current_input[-1].isdigit():
            self.current_input += "0."
        elif "." not in self.current_input.split(" ")[-1]:
            self.current_input += "."
        self.line_edit.setText(self.current_input)

    def button_equal_clicked(self):
        try:
            expr = self.current_input.replace('^', '**')
            result = calculate_expression(expr)
            self.label.setText(str(result))
            self.line_edit.setText(str(result))
            self.add_to_history(self.current_input, result)
            self.current_input = str(result)
        except Exception as e:
            self.label.setText(str(e))

    def button_clear_clicked(self):
        self.reset()

    def button_backspace_clicked(self):
        self.current_input = self.current_input[:-1]
        self.line_edit.setText(self.current_input)

    def button_percent_clicked(self):
        if self.current_input and self.current_input[-1].isdigit():
            self.current_input += "%"
            self.line_edit.setText(self.current_input)

    def button_history_clicked(self):
        self.history_window = HistoryWindow()
        self.history_window.show()

    def toggle_advanced_panel(self):
        self.advanced_panel.setVisible(not self.advanced_panel.isVisible())

    def insert_advanced_func(self, text):
        if text == 'Fraction':
            self.current_input += 'Fraction(,)'
            self.line_edit.setText(self.current_input)
            self.line_edit.setCursorPosition(len(self.current_input) - 1)
        elif text in ['sqrt', 'pow', 'sin', 'cos', 'tan', 'log', 'exp']:
            self.current_input += f'{text}('
            self.line_edit.setText(self.current_input)
            self.line_edit.setCursorPosition(len(self.current_input))
        elif text in ['pi', 'e']:
            self.current_input += text
            self.line_edit.setText(self.current_input)
            self.line_edit.setCursorPosition(len(self.current_input))
        else:
            self.current_input += text
            self.line_edit.setText(self.current_input)
            self.line_edit.setCursorPosition(len(self.current_input))

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        # Цифры
        if text.isdigit():
            self.input_number(text)
        # Операторы
        elif text in '+-*/':
            self.input_operator(text)
        # Точка
        elif text == '.':
            self.input_dot()
        # Скобки
        elif text == '(': 
            self.insert_advanced_func('(')
        elif text == ')':
            self.insert_advanced_func(')')
        # Ввод (Enter/Return)
        elif key in (qtcore.Qt.Key_Return, qtcore.Qt.Key_Enter):
            self.button_equal_clicked()
        # Backspace
        elif key == qtcore.Qt.Key_Backspace:
            self.button_backspace_clicked()
        # Delete (очистка)
        elif key == qtcore.Qt.Key_Delete:
            self.button_clear_clicked()
        # Расширенные функции по первым буквам
        elif text.lower() == 's':
            self.insert_advanced_func('sin(')
        elif text.lower() == 'c':
            self.insert_advanced_func('cos(')
        elif text.lower() == 't':
            self.insert_advanced_func('tan(')
        elif text.lower() == 'l':
            self.insert_advanced_func('log(')
        elif text.lower() == 'e':
            self.insert_advanced_func('exp(')
        elif text.lower() == 'p':
            self.insert_advanced_func('pi')
        elif text.lower() == 'q':
            self.insert_advanced_func('sqrt(')
        elif text.lower() == 'f':
            self.insert_advanced_func('Fraction(,)')
            self.line_edit.setCursorPosition(len(self.current_input) - 1)
        # Степень
        elif text == '^':
            self.input_operator('^')
        else:
            super().keyPressEvent(event)

class AdvancedWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Расширенные функции")
        self.setGeometry(200, 200, 350, 350)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.grid = QGridLayout()
        self.central_widget.setLayout(self.grid)
        self.main_window = main_window
        adv_buttons = [
            ('(', 0, 0), (')', 0, 1), ('^', 0, 2), ('Fraction', 0, 3),
            ('sqrt', 1, 0), ('pow', 1, 1), ('sin', 1, 2), ('cos', 1, 3),
            ('tan', 2, 0), ('log', 2, 1), ('exp', 2, 2), ('pi', 2, 3),
            ('e', 3, 0)
        ]
        for text, row, col in adv_buttons:
            button = QPushButton(text)
            button.setFixedSize(70, 50)
            button.setStyleSheet(
                """
                QPushButton {
                    font-size: 16px;
                    background: #555;
                    color: #fff;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:pressed {
                    background: #888;
                }
                """
            )
            button.clicked.connect(lambda _, t=text: self.insert_func(t))
            self.grid.addWidget(button, row, col)

    def insert_func(self, text):
        if text == 'Fraction':
            self.main_window.insert_advanced('Fraction(,)')
            self.main_window.line_edit.setCursorPosition(len(self.main_window.current_input) - 1)
        elif text in ['sqrt', 'pow', 'sin', 'cos', 'tan', 'log', 'exp']:
            self.main_window.insert_advanced(f'{text}(')
        elif text in ['pi', 'e']:
            self.main_window.insert_advanced(text)
        else:
            self.main_window.insert_advanced(text)

class HistoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("History")
        self.setGeometry(150, 150, 400, 500)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.history_layout = QVBoxLayout()
        self.central_widget.setLayout(self.history_layout)
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.history_list.setStyleSheet("font-size: 16px; color: #fff; background: #333; border-radius: 8px; padding: 8px;")
        self.history_layout.addWidget(self.history_list)
        self.clear_btn = QPushButton("Очистить историю")
        self.clear_btn.setStyleSheet("font-size: 16px; background: #444; color: #fff; border-radius: 8px; padding: 8px;")
        self.clear_btn.clicked.connect(self.clear_history)
        self.history_layout.addWidget(self.clear_btn)
        self.load_history()

    def load_history(self):
        self.history_list.clear()
        if not os.path.exists(HISTORY_FILE):
            return
        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)
        for item in history:
            expr = item.get("expression", "")
            res = item.get("result", "")
            self.history_list.addItem(f"{expr} = {res}")

    def clear_history(self):
        with open(HISTORY_FILE, "w") as file:
            json.dump([], file)
        self.load_history()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())





