import pywebio
import Teensy_UART


def app():
    global teensy
    old = None
    pywebio.output.put_button("set_coord",
                                set_coords
                                )
    table = pywebio.output.output()
    table.append(pywebio.output.put_table(teensy.odometrie))
    table.show
    while (True):
        if old != teensy.odometrie:
            table.reset(pywebio.output.put_table(teensy.odometrie))
            # table.append(pywebio.output.put_table(teensy.odometrie))
            table.show
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
