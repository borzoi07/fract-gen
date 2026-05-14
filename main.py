import sys
import os
from numba import njit, prange
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, QComboBox, QLineEdit, QFrame, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QImage, QPixmap, QColor, QKeySequence, QShortcut, QGuiApplication, QShowEvent
from PyQt6.QtCore import Qt, QTimer
from fract import Fract, Renderer, arr_to_qimage

# 14/05/2026 TODO #
"""
- ADD PROPER UI ELEMENT PLACEMENTS
- ADD COLORMAP CHOICE combobox
- ADD ITERATION CHOICE input
- ADD FPS CHOICE input
https://en.wikipedia.org/wiki/Julia_set
"""

class MainFrame(QWidget):
    def __init__(self, switch_callback, fractal: Fract, fract_frame):
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
        self.fract_frame = fract_frame

        # test # TODO: REMOVE WHEN DONE TESTING
        btn_iter = QPushButton("Iter")
        #layout.addWidget(btn_iter)
        #btn_iter.clicked.connect(self.increase_iter)
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
        layout.addWidget(start_btn, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        

        checkboxes = QVBoxLayout()
        self.disable_zoom = QCheckBox('Disable Zoom?')
        self.enable_disk_save = QCheckBox('Save frames to Disk?')
        self.enable_h_mirror = QCheckBox('Mirror fractal horizontally?')
        for c in (self.disable_zoom, self.enable_disk_save, self.enable_h_mirror):
            c.setStyleSheet("QCheckBox { color: white; padding: 6px; }  QCheckBox::indicator:hover { background-color: #97978f; border: 1px #deded1; } QCheckBox::indicator:checked { background-color: green; border: 1px solid lightgreen; }")
            checkboxes.addWidget(c)
        layout.addLayout(checkboxes, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)

        self.disable_zoom.stateChanged.connect(self.on_zoom_change)
        self.enable_disk_save.stateChanged.connect(self.on_save_change)
        self.enable_h_mirror.stateChanged.connect(self.on_mirror_change)


        comboboxes = QVBoxLayout()
        comboboxes.setContentsMargins(0, 3, 0, 3)
        self.fract_type = QComboBox()
        self.fract_type.addItems(['Mandelbrot Set', 'Julia Set'])
        self.fract_type.currentTextChanged.connect(self.on_fract_type_change)      

        self.julia_sets = QComboBox()
        self.julia_sets.addItems(['Dendrite', 'San Marco Dragon', "Douady's Rabbit", 'Siegel Disk', 'ANIMATION: [0, 2pi]', 'SET: Custom Constant'])

        input_l = QHBoxLayout()
        self.r_input = QLineEdit()
        self.i_input = QLineEdit()
        self.r_input.setPlaceholderText("real part")
        self.i_input.setPlaceholderText("imag part")
        self.r_input.setFixedSize(90 ,35)
        self.i_input.setFixedSize(90 ,35)
        for i in (self.r_input, self.i_input):
            i.setStyleSheet("color: white; background-color: #333; padding: 10px;")
        self.r_input.returnPressed.connect(self.apply_custom_c)
        self.i_input.returnPressed.connect(self.apply_custom_c)
        input_l.addWidget(self.r_input)
        input_l.addWidget(self.i_input)

        self.set_info = QLabel("")
        self.set_info.setStyleSheet("color: white; padding: 100px")
        self.julia_sets.currentTextChanged.connect(self.update_set_info)

        comboboxes.addWidget(self.set_info)
        comboboxes.addWidget(self.fract_type)
        comboboxes.addWidget(self.julia_sets)
        comboboxes.addLayout(input_l)

        self.r_input.hide()
        self.i_input.hide()
        self.julia_sets.hide()
        self.set_info.hide()

        layout.addLayout(comboboxes, 1, 0, alignment=Qt.AlignmentFlag.AlignHCenter)

        if self.fract_type.currentText() == "Julia Set":
            self.fract.is_mandelbrot = False
            self.julia_sets.show()
            self.set_info.show()
            self.fract_frame.reset()
        else:
            self.fract.is_mandelbrot = True
            self.julia_sets.hide()
            self.set_info.hide()
            self.r_input.hide()
            self.i_input.hide()
            self.fract_frame.reset()          


        controls_text = QLabel("Left-Click to Zoom\nRight-Click to Reset View\nESC to return to this menu")
        controls_text.setStyleSheet("color: white; padding: 6px; ")
        layout.addWidget(controls_text, 4, 0, alignment=Qt.AlignmentFlag.AlignBottom)


        #self.loading_text = QLabel("")
        #self.loading_text.setStyleSheet("color: white; ")
        #layout.addWidget(self.loading_text, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # TODO: process events is not going to be needed once render thread is implemented
        # here in the lambda there's an expression with functions returning None
        # the or operator ensures each expression runs in sequence, return value doesn't matter
        #start_btn.clicked.connect(lambda: (self.loading_text.setText("Rendering...") or QApplication.processEvents()))

        # when clicked, switch to fractal view
        start_btn.clicked.connect(switch_callback)

    # TODO: DEPRECATED REMOVE LATER
    def increase_iter(self):
        if self.fract.ITERATIONS <= 0:
            return
        
        self.fract.ITERATIONS -= 10
        print("Iterations:", self.fract.ITERATIONS)

    def on_fract_type_change(self, text):
        if text == "Julia Set":
            self.fract.is_mandelbrot = False
            self.julia_sets.show()
            self.set_info.show()
            self.fract_frame.reset()
        else:
            self.fract.is_mandelbrot = True
            self.julia_sets.hide()
            self.set_info.hide()
            self.r_input.hide()
            self.i_input.hide()
            self.fract_frame.reset()

    def update_set_info(self, text):
        match text:
            case 'Dendrite':
                self.set_info.setText("C = 0 + 1j")
                self.fract.c_const = complex(0.0, 1.0)
                self.fract_frame.reset()
            case 'San Marco Dragon':
                self.set_info.setText("C = -0.75 + 0j\nEdge of the Mandelbrot set")
                self.fract.c_const = complex(-0.75, 0)
                self.fract_frame.reset()
            case "Douady's Rabbit":
                self.set_info.setText("C = -0.123, 0.745j")
                self.fract.c_const = complex(-0.123, 0.745)
                self.fract_frame.reset()
            case 'Siegel Disk':
                self.set_info.setText("-0.39054, -0.58679j")
                self.fract.c_const = complex(-0.39054, -0.58679)
                self.fract_frame.reset()
            case _:
                self.set_info.setText("")
        
        if text == 'ANIMATION: [0, 2pi]':
            self.set_info.setText("z^2 + 0.7885*e^(ia)\nWhere a ranges from [0,2pi]")
            self.fract.INTERVAL_ANIM = True
            self.fract_frame.reset()
        else:
            self.fract.INTERVAL_ANIM = False
            self.fract_frame.reset()

        if text == 'SET: Custom Constant':
            self.set_info.setText("Choose a C complex num (only enter an int/float)")
            self.r_input.show()
            self.i_input.show()
        else:
            self.r_input.hide()
            self.i_input.hide()

    def apply_custom_c(self):
        try:
            real = float(self.r_input.text())
            imag = float(self.i_input.text())
            self.fract.c_const = complex(real, imag)
            self.set_info.setText(f"C = {real} + {imag}j")
            self.fract_frame.request_render()
            self.fract_frame.reset()
        except ValueError:
            self.set_info.setText("Invalid input")

    def on_zoom_change(self):
        if self.disable_zoom.isChecked():
            self.fract.ZOOM = False
            self.fract_frame.reset()
        else:
            self.fract.ZOOM = True
            self.fract_frame.reset()

    def on_save_change(self):
        if self.enable_disk_save.isChecked():
            self.fract.SAVE_FRAMES = True
            self.fract_frame.reset()
        else:
            self.fract.SAVE_FRAMES = False
            self.fract_frame.reset()

    def on_mirror_change(self):
        if self.enable_h_mirror.isChecked():
            self.fract.MIRROR_H = True
            self.fract_frame.reset()
        else:
            self.fract.MIRROR_H = False
            self.fract_frame.reset()

        

class FractalFrame(QWidget):
    def __init__(self, switch_callback, fractal: Fract):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        self.fract = fractal

        self.label = QLabel()
        self.label.setFixedSize(self.fract.WIDTH, self.fract.HEIGHT)
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.x_min = self.fract.x_min_init
        self.x_max = self.fract.x_max_init
        self.y_min = self.fract.y_min_init
        self.y_max = self.fract.y_max_init
        self.target_real = (self.x_min + self.x_max) / 2.0
        self.target_imag = (self.y_min + self.y_max) / 2.0

        self.frame_idx = 0
        self.output_dir = "frames"
        if self.fract.SAVE_FRAMES:
            os.makedirs(self.output_dir, exist_ok=True)

        if self.fract.INTERVAL_ANIM:
            self.angle = 0.0   # start angle
            self.angle_step = 0.02  # radians per frame (~314 frames for full cycle)

        # thread
        self.worker = Renderer(self.fract)
        self.worker.frame_ready.connect(self.on_frame_ready)
        self.worker.start()

        # animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        #self.timer.start(self.fract.F_DELAY)

        # ESC key will trigger going back
        self.esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.esc_shortcut.activated.connect(switch_callback)

        #self.request_render()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            px = float(pos.x())
            py = float(pos.y())
            px = max(0.0, min(px, self.fract.WIDTH - 1))
            py = max(0.0, min(py, self.fract.HEIGHT - 1))
            real = self.x_min + (px / (self.fract.WIDTH - 1)) * (self.x_max - self.x_min)
            imag = self.y_min + (py / (self.fract.HEIGHT - 1)) * (self.y_max - self.y_min)
            self.target_real = real
            self.target_imag = imag
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.x_min = self.fract.x_min_init
            self.x_max = self.fract.x_max_init
            self.y_min = self.fract.y_min_init
            self.y_max = self.fract.y_max_init
            self.target_real = (self.x_min + self.x_max) / 2.0
            self.target_imag = (self.y_min + self.y_max) / 2.0
            self.request_render()
            event.accept()
        else:
            super().mousePressEvent(event)

    def update_frame(self):
        if self.fract.INTERVAL_ANIM:
            # c = 0.7885 * e^(i a)
            self.angle += self.angle_step
            if self.angle > 2 * np.pi:
                self.angle -= 2 * np.pi

            c_real = 0.7885 * np.cos(self.angle)
            c_imag = 0.7885 * np.sin(self.angle)

            self.fract.c_const = complex(c_real, c_imag)
            self.worker.request_render = True
            return

        if not self.fract.ZOOM:
            return
        # pan towards cursor
        cur_center_real = (self.x_min + self.x_max) / 2.0
        cur_center_imag = (self.y_min + self.y_max) / 2.0
        new_center_real = cur_center_real + (self.target_real - cur_center_real) * self.fract.PAN_LERP
        new_center_imag = cur_center_imag + (self.target_imag - cur_center_imag) * self.fract.PAN_LERP

        x_range = (self.x_max - self.x_min) * self.fract.ZOOM_FACTOR
        y_range = (self.y_max - self.y_min) * self.fract.ZOOM_FACTOR

        self.x_min = new_center_real - x_range / 2.0
        self.x_max = new_center_real + x_range / 2.0
        self.y_min = new_center_imag - y_range / 2.0
        self.y_max = new_center_imag + y_range / 2.0

        if x_range < 1e-12 or y_range < 1e-12:
            self.x_min = self.fract.x_min_init
            self.x_max = self.fract.x_max_init
            self.y_min = self.fract.y_min_init
            self.y_max = self.fract.y_max_init
            self.target_real = (self.x_min + self.x_max) / 2.0
            self.target_imag = (self.y_min + self.y_max) / 2.0

        self.fract.x_min = self.x_min
        self.fract.x_max = self.x_max
        self.fract.y_min = self.y_min
        self.fract.y_max = self.y_max
        self.worker.request_render = True

    def request_render(self):
        self.worker.request_render = True

    def on_frame_ready(self, rgb_array):
        # rgb_array is HxWx3 uint8 numpy array
        qimg = arr_to_qimage(rgb_array)
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)

        if self.fract.SAVE_FRAMES:
            filename = os.path.join(self.output_dir, f"frame_{self.frame_index:04d}.png")
            qimg.save(filename)
            self.frame_index += 1

    def closeEvent(self, event):
        self.worker.stop()
        super().closeEvent(event)

    def reset(self):
        # stop anim
        self.timer.stop()
        self.worker.request_render = False

        self.fract.x_min = self.fract.x_min_init
        self.fract.x_max = self.fract.x_max_init
        self.fract.y_min = self.fract.y_min_init
        self.fract.y_max = self.fract.y_max_init
        self.x_min = self.fract.x_min_init
        self.x_max = self.fract.x_max_init
        self.y_min = self.fract.y_min_init
        self.y_max = self.fract.y_max_init
        self.target_real = (self.x_min + self.x_max) / 2.0
        self.target_imag = (self.y_min + self.y_max) / 2.0

        if self.fract.SAVE_FRAMES:
            os.makedirs(self.output_dir, exist_ok=True)

        if self.fract.INTERVAL_ANIM:
            self.angle = 0.0   # start angle
            self.angle_step = 0.02  # radians per frame (~314 frames for full cycle)

        # clear display
        self.label.clear()
        self.label.repaint()
        self.frame_index = 0


    def _drawTestNumpy(self):
        x = np.arange(self.w)
        y = np.arange(self.h)

        X, Y = np.meshgrid(x, y)

        # Perform the XOR operation on the whole array
        # 0-255 grayscale pattern
        pattern = ((X ^ Y) % 9 == 0).astype(np.uint8) * 255

        qimg = QImage(pattern.data, self.w, self.h, self.w, QImage.Format.Format_Grayscale8)

        self.label.setPixmap(QPixmap.fromImage(qimg))


class UI_Win(QMainWindow):
    def __init__(self):
        super(UI_Win,self).__init__()
        self.w, self.h = 900, 700
        self.setFixedSize(self.w, self.h)
        self.setGeometry(950, 500, self.w, self.h)
        self.setWindowTitle("Fractal Simulation")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.fract = Fract(self.w, self.h)

        self.fract_frame = FractalFrame(self.show_main, self.fract)
        self.main_frame = MainFrame(self.show_fract, self.fract, self.fract_frame)

        self.stack.addWidget(self.main_frame) # idx 0
        self.stack.addWidget(self.fract_frame) # idx 1

        self.stack.setCurrentIndex(0) # mainframe 0, render 1

    def show_fract(self):
        self.fract_frame.timer.start(self.fract.F_DELAY)
        self.fract_frame.request_render()
        self.fract_frame.update()

        self.stack.setCurrentIndex(1)

    def show_main(self):
        self.fract_frame.reset()

        self.stack.setCurrentIndex(0)

def main():
    app = QApplication(sys.argv)
    window = UI_Win()

    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()