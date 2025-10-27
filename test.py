import tkinter as tk


def on_click():
    print("Cliecked!!!")


if __name__ == "__main__":

    root = tk.Tk()
    root.title("test")

    label = tk.Label(root, text="Hello")
    btn1 = tk.Button(root, text="Click", command=on_click)
    label.pack()
    btn1.pack()

    root.mainloop()
