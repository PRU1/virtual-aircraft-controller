import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure(facecolor="#555555")
ax1 = fig.add_subplot(1, 1, 1)
ax1.set_facecolor("#000000")

def animate (frame, planes):
    x = []
    y = []
    airborne = []
    xcen = [0, 20]
    yrwy = [0, 13]
    yils1 = [0, 8.48]
    yils2 = [0, 18.65]
    for i in planes:
        if i.altitude != 0:
            x.append(i.posx)
            y.append(i.posy)
            airborne.append(i)

    ax1.clear()
    ax1.scatter(x, y, color = "#00FF00")
    ax1.plot(xcen, yrwy, color = "#FFFFFF", linestyle = "-")
    ax1.plot(xcen, yils1, color = "#FFFFFF", linestyle = "-")
    ax1.plot(xcen, yils2, color = "#FFFFFF", linestyle = "-")
    ax1.set_xlim(-20, 20)
    ax1.set_ylim(-20, 20)

    for i in airborne:
        ax1.annotate(f"{i.fltno}\n{i.type}\n{int(i.altitude)} {int(i.speed)} {i.heading % 360}\n{round(i.posx, 2)} {round(i.posy, 2)}", (i.posx, i.posy), (i.posx + 0.2, i.posy - 0.2), color = "#00FF00")

def start_animation(planes):
    anim = animation.FuncAnimation(fig, animate, 1000, fargs = (planes,))
    plt.show()