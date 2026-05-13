from PyQt6.QtGui import QColor

class Fract():
    def __init__(self):
        self.ITERATIONS = 50
        self.zoom_factor = 0.95
        self.zoom_mode = True
        self.mirror_horizontally = False

        # TODO: later will accept mouse input coords
        self.center_x, self.center_y = -0.75, 0.1

        # complex plane window
        self.x_min, self.x_max = -2.0, 1.0
        self.y_min, self.y_max = -1.5, 1.5

        self.const_cR, self.const_cI = 0.355, 0.405 # this one is in the Mandelbrot Set


    def map_pixel(self, x, y, width, height):
        # linear scaling formula
        if self.mirror_horizontally:
            real = self.x_min + ((width - x) / width) * (self.x_max - self.x_min)
            imag = self.y_min + (y / height) * (self.y_max - self.y_min)
        else:
            real = self.x_min + (x / width) * (self.x_max - self.x_min)
            imag = self.y_min + (y / height) * (self.y_max - self.y_min)

        return complex(real, imag)
    

    def zoom(self):
        if self.zoom_mode:
            x_range = (self.x_max - self.x_min) * self.zoom_factor
            y_range = (self.y_max - self.y_min) * self.zoom_factor

            self.x_min = self.center_x - x_range/2
            self.x_max = self.center_x + x_range/2
            self.y_min = self.center_y - y_range/2
            self.y_max = self.center_y + y_range/2


    def mandelbrot(self, x, y, width, height):
        c = self.map_pixel(x, y, width, height)
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
    
    def julia(self, x, y, width, height, c_real, c_imag):
        c = complex(c_real, c_imag)
        z = self.map_pixel(x, y, width, height)
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