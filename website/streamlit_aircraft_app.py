import streamlit as st
import matplotlib.pyplot as plt
import time
import random
import aircraftID as air

planes = [air.gen_aircraft_instance("DEP"), air.gen_aircraft_instance("ARR"), air.gen_aircraft_instance("ARR")]

def advance_simulation():
    # Update aircraft state here (move, change altitude, etc.)
    for plane in planes:
        if plane.altitude > 0:
            plane.posx += random.uniform(-0.5, 0.5)
            plane.posy += random.uniform(-0.5, 0.5)
            # Your real simulation logic would go here

st.title("Evolving Aircraft Plot")

run_sim = st.checkbox("Run Simulation", value=True)

placeholder = st.empty()

while run_sim:
    advance_simulation()

    fig, ax = plt.subplots(figsize=(6,6), facecolor="#555555")
    ax.set_facecolor("#000000")
    x = [p.posx for p in planes if p.altitude > 0]
    y = [p.posy for p in planes if p.altitude > 0]
    ax.scatter(x, y, color="#00FF00")
    ax.plot([0,20], [0,13], color="#FFFFFF")
    ax.plot([0,20], [0,8.48], color="#FFFFFF")
    ax.plot([0,20], [0,18.65], color="#FFFFFF")
    ax.set_xlim(-20, 20)
    ax.set_ylim(-20, 20)
    placeholder.pyplot(fig)
    time.sleep(1)
