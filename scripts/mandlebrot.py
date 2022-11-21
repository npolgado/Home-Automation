import tkinter
import numpy as np
import cmath

root = tkinter.Tk()
root.title('Mandelbrot Set')

canvas = tkinter.Canvas(root, width=400, height=400)
canvas.pack()

def mandelbrot(n, x, y):
	c = complex(x, y)
	z = 0
	for i in range(n):
		if abs(z) > 2:
			return i
		else:
			z = z**2 + c
	return n

def draw_mandelbrot(n, w, h):
	for x in range(w):
		for y in range(h):
			i = mandelbrot(n, (x - w/2)/(w/4), (y - h/2)/(h/4))
			canvas.create_rectangle(x, y, x+1, y+1, fill='#%02x%02x%02x' % (i%4*64, i%8*32, i%16*16))

draw_mandelbrot(256, 400, 400)
root.mainloop()