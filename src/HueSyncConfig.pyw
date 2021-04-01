from tkinter import messagebox, END
from threading import Thread
import atexit
import pygubu
import json
import time
import os

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "configui.ui")


cfile = "testconfig.json" if os.path.isfile("testconfig.json") else "config.json"

CONFIG = json.loads(open(cfile, "r").read())


def set_tkinter_text(tar, txt, i=0):
    tar.delete(i, END)
    tar.insert(i, txt)


class App:
    def __init__(self):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('root')
        builder.connect_callbacks(self)
        self.load_config()

    def load_config(self):
        try:
            print("Loading config...")
            set_tkinter_text(self.builder.get_object("addrin"), CONFIG["adress"] or "auto")
            set_tkinter_text(self.builder.get_object("usr"), CONFIG["user"] or "create")
            self.builder.get_object("lamps").delete("1.0", "99999.0")
            self.builder.get_object("lamps").insert("1.0", ';'.join(CONFIG["lamps"]))
            self.builder.get_object("groups").delete("1.0", "99999.0")
            self.builder.get_object("groups").insert("1.0", ';'.join(CONFIG["groups"]))
            self.builder.get_object("maxbri").set(CONFIG["maxbri"] or 90)
            set_tkinter_text(self.builder.get_object("transtime"), CONFIG["transitiontime"] or 10)
            set_tkinter_text(self.builder.get_object("upms"), CONFIG["updatespermillisecond"] or 1000)
            print("Finished loading config!")
        except:
            messagebox.showwarning("Failed to load config", "Failed to load configuration! All old values will be overwritten with the defaults once saved.")

    def save(self):
        try:
            print("Saving config...")
            set_tkinter_text(self.builder.get_object("addrin"), CONFIG["adress"] or "auto")
            CONFIG["adress"] = self.builder.get_object("addrin").get()
            CONFIG["user"] = self.builder.get_object("usr").get()
            CONFIG["maxbri"] = self.builder.get_object("maxbri").get()
            CONFIG["transitiontime"] = int(self.builder.get_object("transtime").get())
            CONFIG["updatespermillisecond"] = int(self.builder.get_object("upms").get())
            CONFIG["lamps"] = [x.strip() for x in str(self.builder.get_object("lamps").get("1.0", END)).split(";") if len(x) > 0]
            CONFIG["groups"] = [x.strip() for x in str(self.builder.get_object("groups").get("1.0", END)).split(";") if len(x) > 0]

            open(cfile, "w").write(json.dumps(CONFIG, indent=4, sort_keys=True))
            print("Finished saving config!")
        except:
            messagebox.showerror("Error", "Something unexpected went wrong whilst saving, please try again!")

    def run(self):
        self.mainwindow.mainloop()


def start_exiter():
    time.sleep(5)
    os._exit(0)


def on_exit():
    Thread(target=start_exiter).start()
    root.destroy()


def on_window_close():
    Thread(target=start_exiter).start()
    root.destroy()
    os._exit(0)


if __name__ == '__main__':
    import tkinter as tk

    root = tk.Tk()

    # Window
    root.minsize(200, 480)
    root.iconbitmap(r"icon.ico")
    root.title("Hue Sync Config")

    # Exit on tkinter exit
    root.protocol("WM_DELETE_WINDOW", on_window_close)
    atexit.register(on_exit)

    app = App()
    app.run()

