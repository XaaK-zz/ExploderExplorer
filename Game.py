import sys, pygame
import os
from pygame.locals import *
import pyganim
import SpriteLib

class Game():
    
    def __init__(self,width,height):
        
        pygame.init()
        size = width, height
        black = 0, 0, 0
        
        #general init
        self._screen = pygame.display.set_mode(size)
        self._screenRect = Rect(0, 0, width, height)
        self._background = pygame.Surface(self._screenRect.size).convert()
        self._background.fill(black)
        self._screen.blit(self._background, (0,0))
        
        pygame.display.flip()
        
        self._clock = pygame.time.Clock()
        
        #Group creation
        self._all = pygame.sprite.Group()
        
        SpriteLib.SpaceShip.containers = self._all
        SpriteLib.FireBall.containers = self._all
        SpriteLib.Alien.containers = self._all
        
    def initGame(self):
        
        self._spaceShip = SpriteLib.SpaceShip(self._screenRect)
        self._alien1 = SpriteLib.Alien(self._screenRect,1,(10,10))
        
        self._all.add(self._spaceShip)
        self._all.add(self._alien1)
        
    def gameLoop(self):
        
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
        
            #get key state                
            keystate = pygame.key.get_pressed()
            
            #handle player movement
            self._spaceShip.handleInput(keystate)
            
                
            if keystate[K_SPACE]:
                fireBall1 = SpriteLib.FireBall(self._screenRect)
                fireBall1.rect.top = self._spaceShip.rect.top - 10
                fireBall1.rect.left = self._spaceShip.rect.left + 4
                self._all.add(fireBall1)
                fireBall1 = SpriteLib.FireBall(self._screenRect)
                fireBall1.rect.top = self._spaceShip.rect.top - 10
                fireBall1.rect.left = self._spaceShip.rect.right - 18
                self._all.add(fireBall1)
            if keystate[K_q]:
                alien2 = SpriteLib.Alien(self._screenRect,1,(10,10))
                self._all.add(alien2)
        
             # clear/erase the last drawn sprites
            self._all.clear(self._screen, self._background)
        
            #update all the sprites
            self._all.update()
            
            #screen.blit(spaceShip, spaceShipRect)
            #pygame.display.flip()
        
             #draw the scene
            dirty = self._all.draw(self._screen)
            #pygame.display.update(dirty)
            pygame.display.update()
            
            #cap the framerate
            self._clock.tick(30)
    
        