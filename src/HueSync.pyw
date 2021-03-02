from threading import Thread
import cv2.cv2 as cv2
import numpy as np
import pyautogui
import requests
import tkinter
import pygubu
import atexit
import rgbxy
import json
import time
import os


class LinkButtonNotPressed(Exception):
    pass


def get_bridge_ip(number=0):
    return requests.get("https://discovery.meethue.com/").json()[number]["internalipaddress"]


cfile = "testconfig.json" if os.path.isfile("testconfig.json") else "config.json"

CONFIG = json.loads(open(cfile, "r").read())


if CONFIG["adress"].lower() == "auto":
    adress = get_bridge_ip(CONFIG["bridge_number"])
else:
    adress = CONFIG["adress"]

if CONFIG["user"].lower() == "create":
    r = requests.post(f"http://{adress}/api/", json={"devicetype": "huesync"})
    if 199 < r.status_code < 300:
        j = r.json()[0]
        try:
            if j["error"]["type"] == 101:
                raise LinkButtonNotPressed("Please press the big link button on your bridge 30s before you run this "
                                           + "script!")
        except (KeyError, IndexError):
            try:
                u = j["success"]["username"]
                CONFIG["user"] = u

                open(cfile, "w").write(json.dumps(CONFIG))

                print(f"Successfully created a user! [{u}]")
            except (KeyError, IndexError):
                print("Please try again! [User Creation Exception]")
                exit()

username = CONFIG["user"]
baseURL = f"http://{adress}/api/{username}/"
lURL = f"{baseURL}lights/"

sync_lamps = CONFIG["lamps"]


def add_lamps_in_room(room: str):
    for lamp in requests.get(f"{baseURL}groups/{room}/").json()["lights"]:
        sync_lamps.append(lamp)


for group in CONFIG["groups"]:
    add_lamps_in_room(group)


def set_all_xyb(x, y, bri, transtime=0) -> list[requests.models.Response]:
    res: list[requests.models.Response] = []
    for lamp in sync_lamps:
        res.append(set_xyb(lamp, x, y, bri, transtime=transtime))
    return res


def set_state(lamp: str, state: bool):
    return requests.put(f"{lURL}{lamp}/state", json={"on": state})


def set_all_states(state: bool):
    result: list[requests.models.Response] = []
    for lamp in sync_lamps:
        result.append(set_state(lamp, state))
    return result


def get_state_list():
    res = {}
    for l in sync_lamps:
        state = requests.get(f"{lURL}{l}/").json()["state"]
        res[l] = {
            "on": state["on"],
            "x": state["xy"][0],
            "y": state["xy"][1],
            "bri": state["bri"]
        }
    return res


def apply_state_list(l: dict, transtime=10):
    for k in l.keys():
        set_xyb(k, l[k]["x"], l[k]["y"], l[k]["bri"], transtime=transtime)
        set_state(k, l[k]["on"])


def set_xyb(lamp: str, x, y, bri, transtime=0) -> requests.models.Response:
    return requests.put(f"{lURL}{lamp}/state/", json={"xy": [x, y], "bri": bri, "transitiontime": transtime})


def screenshot():
    return np.array(pyautogui.screenshot())[:, :, ::-1].copy()


def bgr_to_rgb(bgr) -> tuple[int, int, int]:
    return bgr[2], bgr[1], bgr[0]


def get_main_color_on_screen():
    sc = screenshot()
    data = np.reshape(sc, (-1, 3))
    data = np.float32(data)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    compactness, labels, centers = cv2.kmeans(data, 1, None, criteria, 10, flags)

    rgb = bgr_to_rgb(centers[0].astype(np.int32))

    return tuple(rgb)


def get_complementary(color):
    color = color[1:]
    color = int(color, 16)
    comp_color = 0xFFFFFF ^ color
    comp_color = "#%06X" % comp_color
    return comp_color


class UiApp:

    oState = {}
    oBgColor = "SystemButtonFace"

    def __init__(self):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(os.path.dirname(__file__))
        builder.add_from_file(os.path.join(os.path.dirname(__file__), "ui.ui"))
        self.mainwindow = builder.get_object('frame')
        builder.connect_callbacks(self)

    def onStartButtonClick(self):
        global run
        self.oBgColor = self.builder.get_object("colorPreview")["bg"]
        run = True
        self.oState = get_state_list()
        set_all_states(True)
        self.builder.get_object("startButton")["state"] = "disable"
        self.builder.get_object("stopButton")["state"] = "enable"

    def onStopButtonClick(self):
        global run
        run = False
        apply_state_list(self.oState)
        self.builder.get_object("colorPreview")["bg"] = self.oBgColor
        self.builder.get_object("startButton")["state"] = "enable"
        self.builder.get_object("stopButton")["state"] = "disable"

    def update_color(self, rgb):
        global run
        self.builder.get_object("colorPreview")["bg"] = self.oBgColor if not run else '#%02x%02x%02x' % rgb

    def run(self):
        self.mainwindow.mainloop()


def main():
    while True:
        while run:
            try:
                # Get Values
                r, g, b = get_main_color_on_screen()
                x, y = rgbxy.Converter().rgb_to_xy(r, g, b)
                bri = min(CONFIG["maxbri"], int(abs(100 - (r + g + b))))

                set_all_xyb(x, y, bri, transtime=CONFIG["transitiontime"])
                app.update_color(tuple([min(255, v * 3) for v in (r, g, b)]))

                time.sleep(1000 / CONFIG["updatespermillisecond"])
            except Exception as ex:
                print(ex)


def on_exit():
    app.onStopButtonClick()
    root.destroy()


def on_window_close():
    app.onStopButtonClick()
    root.destroy()
    os._exit(0)


if __name__ == "__main__":
    run = False
    Thread(target=main).start()

    root = tkinter.Tk()

    # Window
    # root.geometry(f"1100x110")
    root.resizable(0, 0)
    root.iconbitmap(r"icon.ico")
    root.title("Hue Sync")

    # Exit on tkinter exit
    root.protocol("WM_DELETE_WINDOW", on_window_close)
    atexit.register(on_exit)

    app = UiApp()
    app.run()
