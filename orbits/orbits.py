import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
from datetime import datetime, timedelta
import re
from math import sin, cos, pi

import horizon

MOON = '301'
EARTH = '399'
CH3 = '-158'
CAPSTONE = '-1176'
ART1 = '-1023'
LRO = '-85'
MOON_CENTER = '500@301'
MOON_EARTH_CENTER = '500@3'
SOLAR_CENTER = '500@0'
JWST = '-170'

frames = 1600
interval = 30
history = None
history = timedelta(hours=12)

res = 11
sphereRange = [n * 2.0 * pi / res for n in range(0,res)]
sphere = [[sin(p) * cos(t), sin(p) * sin(t), cos(p)] 
          for t in sphereRange
          for p in sphereRange]
sphere = sphere + [[sin(t) * cos(p), sin(t) * sin(p), cos(t)] 
          for t in sphereRange
          for p in sphereRange]
sphereArrays = [
    [a[0] for a in sphere],
    [a[1] for a in sphere],
    [a[2] for a in sphere]
]

def generatePlot():

    # moon missions

    center = MOON_EARTH_CENTER
    # center = MOON_CENTER
    frames = 1600
    interval = 15
    history = None
    # history = timedelta(hours=48)

    # artemis 1

    objects = [EARTH,MOON,ART1]
    start=datetime(2022,11,12,0,0,0,0)
    stop=datetime(2022,12,15,0,0,0,0)

    # chandrayaan 3

    # objects = [EARTH, MOON, CH3]
    # start=datetime(2023,7,12,0,0,0,0)
    # stop=datetime(2023,8,20,0,0,0,0)

    # luna 25

    # objects = [MOON,'2023-118A']
    # start=datetime(2023,8,16,0,0,0,0)
    # stop=datetime(2023,8,17,0,0,0,0)

    # jwst

    # objects = [EARTH, MOON, JWST]
    # start = datetime(2021,12,24)
    # stop = datetime(2024,1,1)

    # iss
    
    # objects = ['399','-125544']
    # start=datetime(2023,1,1,0,0,0,0)
    # stop=datetime(2023,1,2,0,0,0,0)
    # center = '500@399'
    # frames = 1600
    # interval = 30
    # history = timedelta(minutes=90)

    # galilean moons

    # objects = ['599'] + [f'5{num+1:02d}' for num in range(4)]
    # start=datetime(2023,1,1,0,0,0,0)
    # stop=datetime(2023,6,1,0,0,0,0)
    # center = '500@5'
    # frames = 1600
    # interval = 30
    # history = timedelta(hours=12)

    # inner solar system

    # objects = ['10','199','299','399','499']
    # start=datetime(2023,1,1,0,0,0,0)
    # stop=datetime(2026,1,1,0,0,0,0)
    # center=SOLAR_CENTER
    # frames = 1600
    # interval = 30
    # history = timedelta(weeks=8)

    # mars express

    # objects = ['10','199','299','499','399','-41']
    # start=datetime(2003,5,1,0,0,0,0)
    # stop=datetime(2004,1,1,0,0,0,0)
    # center=SOLAR_CENTER
    # frames = 800
    # interval = 10
    # history = timedelta(weeks=16)

    # DART

    # objects = ['920065803','120065803','-135']    
    # start=datetime(2022,9,26,23,13,50,0)
    # stop=datetime(2022,9,26,23,16,0,0)
    # center='500@20065803'
    # frames = 100
    # interval = 20
    # history = timedelta(weeks=16)

    bodyData = horizon.getBodyInfo()

    plt.style.use('dark_background')

    fig = plt.figure(facecolor=None)
    ax = fig.add_subplot(projection='3d')
    ax.axis('off')

    dateData = {}

    lines = []
    dots = {}
    radii = {}

    delta = (stop - start)/frames
    slices = [start + (i * delta) for i in range(frames+1)]
    earlyPattern = re.compile("No ephemeris for target .+ prior to (.+) TDB")
    latePattern = re.compile("No ephemeris for target .+ after (.+) TDB")

    print("Getting data...")
    def retrieve(o: str, start: datetime, stop: datetime, frames: int) -> str:
        s = horizon.getData(
            center,
            o,
            start,
            stop,
            frames)
        tooEarly = earlyPattern.findall(s)
        if tooEarly:
            start = datetime.strptime(tooEarly[0], 'A.D. %Y-%b-%d %H:%M:%S.%f')
            for s in slices:
                if s >= start:
                    start = s
                    break
            frames = slices.index(stop) - slices.index(start)
            s = horizon.getData(
                center,
                o,
                start,
                stop,
                frames)
        tooLate = latePattern.findall(s)
        if tooLate:
            stop = datetime.strptime(tooLate[0], 'A.D. %Y-%b-%d %H:%M:%S.%f')
            for s in reversed(slices):
                if s <= stop:
                    stop = s
                    break
            frames = slices.index(stop) - slices.index(start)
            s = horizon.getData(
                center,
                o,
                start,
                stop,
                frames)
        return s

    objectData = {o: retrieve(o, start, stop, frames) for o in objects}

    for o in objectData:
        #print(objectData[o])
        if 'No matches found.' in objectData[o]:
            print(f"No matches found for object {o}")
            return
        
    

    print("Data retrieved.")
    print("Plotting data...")
    for o in objects:
        fstring = objectData[o].split('\n')
        name = ''
        read = False
        dateData[o] = {}

        for line in fstring:
            if read:
                if '$$EOE' in line:
                    break
                l = line.split(',')
                dateData[o][datetime.strptime(l[1].strip(), 'A.D. %Y-%b-%d %H:%M:%S.%f')] = [float(l[2]), float(l[3]), float(l[4])]
            else:
                if 'Target body name' in line:
                    name = line.split(':')[1].split('(')[0].strip()
                    d = list(filter(lambda x: x['englishName'] in name, bodyData))
                    if d:
                        radii[o] = float(d[0]['meanRadius'])
                read = '$$SOE' in line

        firstLine = dateData[o][list(dateData[o].keys())[0]]
        lines.append([o,ax.plot(firstLine[0], firstLine[1], firstLine[2], label=name)[0]])
        dot = ',' if radii.get(o) else '.'
        dots[o] = ax.plot(np.nan, np.nan, np.nan, dot, linestyle='solid', color=lines[-1][1].get_color())[0]

    ax.set(autoscale_on=True, aspect='equal')
    ax.legend()

    frameData = {
        o : [dateData[o].get(date) for date in slices]           
        for o in dateData    
    }
    
    def update(frame):
        if history:
            start = max(int(frame - (history / delta)),0)
        else:
            start = 0

        for line in lines:
            line[1].set_data_3d(
                [d[0] for d in frameData[line[0]][start:frame] if d],
                [d[1] for d in frameData[line[0]][start:frame] if d],
                [d[2] for d in frameData[line[0]][start:frame] if d])
            last = frameData[line[0]][frame]
            if last:
                d = radii.get(line[0])
                if d:
                    dots[line[0]].set_data_3d(
                        [ (x * d) + last[0] for x in sphereArrays[0]],
                        [ (x * d) + last[1] for x in sphereArrays[1]],
                        [ (x * d) + last[2] for x in sphereArrays[2]])
                else:
                    dots[line[0]].set_data_3d([last[0]],[last[1]],[last[2]])
            else:
                dots[line[0]].set_data_3d([np.nan],[np.nan],[np.nan])

            ax.set_title(slices[frame].strftime("%Y-%b-%d"))
        return lines + [val for val in dots.values()]


    ani = animation.FuncAnimation(fig=fig, func=update, frames=len(slices), interval=interval)
    plt.show()
    

if __name__ == "__main__":
    generatePlot()