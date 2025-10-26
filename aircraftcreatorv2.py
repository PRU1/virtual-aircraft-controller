import aircraftID as air
import time
import random
import threading
import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

# --- Set up aircraft and containers ---
a0 = air.gen_aircraft_instance("DEP")
a1 = air.gen_aircraft_instance("ARR")
a2 = air.gen_aircraft_instance("ARR")

planes = [a0, a1, a2]
planes_dict = {}
planes_lock = threading.Lock()
for i in planes:
    planes_dict[i.fltno] = i

# --- Background plane generator ---
def gen_aircraft():
    while True:
        time.sleep(15)
        if random.random() < 0.5:
            new_plane = air.gen_aircraft_instance(random.choice(["ARR", "DEP"]))
            with planes_lock:
                planes.append(new_plane)
                planes_dict[new_plane.fltno] = new_plane
            threading.Thread(target=new_plane.run, daemon=True).start()

# --- Cleanup thread ---
def cleanup_loop():
    while True:
        with planes_lock:
            planes[:] = [
                p for p in planes
                if not (
                    (p.status == "ARR" and p.on_ground) or
                    (p.status == "DEP" and p.altitude >= 4000)
                )
            ]
            for flt in list(planes_dict.keys()):
                p = planes_dict[flt]
                if (p.status == "ARR" and p.on_ground) or (p.status == "DEP" and p.altitude >= 4000):
                    del planes_dict[flt]
        time.sleep(10)

# --- Aircraft run threads ---
for i in planes:
    threading.Thread(target=i.run, daemon=True).start()

# --- Tkinter GUI + matplotlib plot ---
def tk_gui():
    root = tk.Tk()
    root.title("ATC Simulation & Command Console")

    frm = ttk.Frame(root, padding=10)
    frm.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    label = ttk.Label(frm, text="Enter command (callsign cmd value ...):")
    label.pack()
    entry = ttk.Entry(frm, width=40)
    entry.pack()
    entry.focus()
    log = tk.Text(frm, height=13, width=50)
    log.pack()

    fig, ax1 = plt.subplots(figsize=(5,5), facecolor="#555555")
    ax1.set_facecolor("#000000")
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Track last save time
    last_save_time = time.time()

    def animate_plot():
        nonlocal last_save_time
        with planes_lock:
            x = []
            y = []
            airborne = []
            for i in planes:
                if i.altitude != 0:
                    x.append(i.posx)
                    y.append(i.posy)
                    airborne.append(i)
            ax1.clear()
            ax1.scatter(x, y, color="#00FF00")
            ax1.plot([0,20], [0,13], color="#FFFFFF")
            ax1.plot([0,20], [0,8.48], color="#FFFFFF")
            ax1.plot([0,20], [0,18.65], color="#FFFFFF")
            ax1.set_xlim(-20, 20)
            ax1.set_ylim(-20, 20)
            for i in airborne:
                ax1.annotate(
                    f"{i.fltno}\n{i.type}\n{int(i.altitude)} {int(i.speed)} {i.heading % 360}\n{round(i.posx, 2)} {round(i.posy, 2)}",
                    (i.posx, i.posy), (i.posx + 0.2, i.posy - 0.2), color="#00FF00"
                )
        canvas.draw()

        # Save plot every 2 seconds
        current_time = time.time()
        if current_time - last_save_time >= 2:
            plot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_plot.png")
            fig.savefig(plot_path, dpi=100, bbox_inches='tight')
            last_save_time = current_time

        root.after(1000, animate_plot)  # Update GUI every 1 second

    def on_submit():
        instruction = entry.get()
        entry.delete(0, tk.END)
        cmd = instruction.strip().split()
        if len(cmd) >= 3 and len(cmd) % 2 == 1:
            callsign = cmd[0]
            with planes_lock:
                dest = planes_dict.get(callsign)
            if dest:
                errors = False
                for n in range(int((len(cmd) - 1)/2)):
                    command = cmd[n*2 + 1]
                    value = cmd[n*2 + 2]
                    if command in ["alt", "speed", "heading", "clearL", "clearTO"]:
                        try:
                            dest.command(command, int(value))
                        except Exception:
                            log.insert(tk.END, f"Invalid value for {command}\n")
                            errors = True
                    else:
                        log.insert(tk.END, f"Invalid command: {command}\n")
                        errors = True
                if not errors:
                    log.insert(tk.END, f"Tower: {instruction}\n")
            else:
                log.insert(tk.END, "Callsign not found!\n")
        else:
            log.insert(tk.END, "Invalid command format.\n")
        log.see(tk.END)

    entry.bind("<Return>", lambda evt: on_submit())
    submit_button = ttk.Button(frm, text="Send", command=on_submit)
    submit_button.pack()

    # Start matplotlib animation and Tkinter mainloop
    animate_plot()
    root.mainloop()

# --- Start background threads ---
threading.Thread(target=gen_aircraft, daemon=True).start()
threading.Thread(target=cleanup_loop, daemon=True).start()

# --- Start GUI in main thread ---
tk_gui()