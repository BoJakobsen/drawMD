#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


"""

import numpy as np
#import matplotlib.pyplot as plt
from itertools import chain
import time
import numba 

RED = (255, 0, 0) 
BGCOLOR = "purple"
ATOM_SIZE=10 # pixel diameter for one atom
MAX_SPEED=10 # 
SCREEN_HEIGHT=400
SCREEN_WIDTH=400
WALL_THICKNESS=10

rng = np.random.default_rng()


#@numba.njit(nopython=True)        
def update_forces_JL(atom_x,atom_y,atom_eps,atom_radius):
        fx = np.zeros_like(atom_x)
        fy = np.zeros_like(atom_y)

        # # # Lennard-Jones pair forces between particles 
        # # for now all atoms are the same
        sig = atom_radius + atom_radius
        sig2 = sig * sig
        sig6 = sig2 * sig2 * sig2 
        sig12 = sig6 * sig6     

        eps = np.sqrt(atom_eps * atom_eps) 

        for kk in range(0, len(atom_x)): # loop all atoms
            for jj in range(0,len(atom_x)):
                if jj != kk :
                    x = atom_x[jj] - atom_x[kk]
                    y = atom_y[jj] - atom_y[kk]
                    r2 = np.square(x) + np.square(y)
                    r6 = r2 * r2 * r2
                    r12 = r6 * r6        
                    pre = eps*(-48.0*sig12/r12+24.0*sig6/r6)/r2
                    fx[kk] += (x*pre)
                    fy[kk] += (y*pre)
                    return fx, fy

# class definitions
class Sim():
    def __init__(self):
        self.dt = 0.005*ATOM_SIZE
        self.eps_wall=10
        self.x0=WALL_THICKNESS
        self.y0=WALL_THICKNESS
        self.x1=SCREEN_WIDTH - WALL_THICKNESS # 
        self.y1=SCREEN_HEIGHT -WALL_THICKNESS # 
        self.mass=1
        self.radius=ATOM_SIZE
        self.eps=1
        self.Natoms=0
        self.atom_x=np.empty([0])
        self.atom_y=np.empty([0])  
        self.atom_vx=np.empty([0])
        self.atom_vy=np.empty([0])
        self.atom_fx=np.empty([0])
        self.atom_fy=np.empty([0])

    def add_atom(self,xpos,ypos):
        #Initial vel, uniform
        #vel=pygame.Vector2.from_polar((0.5, rng.uniform(0, 365)))
        
        self.atom_x = np.append(self.atom_x, xpos)
        self.atom_y = np.append(self.atom_y, ypos)
        #self.atom_vx = np.append(self.atom_vx,vel.x)
        #self.atom_vy = np.append(self.atom_vy,vel.y)
        self.atom_vx = np.append(self.atom_vx,0.35)
        self.atom_vy = np.append(self.atom_vy,0.35)
        self.Natoms += 1

    def update_forces(self):
        # Reset the atoms force
        sim.atom_fx=np.zeros_like(sim.atom_x,np.float64)
        sim.atom_fy=np.zeros_like(sim.atom_x,np.float64)

        # Repulsive walls, all done in one calculation
        tmp = (self.x0-self.atom_x)*(self.x0-self.atom_x)
        tmp *= tmp*tmp
        self.atom_fx += self.eps_wall/tmp
        tmp = (self.x1-self.atom_x)*(self.x1-self.atom_x)
        tmp *= tmp*tmp
        self.atom_fx -= self.eps_wall/tmp
        tmp = (self.y0-self.atom_y)*(self.y0-self.atom_y)
        tmp *= tmp*tmp
        self.atom_fy += self.eps_wall/tmp
        tmp = (self.y1-self.atom_y)*(self.y1-self.atom_y)
        tmp *= tmp*tmp
        self.atom_fy -= self.eps_wall/tmp	

        fx, fy = update_forces_JL(self.atom_x,self.atom_y,self.eps,self.radius)
        self.atom_fx += fx
        self.atom_fy += fy



    def update(self):
        self.atom_x += self.atom_vx * self.dt
        self.atom_y += self.atom_vy * self.dt
        
        self.update_forces()
        
        self.atom_vx += self.atom_fx / self.mass * self.dt
        self.atom_vy += self.atom_fy / self.mass * self.dt 
            


# make sim object
sim = Sim()

# add some atoms
for xpos in range(50,SCREEN_WIDTH-50,70):
    for ypos in range(50,SCREEN_WIDTH-50,70):
        sim.add_atom(xpos,ypos)

print('Natoms=' + str(sim.Natoms))            



#testT = time.perf_counter()

Tstart = time.perf_counter()
Nsteps=0
Nmax=8000

running= True

while running:        
    # do the simulation update
    sim.update()    
    Nsteps += 1

    if Nsteps == Nmax:
        running=False
        Tend = time.perf_counter()


DT=Tend-Tstart
print('steps per second: ' + str(Nmax/DT))    

    #if time.perf_counter ()- testT >= 1:
    #    testT=time.perf_counter()
    #    print(Nsteps)
    #    Nsteps=0
