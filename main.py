import sys
from numba import njit, prange
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFrame, QWidget, QVBoxLayout, QGridLayout, QStackedWidget, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QImage, QPixmap, QColor, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from fract import Fract

# 13/05/2026 TODO #
"""
focus on improving the rendering with numpy and numba
color using matplotlib colormaps
then after that's done add the main frame controls and input processing

add QThread Renderer (implement threading for fractal rendering logic)

after that add animations and mouse interactions which are can also be toggled in main frame

Implement Julia sets animation (no zoom animation) for:
z*z + 0.7885*e^ia where a ranges from 0 to 2pi

https://en.wikipedia.org/wiki/Julia_set
"""

class MainFrame(QWidget):
    def __init__(self, switch_callback, fractal: Fract):
        super().__init__()
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#1A1A1A"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.switch_callback = switch_callback

        self.fract = fractal

        # test
        btn_iter = QPushButton("Iter")
        layout.addWidget(btn_iter)
        btn_iter.clicked.connect(self.increase_iter)
        #

        start_btn = QPushButton("Start Rendering")
        start_btn.setStyleSheet("""
    QPushButton {
        background-color: #deded1;
        border-radius: 8px;
        padding: 6px;
        size: 
    }
    QPushButton:hover {
        background-color: #97978f;
    }
""")
        start_btn.setFixedSize(120, 40)
        layout.addWidget(start_btn, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        self.loading_text = QLabel("")
        self.loading_text.setStyleSheet("color: white; ")
        layout.addWidget(self.loading_text, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        # TODO: process events is not going to be needed once render thread is implemented
        # here in the lambda there's an expression with functions returning None
        # the or operator ensures each expression runs in sequence, return value doesn't matter
        start_btn.clicked.connect(lambda: (self.loading_text.setText("Rendering...") or QApplication.processEvents()))

        # when clicked, switch to fractal view
        start_btn.clicked.connect(switch_callback)

    def increase_iter(self):
        if self.fract.ITERATIONS <= 0:
            return
        
        self.fract.ITERATIONS -= 10
        print("Iterations:", self.fract.ITERATIONS)

class FractalFrame(QWidget):
    def __init__(self, switch_callback, fractal: Fract, width, height):
        super().__init__()
        self.w, self.h = width, height

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.rendering = True # TODO: add actual functionality to this later

        self.fract = fractal
        self.fract.zoom_mode = False
        self.fract.c_const = complex(0.355, 0.405) # this one is in the Mandelbrot Set

        self.label = QLabel()
        self.label.setFixedSize(self.w, self.h)
        layout.addWidget(self.label)

        # ESC key will trigger going back
        self.esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.esc_shortcut.activated.connect(switch_callback)


    def _drawTestNumpy(self):
        x = np.arange(self.w)
        y = np.arange(self.h)

        X, Y = np.meshgrid(x, y)

        # Perform the XOR operation on the whole array
        # 0-255 grayscale pattern
        pattern = ((X ^ Y) % 9 == 0).astype(np.uint8) * 255

        qimg = QImage(pattern.data, self.w, self.h, self.w, QImage.Format.Format_Grayscale8)

        self.label.setPixmap(QPixmap.fromImage(qimg))

    def drawMandelbrot(self):
        # TODO: Figure out a better way to color this with matplotlib
        # TODO: Add Looping Animation
        # TODO: Add Mouse Interactions With Animation
        qimg = QImage(self.w, self.h, QImage.Format.Format_RGB32)
        qimg.fill(QColor("black"))

        for x in range(self.w):
            for y in range(self.h):
                qimg.setPixelColor(x, y, self.fract.mandelbrot(x, y, self.w, self.h))
                pass
        
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)

    def drawJulia(self):
        qimg = QImage(self.w, self.h, QImage.Format.Format_RGB32)
        qimg.fill(QColor("black"))

        for x in range(self.w):
            for y in range(self.h):
                qimg.setPixelColor(x, y, self.fract.julia(x, y, self.w, self.h, self.fract.c_const))

        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)

        self.fract.zoom()


class UI_Win(QMainWindow):
    def __init__(self):
        super(UI_Win,self).__init__()
        self.w, self.h = 900, 700
        self.setFixedSize(self.w, self.h)
        self.setGeometry(950, 500, self.w, self.h)
        self.setWindowTitle("Fractal Simulation")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.fract = Fract()

        self.main_frame = MainFrame(self.show_fract, self.fract)
        self.fract_frame = FractalFrame(self.show_main, self.fract, self.w, self.h)

        self.stack.addWidget(self.main_frame) # idx 0
        self.stack.addWidget(self.fract_frame) # idx 1

        self.stack.setCurrentIndex(0) # mainframe 0, render 1

    def show_fract(self):
        self.stack.setCurrentIndex(1)
        self.fract_frame.drawJulia()
        self.fract_frame.update()
    def show_main(self):
        self.main_frame.loading_text.setText("")
        self.stack.setCurrentIndex(0)

def main():
    app = QApplication(sys.argv)
    window = UI_Win()

    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()