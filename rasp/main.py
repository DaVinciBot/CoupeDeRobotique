from bot import Logger, Utils, GPIO, Rolling_basis
import time



def main():
    Utils.start_api()
    state = Utils.load_state()
    
    com = Rolling_basis()
    com.Go_To([10, 100, 0])
    
    l = Logger() # le pin 33 ne fonctionne pas
    pins = {"tirette": {"pin": 37, "mode": "INPUT"}, "led": {"pin": 8, "mode":"OUTPUT"}}
    
    state.set("tirette", "0")
    state.set("led", "0")
    gpios: list[GPIO.PIN] = []
    for pin in pins:
        gpios.append(GPIO.PIN(pins[pin]["pin"], pins[pin]["mode"]))
        if pins[pin]["mode"] == "OUTPUT": gpios[-1].set(False)
        
    gpios[1].set(False)
    while True:
        
        for gpio in gpios:
            l.log(f"Pin: {gpio.pin}, Value: {gpio.get()}", 0)
            
        state.set("led", str(gpios[1].get()))
        state.set("tirette", str(gpios[0].get()))


        time.sleep(1)


if __name__ == "__main__":
    main()
