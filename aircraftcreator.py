import atcplot as atc
import aircraftID as air
import time
import threading

a0 = air.gen_aircraft_instance("DEP")
threading.Thread(target=a0.run).start()

a1 = air.gen_aircraft_instance("ARR")
threading.Thread(target=a1.run).start()

a2 = air.gen_aircraft_instance("ARR")
threading.Thread(target=a2.run).start()

planes = [a0, a1, a2]

planes_dict = {}
for i in planes:
    planes_dict[i.fltno] = i

# --- function to send commands after animation starts ---
def send_commands():
    while True:
        instruction = input("Tower: ")
        callsign, cmd, value = instruction.split()
        dest = planes_dict.get(callsign)
        dest.command(cmd, int(value))
        time.sleep(1)

# run that in the background so plt.show() doesn't block it
threading.Thread(target=send_commands, daemon=True).start()

# --- start animation (main thread stays inside plt.show()) ---
atc.start_animation(planes)