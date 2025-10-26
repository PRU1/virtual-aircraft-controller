import atcplot as atc
import aircraftID as air
import audioparser
import time
import random
import threading
import tkinter as tk
from tkinter import ttk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

# --- Initialize aircraft and containers ---
a0 = air.gen_aircraft_instance("DEP")
a1 = air.gen_aircraft_instance("ARR")
a2 = air.gen_aircraft_instance("ARR")

planes = [a0, a1, a2]
planes_dict = {}
planes_lock = threading.Lock()

for i in planes:
    planes_dict[i.fltno] = i


def send_commands(instruction):
    while True:
        cmd = instruction
        if len(cmd) >= 3 and len(cmd) % 2 == 1:
            callsign = cmd[0]
            if callsign in planes_dict:
                dest = planes_dict.get(callsign)
                for n in range(int((len(cmd) - 1)/2)):
                    command = cmd[n * 2 + 1]
                    value = cmd[n * 2 + 2]
                    try:
                        value = int(value)
                    except:
                        print("Invalid value")
                        continue
                    if command in ["alt", "speed", "heading", "clearL", "clearTO"]:
                        dest.command(command, int(value))
                    else:
                        print("Invalid command")

            else:
                print("Callsign not found")
        else:
            print("Invalid command format")
        time.sleep(1)


def process_command_string(instruction: str) -> tuple[bool, str]:
    """Parse a manual-style instruction string and apply commands.

    Example: "ABC123 alt 5000 speed 220"
    Returns (True, '') on success or (False, message) on error.
    """
    cmd = instruction.strip().split()
    if len(cmd) < 3 or len(cmd) % 2 == 0:
        return False, "Invalid command format"

    callsign = cmd[0]
    with planes_lock:
        dest = planes_dict.get(callsign)
    if not dest:
        return False, f"Callsign '{callsign}' not found"

    for n in range(int((len(cmd) - 1) / 2)):
        command = cmd[n * 2 + 1]
        value = cmd[n * 2 + 2]
        if command not in ["alt", "speed", "heading", "clearL", "clearTO"]:
            return False, f"Invalid command: {command}"
        try:
            dest.command(command, int(value))
        except Exception as exc:
            return False, f"Invalid value for {command}: {exc}"

    return True, ""

# Threads are started by start_background(); do not start them at import time.

# --- Background generator ---
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

# --- Audio command handler ---
def audio_command_loop(log_widget=None):
    while True:
        try:
            cmd = audioparser.parse_audio("./pilotCommand.wav")
            if len(cmd) >= 3 and len(cmd) % 2 == 1:
                callsign = cmd[0]
                with planes_lock:
                    dest = planes_dict.get(callsign)
                if dest:
                    for n in range(int((len(cmd) - 1)/2)):
                        command = cmd[n * 2 + 1]
                        value = cmd[n * 2 + 2]
                        try:
                            value = int(value)
                        except:
                            if log_widget:
                                log_widget.insert(tk.END, f"Invalid value for {command}\n")
                            continue
                        if command in ["alt", "speed", "heading", "clearL", "clearTO"]:
                            dest.command(command, value)
                            if log_widget:
                                log_widget.insert(tk.END, f"VoiceCmd → {callsign} {command} {value}\n")
                        else:
                            if log_widget:
                                log_widget.insert(tk.END, f"Invalid command: {command}\n")
                else:
                    if log_widget:
                        log_widget.insert(tk.END, f"Callsign '{callsign}' not found.\n")
            else:
                if log_widget:
                    log_widget.insert(tk.END, "Invalid voice command format.\n")
        except Exception as e:
            if log_widget:
                log_widget.insert(tk.END, f"Audio parse error: {e}\n")
        if log_widget:
            log_widget.see(tk.END)
        time.sleep(3)

# --- Tkinter GUI + Matplotlib Plot ---
def tk_gui():
    root = tk.Tk()
    root.title("ATC Simulation with Voice Commands")

    frm = ttk.Frame(root, padding=10)
    frm.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    label = ttk.Label(frm, text="Manual Command (callsign cmd value ...):")
    label.pack()

    entry = ttk.Entry(frm, width=40)
    entry.pack()
    entry.focus()

    log = tk.Text(frm, height=15, width=50)
    log.pack()

    fig, ax1 = plt.subplots(figsize=(5,5), facecolor="#555555")
    ax1.set_facecolor("#000000")
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    last_save_time = time.time()

    def animate_plot():
        nonlocal last_save_time
        with planes_lock:
            x, y, airborne = [], [], []
            for p in planes:
                if p.altitude != 0:
                    x.append(p.posx)
                    y.append(p.posy)
                    airborne.append(p)
            ax1.clear()
            ax1.scatter(x, y, color="#00FF00")
            ax1.plot([0,20],[0,13], color="#FFFFFF")
            ax1.plot([0,20],[0,8.48], color="#FFFFFF")
            ax1.plot([0,20],[0,18.65], color="#FFFFFF")
            ax1.set_xlim(-20, 20)
            ax1.set_ylim(-20, 20)
            for p in airborne:
                ax1.annotate(
                    f"{p.fltno}\n{p.type}\n{int(p.altitude)} {int(p.speed)} {p.heading % 360}",
                    (p.posx, p.posy), (p.posx + 0.2, p.posy - 0.2), color="#00FF00"
                )
        canvas.draw()

        # Save snapshot periodically
        now = time.time()
        if now - last_save_time >= 2:
            plot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_plot.png")
            fig.savefig(plot_path, dpi=100, bbox_inches="tight")
            last_save_time = now

        root.after(1000, animate_plot)

    def on_submit():
        instruction = entry.get().strip()
        entry.delete(0, tk.END)
        cmd = instruction.split()
        if len(cmd) >= 3 and len(cmd) % 2 == 1:
            callsign = cmd[0]
            with planes_lock:
                dest = planes_dict.get(callsign)
            if dest:
                for n in range(int((len(cmd) - 1)/2)):
                    command = cmd[n*2 + 1]
                    value = cmd[n*2 + 2]
                    if command in ["alt", "speed", "heading", "clearL", "clearTO"]:
                        try:
                            dest.command(command, int(value))
                            log.insert(tk.END, f"Tower: {instruction}\n")
                        except:
                            log.insert(tk.END, f"Invalid value for {command}\n")
                    else:
                        log.insert(tk.END, f"Invalid command: {command}\n")
            else:
                log.insert(tk.END, "Callsign not found!\n")
        else:
            log.insert(tk.END, "Invalid command format.\n")
        log.see(tk.END)

    entry.bind("<Return>", lambda evt: on_submit())
    ttk.Button(frm, text="Send", command=on_submit).pack()

    # Start animation + background voice command loop
    threading.Thread(target=audio_command_loop, args=(log,), daemon=True).start()
    animate_plot()
    root.mainloop()

# --- Background thread bootstrap ---
_threads_started = False

def start_background(start_gui: bool = False):
    """Start background aircraft threads (headless by default)."""
    global _threads_started
    if not _threads_started:
        for plane in planes:
            threading.Thread(target=plane.run, daemon=True).start()
        threading.Thread(target=gen_aircraft, daemon=True).start()
        threading.Thread(target=cleanup_loop, daemon=True).start()
        _threads_started = True

    if start_gui:
        tk_gui()


if __name__ == "__main__":
    start_background(start_gui=True)
