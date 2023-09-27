from bot import Logger, API, Utils, GPIO
import time


def main():
    """
    _summary_
    """
    Utils.start_api()
    state = Utils.load_state()
    
    l = Logger()
    pins = {"tirette": {"pin": 37, "mode": "INPUT"}, "led": {"pin": 33, "mode":"OUTPUT"}}
    
    state.set("tirette", "0")
    state.set("led", "0")
    gpios = []
    for pin in pins:
        gpios.append(GPIO.GPIO(pins[pin]["pin"], pins[pin]["mode"]))
        if pins[pin]["mode"] == "OUTPUT": gpios[-1].set(0)
    
    gpios[1].set(1)
    while True:
        for gpio in gpios:
            l.log(f"Pin: {gpio.pin}, Value: {gpio.get()}", 0)
        gpios[1].set(not gpios[1].get())
        state.set("led", str(gpios[1].get()))
        state.set("tirette", str(gpios[0].get()))


        time.sleep(1)


if __name__ == "__main__":
    main()
