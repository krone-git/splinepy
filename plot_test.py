import tkinter as tk
from math import sin

from tensor import Tensor
from vector import Vector
from matrix import Matrix
from plot import TkinterGraphPlotterCanvas, TkinterInterpolationCurve


app = tk.Tk()

canvas = TkinterGraphPlotterCanvas(
    app, resolution=50
)
canvas.pack(expand=tk.YES, fill=tk.BOTH)
canvas.origin.set_origin(
    canvas.winfo_reqwidth() / 2, canvas.winfo_reqheight() / 2,
)
canvas.update()

function = lambda x: (10 * x, 10 * sin(x))
curve = TkinterInterpolationCurve(
    canvas,
    canvas.origin,
    True,
    function,
    1,
    "black",
    "black",
    4
)
curve.update()
canvas._curves.append(curve)

app.mainloop()