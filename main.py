import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt6.QtGui import QImage, QPixmap, QColor
from PyQt6.QtCore import QTimer
from fract_logic import Fract

class UI_Win(QMainWindow):
    def __init__(self):
        super(UI_Win,self).__init__()
        self.w, self.h = 800, 600

        self.label = QLabel()
        self.setCentralWidget(self.label)

        #self.image = QImage(800, 600, QImage.Format.Format_RGB32)
        #self.image.fill(QColor("black"))

        self.setGeometry(950, 500, 600, 600)
        self.setWindowTitle("Fractal Simulation")

        self.frame = 0

        #self.timer = QTimer()
        #self.timer.timeout.connect(self.drawJulia)
        #self.timer.start(100)  # 100 ms/frame

        self.const_cR, self.const_cI = 0.355, 0.405 # this one is in the Mandelbrot Set

        #self._drawTestNumpy()
        #self.SetupUI()

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
                #qimg.setPixelColor(x, y, mandelbrot(x, y, self.w, self.h))
                pass
        
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)

    def drawJulia(self):
        #qimg = QImage(self.w, self.h, QImage.Format.Format_RGB32)
        #qimg.fill(QColor("black"))

        qimg = QImage(self.w, self.h, QImage.Format.Format_RGB32)
        qimg.fill(QColor("black"))

        fract = Fract()
        fract.zoom_mode = False
        for x in range(self.w):
            for y in range(self.h):
                qimg.setPixelColor(x, y, fract.julia(x, y, self.w, self.h, self.const_cR, self.const_cI))

        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)

        fract.zoom()

        #self.frame += 1
        #if self.frame > 200:
        #self.timer.stop()


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

    #window.drawMandelbrot()
    window.drawJulia()

    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()