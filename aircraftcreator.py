import atcplot as atc
import aircraftID as air
import time
import random
import threading

a0 = air.gen_aircraft_instance("DEP")
threading.Thread(target=a0.run).start()

a1 = air.gen_aircraft_instance("ARR")
threading.Thread(target=a1.run).start()

a2 = air.gen_aircraft_instance("ARR")
threading.Thread(target=a2.run).start()

planes = [a0, a1, a2]

planes_dict = {}
planes_lock = threading.Lock()
for i in planes:
    planes_dict[i.fltno] = i

# --- function to send commands after animation starts ---
def gen_aircraft():
    while True:
        time.sleep(15)
        if random.random() < 0.5:
            new_plane = air.gen_aircraft_instance(random.choice(["ARR", "DEP"]))
            planes.append(new_plane)
            planes_dict[new_plane.fltno] = new_plane
            threading.Thread(target=new_plane.run).start()
            

def send_commands():
    while True:
        instruction = input("Tower: ")
        callsign, cmd, value = instruction.split()
        dest = planes_dict.get(callsign)
        dest.command(cmd, int(value))
        time.sleep(1)

def cleanup_loop():
    while True:
        with planes_lock:
            before = len(planes)
            # Keep only planes that are still active
            planes[:] = [
                p for p in planes
                if not (
                    (p.status == "ARR" and p.on_ground) or
                    (p.status == "DEP" and p.altitude >= 4000)
                )
            ]

            # Sync dictionary
            for flt in list(planes_dict.keys()):
                p = planes_dict[flt]
                if (p.status == "ARR" and p.on_ground) or (p.status == "DEP" and p.altitude >= 4000):
                    del planes_dict[flt]

            after = len(planes)
        if before != after:
            print(f"Cleaned up {before - after} inactive aircraft")
        time.sleep(10)


# run that in the background so plt.show() doesn't block it
threading.Thread(target=gen_aircraft, daemon=True).start()
threading.Thread(target=send_commands, daemon=True).start()
threading.Thread(target=cleanup_loop, daemon=True).start()

# --- start animation (main thread stays inside plt.show()) ---
atc.start_animation(planes)