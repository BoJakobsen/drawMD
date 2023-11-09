#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
From 
pygame docs


"""

import pygame
import numpy as np


RED = (255, 0, 0) 
BGCOLOR = "purple"
ATOM_SIZE=10
MAX_SPEED=200
SCREEN_HEIGHT=500
SCREEN_WIDTH=800

rng = np.random.default_rng()

# class definitions

class Atom(pygame.sprite.Sprite):
    def __init__(self, color, radius):
        # Call the parent class (Sprite) constructor
        super().__init__()
        
        self.color=color
        self.radius=radius
        self.vel=pygame.Vector2(rng.uniform(-1, 1), rng.uniform(-1, 1)) * MAX_SPEED
        
        self.image = pygame.Surface([radius*2, radius*2], pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()        
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), radius)
        self.rect = self.image.get_rect()
        self.pos = self.rect.center
        
    def update(self):
        self.pos += (self.vel * dt)
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
dt = 0

# player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)


# make walls
walls=pygame.sprite.Group()

object_=Wall(0, 0, 10, SCREEN_HEIGHT,'green', pygame.Vector2(1,0))
walls.add(object_)
object_=Wall(SCREEN_WIDTH-10, 0, SCREEN_WIDTH, SCREEN_HEIGHT,'green', pygame.Vector2(-1,0))
walls.add(object_)
object_=Wall(10, 0, SCREEN_WIDTH-10, 10,'green', pygame.Vector2(0,-1))
walls.add(object_)
object_=Wall(10, SCREEN_HEIGHT-10, SCREEN_WIDTH-10, SCREEN_HEIGHT,'green', pygame.Vector2(0,1))
walls.add(object_)

# Setup a list for the atoms
atoms = pygame.sprite.Group() 
#object_ = Atom(RED, ATOM_SIZE) 
#object_.rect.x = 200
#object_.rect.y = 300
#atoms.add(object_) 

new_click=True        

while running:
    
    
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
        
    atoms.update() 

    #Check for collition with wall
    for wall in walls.sprites():
        #wall_hit_list = pygame.sprite.spritecollide(wall, atoms, True)
        atom_list = pygame.sprite.spritecollide(wall, atoms, False)
        for atom in atom_list:
            atom.vel=atom.vel.reflect(wall.normal)
                
 
    # check for atom colitions
    atoms2=atoms.copy()
    for atom in atoms:
        atoms2.remove(atom)
        coll_list = pygame.sprite.spritecollide(atom, atoms2, False)
        for atom2 in coll_list:
            #Hard sphere interactions
            vel1=atom.vel
            vel2=atom2.vel
            atom.vel=vel2
            atom2.vel=vel1
            
        
        
        
    # fill the screen with a color to wipe away anything from last frame
    screen.fill(BGCOLOR)

    #player_pos.x, player_pos.y = pygame.mouse.get_pos()
    #pygame.draw.circle(screen, "red", player_pos, 40)

    walls.draw(screen)
    atoms.draw(screen) 
    

    
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
