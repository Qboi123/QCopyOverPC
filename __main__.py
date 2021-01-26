import tkinter as tk
import lib.gui
import globals as g


class Main(tk.Tk):
    def __init__(self):
        super().__init__()

        g.root_window = self


if __name__ == '__main__':
    Main()
