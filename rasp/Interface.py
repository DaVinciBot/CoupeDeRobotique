import pywebio
import Teensy_UART


def app():
    global teensy
    while (True):
        coords = pywebio.input.input_group("Coordinates",
                                           [
                                               pywebio.input.input(
                                                   "x", name="x", type=pywebio.input.FLOAT),
                                               pywebio.input.input(
                                                   "y", name="y", type=pywebio.input.FLOAT),
                                           ],
                                           )
        teensy.Go_To(coords["x"], coords["y"])


if __name__ == "__main__":
    global teensy
    teensy = Teensy_UART.Teensy()
    pywebio.start_server(app, port=42069)
