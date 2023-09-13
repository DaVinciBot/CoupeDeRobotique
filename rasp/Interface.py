from Libraries.Teensy_Com import Rolling_basis
import pywebio
import time
import threading


def app():
    global teensy
    old = None
    th = threading.Thread(target=pin)
    pywebio.session.register_thread(th)
    th.start()
    pywebio.output.put_scope("buttons")
    pywebio.output.put_buttons(
        ["Home", "dummy"],
        onclick=buttons,
        scope="buttons"
    )
    pywebio.output.put_scope("data")
    pywebio.output.put_table([teensy.odometrie], scope="data")
    while (True):
        time.sleep(0.5)
        if old != teensy.odometrie:
            pywebio.output.clear_scope("data")
            pywebio.output.put_table([teensy.odometrie], scope="data")
            old = teensy.odometrie


def pin():
    while True:
        coords = pywebio.input.input_group("Coordinates",
                                           [
                                               pywebio.input.input(
                                                   "x", name="x", type=pywebio.input.FLOAT),
                                               pywebio.input.input(
                                                   "y", name="y", type=pywebio.input.FLOAT),
                                           ],
                                           )
        teensy.Go_To([float(coords["x"]), float(coords["y"]),0])


def buttons(button):
    if button == "Home":
            teensy.Home_Position()


class dummy:
    odometrie = [[0, 0, 0]]

    def Go_To(self, x, y):
        print("going to ", x, " ", y)

    def Home_Position(self):
        print("homing")


if __name__ == "__main__":
    global teensy
    teensy = Rolling_basis(crc = False)
    # teensy = dummy()
    pywebio.start_server(app, port=42069)
