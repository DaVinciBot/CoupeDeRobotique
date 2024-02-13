import time

def unknown_action():
    print("received an unknown action")

def plant():
    print("début de la phase plante")
    for i in range(20):
        print(i)
        time.sleep(1)
    
def solar_panel():
    print("début de la phase panneau solaire")
    
def return_home():
    print("return home")