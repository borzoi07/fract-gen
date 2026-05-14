from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal
from matplotlib import colormaps
import numpy as np
from numba import njit, prange

def map_colors(arr, colormap='inferno'):
    max_val = arr.max()
    # normalize to [0, 1]
    if max_val == 0:
        norm = arr.astype(np.float32)
    else:
        norm = arr.astype(np.float32) / float(max_val)
    # retrieve a func from dict that maps values from [0, 1] to colors
    cmap = colormaps.get(colormap)
    colored = cmap(norm)[:, :, :3] # idk what this does but it works
    rgb_array = np.uint8(colored * 255)
    return rgb_array

def arr_to_qimage(arr) -> QImage:
    height, width, channels = arr.shape
    array_c = np.ascontiguousarray(arr, dtype=np.uint8)
    # each pixel has 3 channels (rgb) so one row of width pixels needs width × 3 bytes
    qimg = QImage(array_c.data, width, height, 3 * width, QImage.Format.Format_RGB888) # 3 channel format each 8 bits
    return qimg.copy()

class Fract():
    ITERATIONS = 200
    ZOOM_FACTOR = 0.988
    ZOOM = True
    PAN_LERP = 0.05 # default 0.12
    FPS = 30
    F_DELAY = int(1000 / FPS)
    MIRROR_H = False
    INTERVAL_ANIM = False
    SAVE_FRAMES = False

    x_min_init, x_max_init = -2.0, 2.0
    y_min_init, y_max_init = -1.5, 1.5

    is_mandelbrot = False

    def __init__(self, w, h):
        self.WIDTH, self.HEIGHT = w, h
    
        # complex plane window
        self.x_min, self.x_max = Fract.x_min_init, Fract.x_max_init
        self.y_min, self.y_max = Fract.y_min_init, Fract.y_max_init

        self.c_const = complex(0.355, 0.405) # this one is in the Mandelbrot Set
    
    @staticmethod
    @njit(parallel=True, fastmath=True)
    def mandelbrot(x_min, x_max, y_min, y_max, width, height, iterations, mirror_h):
        arr = np.empty((height, width), dtype=np.int32)
        # linear scaling formula
        # width and height minus 1 to include the edges of the max boundary [x_min, x_max]
        dx = (x_max - x_min) / (width - 1)
        dy = (y_max - y_min) / (height - 1)

        # run only the row level on separate threads
        # y row can be computed independently so there won't be race conditions
        for y in prange(height):
            imag = y_min + y * dy
            for x in range(width):
                real = x_min + (width - x if mirror_h else x) * dx
                cR = real
                cI = imag
                zr, zi = 0, 0 # declaring this outside prange will result in reduction error
                iteration = 0
                for itr in range(iterations):
                    # z = z*z + c but with explicit arithmetic instead of complex()
                    zr2 = zr * zr - zi * zi + cR
                    zi = 2.0 * zr * zi + cI
                    zr = zr2
                    if zr * zr + zi * zi > 4.0: # escape value
                        iteration = itr
                        break
                arr[y, x] = iteration
        
        return arr
    
    @staticmethod
    @njit(parallel=True, fastmath=True)
    def julia(x_min, x_max, y_min, y_max, width, height, iterations, c_real, c_imag, mirror_h):
        arr = np.empty((height, width), dtype=np.int32)
        cR, cI = c_real, c_imag
        # linear scaling formula
        # width and height minus 1 to include the edges of the max boundary [x_min, x_max]
        dx = (x_max - x_min) / (width - 1)
        dy = (y_max - y_min) / (height - 1)

        # run only the row level on separate threads
        # y row can be computed independently so there won't be race conditions
        for y in prange(height):
            imag = y_min + y * dy
            for x in range(width):
                real = x_min + (width - x if mirror_h else x) * dx
                zr = real
                zi = imag
                iteration = 0
                for itr in range(iterations):
                    # z = z*z + c but with explicit arithmetic instead of complex()
                    zr2 = zr * zr - zi * zi + cR
                    zi = 2.0 * zr * zi + cI
                    zr = zr2
                    if zr * zr + zi * zi > 4.0: # escape value
                        iteration = itr
                        break
                arr[y, x] = iteration
        
        return arr
    
        # Coloring method without matplotlib colormaps
        # QColor(iteration % 8 * 32, iteration % 16 * 16, iteration % 32 * 8)

class Renderer(QThread):
    frame_ready = pyqtSignal(object)

    def __init__(self, fractal: Fract):
        super(QThread,self).__init__()
        
        self.fract = fractal
        self.running = True
        self.request_render = True

    def run(self):
        # Keep rendering while thread is alive
        while self.running:
            if not self.request_render:
                self.msleep(5)
                continue
            # copy parameters locally to avoid race conditions
            xm, xM = self.fract.x_min, self.fract.x_max
            ym, yM = self.fract.y_min, self.fract.y_max
            max_it = self.fract.ITERATIONS
            cr, ci = self.fract.c_const.real, self.fract.c_const.imag
            mirror_h = self.fract.MIRROR_H

            if self.fract.is_mandelbrot:
                array = self.fract.mandelbrot(xm, xM, ym, yM, self.fract.WIDTH, self.fract.HEIGHT, max_it, mirror_h)
            else:
                array = self.fract.julia(xm, xM, ym, yM, self.fract.WIDTH, self.fract.HEIGHT, max_it, cr, ci, mirror_h)

            rgb = map_colors(array, colormap='inferno')

            self.frame_ready.emit(rgb)
            self.request_render = False

    def stop(self):
        self.running = False
        self.wait()     






"""
ITERATIONS = 50

def map_pixel(x, y, width, height):
    # complex plane window
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.5, 1.5

    # linear scaling formula
    real = x_min + (x / width) * (x_max - x_min)
    imag = y_min + (y / height) * (y_max - y_min)

    return complex(real, imag)

def mandelbrot(x, y, width, height):
    c = map_pixel(x, y, width, height)
    z = 0
    escape_val = 4

    iteration = 0
    while abs(z) <= escape_val and iteration < ITERATIONS:
        z = z*z + c
        iteration += 1

    if iteration == ITERATIONS:
        color = QColor("black")
    else:
        color = QColor(iteration % 8 * 32, iteration % 16 * 16, iteration % 32 * 8)

    return color

def julia(x, y, width, height, c_real, c_imag):
    c = complex(c_real, c_imag)
    z = map_pixel(x, y, width, height)
    escape_val = 4

    iteration = 0
    while abs(z) <= escape_val and iteration < ITERATIONS:
        z = z*z + c
        iteration += 1

    if iteration == ITERATIONS:
        color = QColor("black")
    else:
        color = QColor(iteration % 8 * 32, iteration % 16 * 16, iteration % 32 * 8)

    return color
"""