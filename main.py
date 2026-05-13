import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFrame, QWidget, QVBoxLayout, QStackedWidget
from PyQt6.QtGui import QImage, QPixmap, QColor, QKeySequence, QShortcut
from PyQt6.QtCore import QTimer
from fract_logic import Fract

# 13/05/2026 TODO #
"""
focus on improving the rendering with numpy
color using matplotlib colormaps
then after that's done add the main frame controls and input processing

add QThread Renderer (implement threading for fractal rendering logic)

after that add animations and mouse interactions which are can also be toggled in main frame
"""

class MainFrame(QWidget):
    def __init__(self, switch_callback, fractal: Fract):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.switch_callback = switch_callback

        self.fract = fractal

        # test
        btn_iter = QPushButton("Iter")
        layout.addWidget(btn_iter)
        btn_iter.clicked.connect(self.increase_iter)
        #

        start_btn = QPushButton("Start Fractal")
        start_btn.setStyleSheet("""
    QPushButton {
        background-color: lightblue;
        border-radius: 8px;
        padding: 6px;
    }
    QPushButton:hover {
        background-color: yellow;
    }
""")
        layout.addWidget(start_btn)

        self.loading_text = QLabel("")
        layout.addWidget(self.loading_text)

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
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.w, self.h = width, height
        self.rendering = True # TODO: add actual functionality to this later

        self.fract = fractal
        self.fract.zoom_mode = False
        self.fract.const_cR, self.fract.const_cI = 0.355, 0.405 # this one is in the Mandelbrot Set

        self.label = QLabel()
        layout.addWidget(self.label)

        # ESC key will trigger going back
        self.esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.esc_shortcut.activated.connect(switch_callback)

        self.drawJulia()

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
        #qimg = QImage(self.w, self.h, QImage.Format.Format_RGB32)
        #qimg.fill(QColor("black"))

        qimg = QImage(self.w, self.h, QImage.Format.Format_RGB32)
        qimg.fill(QColor("black"))

        for x in range(self.w):
            for y in range(self.h):
                qimg.setPixelColor(x, y, self.fract.julia(x, y, self.w, self.h, self.fract.const_cR, self.fract.const_cI))

        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)

        self.fract.zoom()

        #self.frame += 1
        #if self.frame > 200:
        #self.timer.stop()


class UI_Win(QMainWindow):
    def __init__(self):
        super(UI_Win,self).__init__()
        self.w, self.h = 800, 600

        #self.label = QLabel()
        #self.setCentralWidget(self.label)

        #self.image = QImage(800, 600, QImage.Format.Format_RGB32)
        #self.image.fill(QColor("black"))

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.fract = Fract()

        self.main_frame = MainFrame(self.show_fract, self.fract)
        self.fract_frame = FractalFrame(self.show_main, self.fract, self.w, self.h)

        self.stack.addWidget(self.main_frame) # idx 0
        self.stack.addWidget(self.fract_frame) # idx 1

        self.stack.setCurrentIndex(0) # mainframe 0, render 1

        self.setGeometry(950, 500, 600, 600)
        self.setWindowTitle("Fractal Simulation")

        self.frame = 0

        #self.timer = QTimer()
        #self.timer.timeout.connect(self.drawJulia)
        #self.timer.start(100)  # 100 ms/frame

        #self._drawTestNumpy()
        #self.SetupUI()

    def show_fract(self):
        self.stack.setCurrentIndex(1)
        self.fract_frame.drawJulia()
        self.fract_frame.update()
    def show_main(self):
        self.main_frame.loading_text.setText("")
        self.stack.setCurrentIndex(0)

"""
    def drawSim(self):
        # Plot pixels directly onto QImage
        for x in range(800):
            for y in range(600):
                if (x ^ y) % 9 == 0:
                    self.image.setPixelColor(x, y, QColor("cyan"))

        pixmap = QPixmap.fromImage(self.image)
        self.label.setPixmap(pixmap)
"""
        
"""
    def SetupUI(self):

        txt = QLabel(self)
        txt.setText("Test")

        txt.move(250, 250)

        btn = QPushButton(self)
        btn.move(250, 300)
        btn.setText("Click")
        btn.clicked.connect(self.on_clicked)

    def on_clicked(self):
        print("Pressed")
"""

def main():
    app = QApplication(sys.argv)
    window = UI_Win()

    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()