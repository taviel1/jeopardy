import sys
import random
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLabel,
    QMessageBox, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt


class Game(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("data/questions.db")
        self.cur = self.conn.cursor()
        self.setWindowTitle("Своя Игра")
        self.resize(900, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #1E3A8A;
                color: white;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #60A5FA;
            }
            QLabel {
                color: white;
            }
        """)

        self.score = 0
        self.used_questions = set()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.start_game()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.clear_layout(item.layout())

    def start_game(self):
        self.clear_layout(self.layout)
        top_bar = QHBoxLayout()

        new_game_btn = QPushButton("Новая игра")
        new_game_btn.setFixedWidth(150)
        new_game_btn.clicked.connect(self.restart_game)
        new_game_btn.setStyleSheet("background-color: #2563EB; font-weight: bold;")

        self.score_label = QLabel(f"Счёт: {self.score}")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.score_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        top_bar.addWidget(new_game_btn)
        top_bar.addStretch()
        top_bar.addWidget(self.score_label)

        grid = QGridLayout()
        categories = [row[0] for row in self.cur.execute("SELECT DISTINCT category FROM questions").fetchall()]
        self.categories = random.sample(categories, 5)

        for col, category in enumerate(self.categories):
            label = QLabel(category)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-weight: bold; font-size: 18px; margin: 5px;")
            grid.addWidget(label, 0, col)

            for row, points in enumerate([10, 20, 30, 40, 50]):
                btn = QPushButton(str(points))
                btn.setFixedSize(140, 70)
                btn.clicked.connect(lambda _, c=category, p=points: self.show_question(c, p))
                grid.addWidget(btn, row + 1, col)

        self.layout.addLayout(top_bar)
        self.layout.addLayout(grid)

    def show_question(self, category, points):
        question_data = self.cur.execute(
            "SELECT id, question, answer, option1, option2, option3, option4 FROM questions WHERE category=? AND points=?",
            (category, points)
        ).fetchone()

        if not question_data:
            QMessageBox.warning(self, "Ошибка", "Вопрос не найден.")
            return

        qid, question, correct, o1, o2, o3, o4 = question_data
        if qid in self.used_questions:
            QMessageBox.information(self, "Инфо", "Этот вопрос уже использован.")
            return
        self.used_questions.add(qid)

        options = [o1, o2, o3, o4]
        random.shuffle(options)

        qwin = QWidget()
        qwin.setWindowTitle(f"{category} — {points}")
        vbox = QVBoxLayout()
        qlabel = QLabel(question)
        qlabel.setWordWrap(True)
        qlabel.setStyleSheet("font-size: 18px; margin-bottom: 15px; color: black;")
        vbox.addWidget(qlabel)

        for opt in options:
            btn = QPushButton(opt)
            btn.setStyleSheet("""
                background-color: #3B82F6;
                color: white;
                border-radius: 10px;
                font-size: 16px;
            """)
            btn.clicked.connect(lambda _, b=btn, o=opt, c=correct, p=points, w=qwin: self.check_answer(b, o, c, p, w))
            vbox.addWidget(btn)

        qwin.setLayout(vbox)
        qwin.resize(500, 300)
        qwin.show()
        self.qwin = qwin

    def check_answer(self, button, chosen, correct, points, window):
        if chosen == correct:
            self.score += points
            button.setStyleSheet("background-color: #16A34A; color: white; font-size: 16px; border-radius: 10px;")
            QMessageBox.information(self, "Верно!", f"Ответ правильный!\nВаш счёт: {self.score}")
        else:
            button.setStyleSheet("background-color: #DC2626; color: white; font-size: 16px; border-radius: 10px;")
            QMessageBox.warning(self, "Ошибка", f"Неверно!\nПравильный ответ: {correct}\nВаш счёт: {self.score}")
        self.score_label.setText(f"Счёт: {self.score}")
        window.close()

    def restart_game(self):
        confirm = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите начать новую игру?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.score = 0
            self.used_questions.clear()
            self.start_game()
            self.score_label.setText("Счёт: 0")


app = QApplication(sys.argv)
game = Game()
game.show()
sys.exit(app.exec())
