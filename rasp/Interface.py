import pywebio
import Teensy_UART


def app():
    global teensy
    old = None
    pywebio.output.put_button("set_coord",
                                set_coords
                                )
    table = pywebio.output.put_scope("data")
    pywebio.output.put_table(teensy.odometrie,scope="data")
    while (True):
        if old != teensy.odometrie:
            pywebio.output.clear_scope("data")
            pywebio.output.put_table(teensy.odometrie,scope="data")
            old = teensy.odometrie


def set_coords():
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
