import tkinter as tk
import subprocess
import sys

def launch_correction():
    presentation_id = id_entry.get()
    mode = var.get()
    subprocess.Popen([sys.executable, "main.py", presentation_id, "--mode", mode])
    root.destroy()

root = tk.Tk()
root.title("SlidesCleaner GUI")

tk.Label(root, text="Entrez l'ID de la présentation :").pack()
id_entry = tk.Entry(root)
id_entry.pack()

var = tk.StringVar(value="manual")
tk.Radiobutton(root, text="Mode Manuel", variable=var, value="manual").pack()
tk.Radiobutton(root, text="Mode Auto", variable=var, value="auto").pack()

tk.Button(root, text="Lancer la correction", command=launch_correction).pack()

root.mainloop()
