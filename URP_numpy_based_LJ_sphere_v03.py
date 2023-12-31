#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


"""

import pygame
import numpy as np
#import matplotlib.pyplot as plt
import time
import numba 

# box size in natural units (sigma)
BOX_HEIGHT=40
BOX_WIDTH=40

# for the graphics
RED = (255, 0, 0) 
BGCOLOR = "purple"
SCALEFACTOR=20 # Scale factor for graphics 
WALL_THICKNESS=10

rng = np.random.default_rng()

@numba.njit()
def update_forces_JL(atom_x,atom_y,atom_eps,atom_sigma):
        fx = np.zeros_like(atom_x)
        fy = np.zeros_like(atom_y)

        # # # Lennard-Jones pair forces between particles 
        # # for now all atoms are the same
        #sig = atom_sigma # atom "radius" is approx sigma/2
        sig2 = atom_sigma * atom_sigma
        sig6 = sig2 * sig2 * sig2 
        sig12 = sig6 * sig6     

        eps = atom_eps 

        for kk in range(0, len(atom_x)): # loop all atoms
            for jj in range(0,len(atom_x)):
                if jj != kk :
                    x = atom_x[jj] - atom_x[kk]
                    y = atom_y[jj] - atom_y[kk]
                    r2 = np.square(x) + np.square(y)
                    r6 = r2 * r2 * r2
                    r12 = r6 * r6        
                    pre = eps*(-48.0*sig12/r12+24.0*sig6/r6)/r2 #OBS r2 is used here
                    fx[kk] += (x*pre)
                    fy[kk] += (y*pre)                    
        return fx, fy


# class definitions

class Sim():
    def __init__(self):
        self.dt = 0.005
        self.eps_wall=10
        self.x0=0
        self.y0=0
        self.x1=BOX_WIDTH 
        self.y1=BOX_HEIGHT
        self.mass=1
        self.sigma=1
        self.eps=1
        self.Natoms=0
        self.atom_x=np.empty([0])
        self.atom_y=np.empty([0])  
        self.atom_vx=np.empty([0])
        self.atom_vy=np.empty([0])
        self.atom_fx=np.empty([0])
        self.atom_fy=np.empty([0])
        # Thermodynamic parameters
        self.langevin_kT = 2 # min="0.0" max="2.5"  value=1.0 
        self.langevin_friction = 0.030 #max="0.030", value=0.01
    
    def add_atom(self,xpos,ypos):
        #Initial vel, uniform
        vel=pygame.Vector2.from_polar((0.005, rng.uniform(0, 365)))
        
        self.atom_x = np.append(self.atom_x, xpos)
        self.atom_y = np.append(self.atom_y, ypos)
        #self.atom_vx = np.append(self.atom_vx,vel.x)
        #self.atom_vy = np.append(self.atom_vy,vel.y)
        self.atom_vx = np.append(self.atom_vx,0)
        self.atom_vy = np.append(self.atom_vy,0)
        self.Natoms += 1
        

    def update_forces(self):
        self.atom_fx=np.zeros_like(self.atom_x)
        self.atom_fy=np.zeros_like(self.atom_x)
        
        # Repulsive walls
        tmp = (self.x0-self.atom_x)*(self.x0-self.atom_x)
        tmp *= tmp*tmp
        self.atom_fx += self.eps_wall/tmp
        tmp = (self.x1-self.atom_x)*(self.x1-self.atom_x)
        tmp *= tmp*tmp
        self.atom_fx -= self.eps_wall/tmp
        tmp = (self.y0-self.atom_y)*(self.y0-self.atom_y)
        tmp *= tmp*tmp;
        self.atom_fy += self.eps_wall/tmp
        tmp = (self.y1-self.atom_y)*(self.y1-self.atom_y)
        tmp *= tmp*tmp
        self.atom_fy -= self.eps_wall/tmp      

        fx, fy = update_forces_JL(self.atom_x,self.atom_y,self.eps,self.sigma)
        self.atom_fx += fx
        self.atom_fy += fy

        # Add Langevin forces for thermostatting:
	    # Random noise from Normal distribution and friction force from velocity.
	    # The Normal distribution is approximated by adding three random numbers from a box-distribution.

		#Vector on unit circle
        for kk in range(0,self.Natoms):
            ux = 1
            uy = 1
            ur = np.sqrt(2)
            while (ur>1) :
                ux = 2.0*(rng.random()-0.5)
                uy = 2.0*(rng.random()-0.5)
                ur = np.sqrt(ux*ux+uy*uy)
            ux = ux/ur
            uy = uy/ur
            std = np.sqrt(2.0*self.langevin_kT*self.langevin_friction*self.mass/self.dt)
            flength = std*2*(rng.random()+rng.random()+rng.random()-1.5)
            self.atom_fx[kk] += flength*ux  
            self.atom_fy[kk] += flength*uy  
            self.atom_fx[kk] -= self.mass*self.langevin_friction*self.atom_vx[kk] #   // TODO: Is this right with Leap frog ???
            self.atom_fy[kk] -= self.mass*self.langevin_friction*self.atom_vy[kk]
	    
    	
    def update(self):
        self.atom_x += self.atom_vx * self.dt
        self.atom_y += self.atom_vy * self.dt
        
        self.update_forces()
        
        self.atom_vx += self.atom_fx / self.mass * self.dt
        self.atom_vy += self.atom_fy / self.mass * self.dt 
            

class Atom(pygame.sprite.Sprite):
    def __init__(self, color, radius, Natom):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.radius = radius
        self.color=color        
        self.image = pygame.Surface([radius*2, radius*2], pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()        
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), radius)
        self.rect = self.image.get_rect()
        self.pos = self.rect.center
        self.Natom = Natom # atom number in the sim
    
    def update(self,sim):    
        self.rect.center = (sim.atom_x[self.Natom]*SCALEFACTOR , sim.atom_y[self.Natom]*SCALEFACTOR) 
        
        
class Wall(pygame.sprite.Sprite):
    def __init__(self, x1 , y1, x2, y2, color, normal):
        # Call the parent class (Sprite) constructor
        super().__init__()
                
        self.color=color
        self.image = pygame.Surface([x2-x1, y2-y1], pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()        
        pygame.draw.rect(self.image, self.color, pygame.Rect(0, 0, x2-x1,y2-y1))
        self.rect = self.image.get_rect()
        self.rect.top = y1
        self.rect.left = x1
        self.normal=normal


def add_atom(sim,atoms,xpos,ypos):
    sim.add_atom(xpos,ypos)
    object_ = Atom(RED, sim.sigma/2*SCALEFACTOR, sim.Natoms-1) 
    object_.update(sim)
    atoms.add(object_)

# make sim object
sim = Sim()

# pygame setup
pygame.init()
screen = pygame.display.set_mode((BOX_WIDTH*SCALEFACTOR, BOX_HEIGHT*SCALEFACTOR))
clock = pygame.time.Clock()

# Setup a list for the sprites for atoms
atoms = pygame.sprite.Group() 

# make wall sprites
# walls=pygame.sprite.Group()
# object_=Wall(0, 0, WALL_THICKNESS, SCREEN_HEIGHT,'green', pygame.Vector2(1,0))
# walls.add(object_)
# object_=Wall(SCREEN_WIDTH-WALL_THICKNESS, 0, SCREEN_WIDTH, SCREEN_HEIGHT,'green', pygame.Vector2(-1,0))
# walls.add(object_)
# object_=Wall(WALL_THICKNESS, 0, SCREEN_WIDTH-WALL_THICKNESS, WALL_THICKNESS,'green', pygame.Vector2(0,-1))
# walls.add(object_)
# object_=Wall(WALL_THICKNESS, SCREEN_HEIGHT-WALL_THICKNESS, SCREEN_WIDTH-WALL_THICKNESS, SCREEN_HEIGHT,'green', pygame.Vector2(0,1))
# walls.add(object_)

# add some atoms
if True:
    for xpos in range(5,BOX_WIDTH-5,3):
        for ypos in range(5,BOX_HEIGHT-5,3):
            add_atom(sim, atoms, xpos, ypos)
    print('Natoms=' + str(sim.Natoms))  
            
#add_atom(sim, atoms, BOX_WIDTH/2, BOX_HEIGHT/2)

# Handle only one atom per click
new_click=True        

running = True

# counter from when to redraw the screen
Nsteps = 0

# for speed test
# Tstart = time.perf_counter()
# Nmax=12000
# testN=0


while running:
        
    # do the simulation update
    sim.update()    
    Nsteps += 1
 
    # for test with fixed number of iterations
    # testN += 1
    # if testN == Nmax:
    #     running=False
    #     Tend = time.perf_counter()

    # draw if needed
    if Nsteps >= 100: 
        Nsteps = 0

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        m_left, _, _ = pygame.mouse.get_pressed()
        if m_left and new_click:
            clickpos_x, clickpos_y = pygame.mouse.get_pos()
            add_atom(sim, atoms, clickpos_x/SCALEFACTOR, clickpos_y/SCALEFACTOR)            
            new_click=False
        if not m_left:
            new_click=True

        # Update pixel pos
        atoms.update(sim)     

        # fill the screen with a color to wipe away anything from last frame
        screen.fill(BGCOLOR)
        # draw atoms and walls
        #walls.draw(screen)
        atoms.draw(screen) 
        # flip() the display to put your work on screen
        pygame.display.flip()
        clock.tick(25) 


# DT=Tend-Tstart
# print('steps per second: ' + str(Nmax/DT))    

pygame.quit()
