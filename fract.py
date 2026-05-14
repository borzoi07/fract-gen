from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtCore import QThread
from matplotlib import colormaps
import numpy as np
from numba import njit, prange

def map_colors(arr, colormap='inferno'):
    ...

def arr_to_qimage(arr):
    ...

class Fract():
    ITERATIONS = 50
    ZOOM_FACTOR = 0.95
    ZOOM = False
    PAN_LERP = 0.12
    FPS = 30
    F_DELAY = int(1000 / FPS)
    MIRROR_H = False

    x_min_init, x_max_init = -2.0, 2.0
    y_min_init, y_max_init = -1.5, 1.5

    def __init__(self):
        """
        self.ITERATIONS = 50
        self.zoom_factor = 0.95
        self.zoom_mode = True
        self.mirror_horizontally = False
        """
    
        # TODO: later will accept mouse input coords
        self.center_x, self.center_y = -0.75, 0.1

        # complex plane window
        self.x_min, self.x_max = Fract.x_min_init, Fract.x_max_init
        self.y_min, self.y_max = Fract.y_min_init, Fract.y_max_init

        self.c_const = complex(0.355, 0.405) # this one is in the Mandelbrot Set


    def map_pixel(self, x, y, width, height):
        # linear scaling formula
        # width and height minus 1 to include the edges of the max boundary [x_min, x_max] 
        if self.MIRROR_H:
            real = self.x_min + ((width - x) / (width - 1)) * (self.x_max - self.x_min)
            imag = self.y_min + (y / (height - 1)) * (self.y_max - self.y_min)
        else:
            real = self.x_min + (x / (width - 1)) * (self.x_max - self.x_min)
            imag = self.y_min + (y / (height - 1)) * (self.y_max - self.y_min)

        return real, imag # complex(real, imag)

    def mandelbrot(self, x, y, width, height):
        cR, cI = self.map_pixel(x, y, width, height)
        c = complex(cR, cI)
        z = 0
        escape_val = 2

        iteration = 0
        while abs(z) <= escape_val and iteration < self.ITERATIONS:
            z = z*z + c
            iteration += 1

        if iteration == self.ITERATIONS:
            color = QColor("black")
        else:
            color = QColor(iteration % 8 * 32, iteration % 16 * 16, iteration % 32 * 8)

        return color
    
    def julia(self, x, y, width, height, c):
        cR, cI = c.real, c.imag
        zr, zi = self.map_pixel(x, y, width, height)
        #escape_val = 2

        iteration = 0
        for itr in range(self.ITERATIONS):
            # z = z*z + c but with explicit arithmetic instead of complex()
            zr2 = zr * zr - zi * zi + cR
            zi = 2.0 * zr * zi + cI
            zr = zr2
            if zr * zr + zi * zi > 4.0: # escape value
                iteration = itr
                break

        if iteration == self.ITERATIONS:
            color = QColor("black")
        else:
            color = QColor(iteration % 8 * 32, iteration % 16 * 16, iteration % 32 * 8)

        return color
    
        # Coloring method without matplotlib colormaps
        # QColor(iteration % 8 * 32, iteration % 16 * 16, iteration % 32 * 8)


    def zoom(self):
        if self.ZOOM:
            x_range = (self.x_max - self.x_min) * self.ZOOM_FACTOR
            y_range = (self.y_max - self.y_min) * self.ZOOM_FACTOR

            self.x_min = self.center_x - x_range/2
            self.x_max = self.center_x + x_range/2
            self.y_min = self.center_y - y_range/2
            self.y_max = self.center_y + y_range/2



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