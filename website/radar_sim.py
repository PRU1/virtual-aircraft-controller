import os
import time
import threading
import random
from typing import List, Dict, Tuple

import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt

# Import aircraft model from the website package
import aircraftID as air

# Shared state
_planes_lock = threading.Lock()
_planes: List[air.aircraft] = []
_planes_dict: Dict[str, air.aircraft] = {}
_log: List[str] = []
_threads_started = False
_stop_flag = False


def _init_planes():
    global _planes, _planes_dict
    # Seed with a couple of arrivals and a departure
    a0 = air.gen_aircraft_instance("DEP")
    a1 = air.gen_aircraft_instance("ARR")
    a2 = air.gen_aircraft_instance("ARR")
    _planes = [a0, a1, a2]
    _planes_dict = {p.fltno: p for p in _planes}


def _start_plane_threads():
    # Each aircraft has a long-running run() loop
    for p in list(_planes):
        t = threading.Thread(target=p.run, daemon=True)
        t.start()


def _generator_loop():
    """Occasionally add new aircraft (ARR/DEP)."""
    while not _stop_flag:
        time.sleep(15)
        try:
            if random.random() < 0.5:
                p = air.gen_aircraft_instance(random.choice(["ARR", "DEP"]))
                with _planes_lock:
                    _planes.append(p)
                    _planes_dict[p.fltno] = p
                threading.Thread(target=p.run, daemon=True).start()
        except Exception:
            # Keep background loop resilient
            pass


def _cleanup_loop():
    """Remove aircraft that have finished (landed or departed)."""
    while not _stop_flag:
        time.sleep(10)
        try:
            with _planes_lock:
                to_remove: List[str] = []
                for p in _planes:
                    if (p.status == "ARR" and p.on_ground) or (p.status == "DEP" and p.altitude >= 4000):
                        to_remove.append(p.fltno)
                if to_remove:
                    _planes[:] = [p for p in _planes if p.fltno not in to_remove]
                    for flt in to_remove:
                        _planes_dict.pop(flt, None)
        except Exception:
            pass


def _render_plot(out_path: str) -> None:
    """Render one frame of the radar plot to the given path."""
    # Snapshot positions
    with _planes_lock:
        airborne = [p for p in _planes if getattr(p, "altitude", 0) != 0]
        xs = [p.posx for p in airborne]
        ys = [p.posy for p in airborne]

    fig, ax1 = plt.subplots(figsize=(5, 5), facecolor="#555555")
    try:
        ax1.set_facecolor("#000000")
        ax1.scatter(xs, ys, color="#00FF00")
        ax1.plot([0, 20], [0, 13], color="#FFFFFF")
        ax1.plot([0, 20], [0, 8.48], color="#FFFFFF")
        ax1.plot([0, 20], [0, 18.65], color="#FFFFFF")
        ax1.set_xlim(-20, 20)
        ax1.set_ylim(-20, 20)

        for p in airborne:
            ax1.annotate(
                f"{p.fltno}\n{p.type}\n{int(p.altitude)} {int(p.speed)} {int(p.heading) % 360}\n{p.posx:.2f} {p.posy:.2f}",
                (p.posx, p.posy), (p.posx + 0.2, p.posy - 0.2), color="#00FF00",
            )

        fig.savefig(out_path, dpi=100, bbox_inches="tight", facecolor="#555555")
        # Force file system to update timestamp
        os.utime(out_path, None)
    finally:
        plt.close(fig)


def _plot_loop():
    """Render current aircraft positions to current_plot.png every second."""
    out_path = os.path.join(os.path.dirname(__file__), "current_plot.png")
    print(f"[radar_sim] Plot loop started, writing to: {out_path}")
    while not _stop_flag:
        try:
            _render_plot(out_path)
            print(f"[radar_sim] Updated plot with {len(_planes)} aircraft")
        except Exception as e:
            print(f"[radar_sim] Plot error: {e}")
            # Never crash the loop; just try again next tick
            pass
        time.sleep(1)


def start_background():
    """Idempotently start all background threads for radar simulation/rendering."""
    global _threads_started
    if _threads_started:
        print("[radar_sim] Background already started")
        return
    _threads_started = True

    print("[radar_sim] Starting background simulation...")
    _init_planes()
    _start_plane_threads()
    
    # Write an initial plot immediately so the file exists for clients
    out_path = os.path.join(os.path.dirname(__file__), "current_plot.png")
    try:
        _render_plot(out_path)
        print(f"[radar_sim] Initial plot written to: {out_path}")
    except Exception as e:
        print(f"[radar_sim] Failed to write initial plot: {e}")

    threading.Thread(target=_generator_loop, daemon=True).start()
    threading.Thread(target=_cleanup_loop, daemon=True).start()
    threading.Thread(target=_plot_loop, daemon=True).start()
    print("[radar_sim] All background threads started")


# --- Command handling (headless replacement for Tk console) ---
def submit_instruction(instruction: str) -> Tuple[bool, str]:
    """
    Accepts a command string in the same format as the Tk GUI:
      "<FLTNO> <cmd1> <value1> [<cmd2> <value2> ...]"
    where cmd in {alt, speed, heading, clearL, clearTO} and values are ints.

    Returns (success, message).
    """
    instruction = (instruction or "").strip()
    if not instruction:
        return False, "Empty instruction"

    parts = instruction.split()
    if len(parts) < 3 or len(parts) % 2 == 0:
        return False, "Invalid command format. Expected: <FLTNO> <cmd> <value> [...]"

    fltno = parts[0]
    with _planes_lock:
        dest = _planes_dict.get(fltno)
    if not dest:
        return False, "Callsign not found!"

    errors = []
    allowed = {"alt", "speed", "heading", "clearL", "clearTO"}
    for i in range((len(parts) - 1) // 2):
        cmd = parts[i * 2 + 1]
        val = parts[i * 2 + 2]
        if cmd not in allowed:
            errors.append(f"Invalid command: {cmd}")
            continue
        try:
            ival = int(val)
        except Exception:
            errors.append(f"Invalid value for {cmd}")
            continue
        try:
            dest.command(cmd, ival)
        except Exception:
            errors.append(f"Failed to queue command: {cmd}")

    if errors:
        _log.append("\n".join(errors))
        return False, "\n".join(errors)
    msg = f"Tower: {instruction}"
    _log.append(msg)
    return True, msg


def get_log(tail: int = 50) -> List[str]:
    return _log[-tail:]


def list_flights() -> List[str]:
    with _planes_lock:
        return list(_planes_dict.keys())


def generate_plot_once(out_path: str | None = None) -> str:
    """Public helper to write a single radar frame on demand.

    Returns the path to the written PNG.
    """
    if out_path is None:
        out_path = os.path.join(os.path.dirname(__file__), "current_plot.png")
    _render_plot(out_path)
    return out_path


# Backwards-friendly alias
def generate_plot():
    return generate_plot_once()

def stop_background():
    global _stop_flag
    _stop_flag = True
