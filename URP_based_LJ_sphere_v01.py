#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
From 
pygame docs


"""

import pygame
import numpy as np
import matplotlib.pyplot as plt


RED = (255, 0, 0) 
BGCOLOR = "purple"
ATOM_SIZE=10 # pixel diameter for one atom
MAX_SPEED=10 # 
SCREEN_HEIGHT=500
SCREEN_WIDTH=800
WALL_THICKNESS=10

rng = np.random.default_rng()

# class definitions


class Sim():
    def __init__(self):
        self.eps=1
        self.dt = 0.005*ATOM_SIZE
        self.eps_wall=10
        self.x0=WALL_THICKNESS
        self.y0=WALL_THICKNESS
        self.x1=SCREEN_WIDTH - WALL_THICKNESS # 
        self.y1=SCREEN_HEIGHT -WALL_THICKNESS # 

    def update_forces(self,atoms):
        
        for atom in atoms:
            atom.f = pygame.Vector2((0,0))

            # Repulsive walls
            tmp = (self.x0-atom.pos.x)*(self.x0-atom.pos.x)
            tmp *= tmp*tmp
            atom.f.x += self.eps_wall/tmp
            tmp = (self.x1-atom.pos.x)*(self.x1-atom.pos.x)
            tmp *= tmp*tmp
            atom.f.x -= self.eps_wall/tmp
            tmp = (self.y0-atom.pos.y)*(self.y0-atom.pos.y)
            tmp *= tmp*tmp;
            atom.f.y += self.eps_wall/tmp
            tmp = (self.y1-atom.pos.y)*(self.y1-atom.pos.y)
            tmp *= tmp*tmp
            atom.f.y -= self.eps_wall/tmp      
	    



            # Lennard-Jones pair forces between particles
            atoms2=atoms.copy()
            atoms2.remove(atom) # list of other atoms
            for atom2 in atoms2:
                sig = atom.radius + atom2.radius
                sig2 = sig * sig
                sig6 = sig2 * sig2 * sig2 
                sig12 = sig6 * sig6     
                eps = np.sqrt(atom.eps * atom2.eps) 
                r = atom2.pos - atom.pos
                r2 = r.length() * r.length() 
                r6 = r2 * r2 * r2
                r12 = r6 * r6        
                pre = eps*(-48.0*sig12/r12+24.0*sig6/r6)/r2
                atom.f += r*pre

		
    def update(self,atoms):
        for atom in atoms:
            atom.pos +=atom.vel * self.dt
        self.update_forces(atoms)
        for atom in atoms: 
            atom.vel += atom.f / atom.mass * self.dt
 
class Atom(pygame.sprite.Sprite):
    def __init__(self, color, radius):
        # Call the parent class (Sprite) constructor
        super().__init__()
        
        self.color=color

        #Initial vel, uniform
        self.vel=pygame.Vector2.from_polar((rng.uniform(0, MAX_SPEED), rng.uniform(0, 365)))
        #self.vel = pygame.Vector2((0,0))
        # Initial acceleration
        self.a = pygame.Vector2((0,0))
        self.f = pygame.Vector2((0,0))
        
        self.mass=1
        self.radius=radius
        self.eps=1
        self.image = pygame.Surface([radius*2, radius*2], pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()        
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), radius)
        self.rect = self.image.get_rect()
        self.pos = self.rect.center
        
    def update(self):
        # self.pos += (self.vel * dt * ATOM_SIZE)
        self.rect.center =self.pos 
        
        
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


# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
last_draw=0 # time for last draw


# some setup for looking at energy
Etots=[]
ts=[]
kk=0

# make sim object
sim = Sim()

# make walls
walls=pygame.sprite.Group()
object_=Wall(0, 0, WALL_THICKNESS, SCREEN_HEIGHT,'green', pygame.Vector2(1,0))
walls.add(object_)
object_=Wall(SCREEN_WIDTH-WALL_THICKNESS, 0, SCREEN_WIDTH, SCREEN_HEIGHT,'green', pygame.Vector2(-1,0))
walls.add(object_)
object_=Wall(WALL_THICKNESS, 0, SCREEN_WIDTH-WALL_THICKNESS, WALL_THICKNESS,'green', pygame.Vector2(0,-1))
walls.add(object_)
object_=Wall(WALL_THICKNESS, SCREEN_HEIGHT-WALL_THICKNESS, SCREEN_WIDTH-WALL_THICKNESS, SCREEN_HEIGHT,'green', pygame.Vector2(0,1))
walls.add(object_)

# Setup a list for the atoms
atoms = pygame.sprite.Group() 

# Handle only one atom per click
new_click=True        

while running:
    
    
    
    # do the simulation update
    sim.update(atoms)    
    
    # draw if needed
    if pygame.time.get_ticks()/1000 - last_draw >= 1/50:

        last_draw=pygame.time.get_ticks()/1000

        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        m_left, _, _ = pygame.mouse.get_pressed()
        if m_left and new_click:
            object_ = Atom(RED, ATOM_SIZE) 
            object_.pos = pygame.mouse.get_pos()
            atoms.add(object_)
            new_click=False
        if not m_left:
            new_click=True

        # Update pixel pos
        atoms.update()     

        # fill the screen with a color to wipe away anything from last frame
        screen.fill(BGCOLOR)
        # draw atoms and walls
        walls.draw(screen)
        atoms.draw(screen) 
        # flip() the display to put your work on screen
        pygame.display.flip()

pygame.quit()

#Make a plot of energy
if False:
    fig, ax = plt.subplots()
    ax.plot(ts, Etots, linewidth=2.0)
    plt.show()
