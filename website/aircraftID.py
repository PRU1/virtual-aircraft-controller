import random
import time
import math
import queue

class aircraft:

    def __init__(self, type, fltno, callsign, status):

        self.command_queue = queue.Queue()

        self.fltno = fltno
        self.callsign = callsign
        self.status = status
        self.clearL = False
        self.clearTO = False
        self.on_approach = False
        self.vertspeed = 30
        self.type = type

        if status == "ARR": #arrival
            self.speed = 240
            self.altitude = random.randint(4, 8) * 1000
            self.on_ground = False
            
            condition = random.randint(0, 3)
            if condition == 0: #spawn on left edge
                self.posx = -20
                self.posy = random.random() * 20 - 10
                self.heading = random.randint(30, 150)
            elif condition == 1: #spawn on top edge
                self.posx = random.random() * 20 - 10
                self.posy = 20
                self.heading = random.randint(120, 240)
            elif condition == 2: #spawn on right edge
                self.posx = 20
                self.posy = random.random() * 20 - 10
                self.heading = random.randint(210, 330)
            else: #spawn on bottom edge
                self.posx = random.random() * 20 - 10
                self.posy = -20
                self.heading = random.randint(300, 420)
                self.heading = self.heading % 360
            print(f"{self.fltno}: Toronto tower, {self.fltno} with you at {int(self.altitude)}ft")
        elif status == "DEP": #departure
            self.speed = 0
            self.altitude = 0
            self.posx = 0
            self.posy = 0
            self.heading = 237
            self.on_ground = True
            print(f"{self.fltno}: Toronto tower, {self.fltno} holding short Runway 23")

        self.target_alt = self.altitude
        self.target_heading = self.heading
        self.target_speed = self.speed

    def command(self, cmd, value):
        self.command_queue.put((cmd, value))

    def run (self):

        while True:

            try:
                while True:  # empty the queue if multiple commands arrived
                    cmd, val = self.command_queue.get_nowait()
                    if cmd == "alt":
                        self.target_alt = val
                        if self.target_alt > self.altitude:
                            print(f"{self.fltno}: Climb and maintain {val}ft, {self.fltno}")
                        else:
                            print(f"{self.fltno}: Descend and maintain {val}ft, {self.fltno}")
                    elif cmd == "heading":
                        self.target_heading = val
                        print(f"{self.fltno}: Turn heading {val}, {self.fltno}")
                    elif cmd == "speed":
                        self.target_speed = val
                        if self.target_speed > self.speed:
                            print(f"{self.fltno}: Increase speed to {val}kt, {self.fltno}")
                        else:
                            print(f"{self.fltno}: Reduce speed to {val}kt, {self.fltno}")
                    elif cmd == "clearL":
                        self.clearL = val
                        print(f"{self.fltno}: Clear to land Runway 23, {self.fltno}")
                    elif cmd == "clearTO":
                        self.clearTO = val
                        print(f"{self.fltno}: Clear for takeoff Runway 23, {self.fltno}")
            except queue.Empty:
                pass

            '''print(self.fltno)
            print(str(self.altitude) + "ft")
            print(self.posx)
            print(self.posy)
            print(str(self.speed) + "kt")
            print(self.heading)'''

            if not self.on_ground: #in air only
                #altitude control - in air only
                if not (self.target_alt - 30 < self.altitude < self.target_alt + 30):
                    self.altitude += ((self.target_alt - self.altitude)/abs(self.target_alt - self.altitude)) * self.vertspeed
                else:
                    self.altitude = self.target_alt

                #heading control - in air only
                if self.heading < 180:
                    if self.heading < self.target_heading < self.heading + 180:
                        if not (self.target_heading - 3 < self.heading < self.target_heading + 3):
                            self.heading += 3
                        else:
                            self.heading = self.target_heading
                    else:
                        if not (self.target_heading - 3 < self.heading < self.target_heading + 3):
                            self.heading -= 3
                        else:
                            self.heading = self.target_heading
                else:
                    if self.heading - 180 < self.target_heading < self.heading:
                        if not (self.target_heading - 3 < self.heading < self.target_heading + 3):
                            self.heading -= 3
                        else:
                            self.heading = self.target_heading
                    else:
                        if not (self.target_heading - 3 < self.heading < self.target_heading + 3):
                            self.heading += 3
                        else:
                            self.heading = self.target_heading

                #check for approach condition - in air only
                if self.status == "ARR" and 0.424 * self.posx < self.posy < 0.933 * self.posx and self.altitude <= math.sqrt(self.posx ** 2 + self.posy **2) * 1000 and 227 < self.heading < 247:
                    self.on_approach = True
                
                #on approach - in air only
                if self.on_approach and self.clearL and not self.on_ground:
                    self.target_alt = 0
                    self.vertspeed = self.altitude / (math.sqrt(self.posx ** 2 + self.posy **2) / (self.speed * 0.0002778))
                    self.target_heading = math.atan(self.posx/self.posy) + 180
                    self.target_speed = 140
                
                #departure condition - in air only
                if self.status == "DEP" and self.altitude >= 4000:
                    return  #departed and handed off
                
                #check for landing
                if self.status == "ARR" and self.altitude == 0:
                    self.on_ground = True
                    self.target_speed = 0

            else: #on ground only
                if self.status == "DEP":
                    if self.clearTO:
                        self.target_speed = 240
                        if self.speed >= 140:
                            self.target_alt = 3000
                            self.altitude = 30
                            self.on_ground = False #taken off
                else:
                    return #landing completed
            
            #speed control - always
            if not (self.target_speed - 5 < self.speed < self.target_speed + 5):
                self.speed += ((self.target_speed - self.speed)/abs(self.target_speed - self.speed)) * 5
            else:
                self.speed = self.target_speed
        
            #update position - always
            self.posx += (math.sin(self.heading * 0.017453) * self.speed * 0.0002778)
            self.posy += (math.cos(self.heading * 0.017453) * self.speed * 0.0002778)
            
            #ensure heading is mod 360
            self.heading = self.heading % 360

            time.sleep(1)
        
heavy = ["A330", "A350", "A380", "B747", "B767", "B777", "B787", "MD11"]

file = "../airlines.txt"
airline_list = []


x = open(file)
raw = x.read()
rawlist = raw.split("\n")
for entry in rawlist:
    fleet = []
    airline_info = entry.split()
    for n in range(int(len(airline_info[2])/4)):
        fleet.append(airline_info[2][n * 4:(n + 1) * 4])
    airline_info[2] = fleet
    airline_list.append(airline_info)

def gen_aircraft_instance(status):
    seed = random.random()
    if seed < 0.2:
        ID = 0
    elif seed < 0.35:
        ID = 1
    elif seed < 0.5:
        ID = 2
    elif seed < 0.57:
        ID = 3
    else:
        ID = random.randint(4, 55)
    number = random.randint(100, 999)
    fltno = airline_list[ID][0] + str(number)
    callsign = airline_list[ID][1] + " " + str(number)[0] + " " + str(number)[1] + " " + str(number)[2]
    airframe = random.choice(airline_list[ID][2])

    if airframe in heavy:
        callsign += " heavy"

    return aircraft(airframe, fltno, callsign, status)

#threading.Thread(target=a1.run).start()