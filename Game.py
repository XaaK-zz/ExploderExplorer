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
        self._allGroup = pygame.sprite.Group()
        self._playerShotsGroup = pygame.sprite.Group()
        self._aliensGroup = pygame.sprite.Group()
    
        SpriteLib.SpaceShip.containers = self._allGroup
        SpriteLib.FireBall.containers = self._playerShotsGroup, self._allGroup
        SpriteLib.Alien.containers = self._aliensGroup, self._allGroup
        SpriteLib.Explosion.containers = self._allGroup
        SpriteLib.Interface.containers = self._allGroup
        
    def initGame(self):
        
        self._spaceShip = SpriteLib.SpaceShip(self._screenRect)
        self._alien1 = SpriteLib.Alien(self._screenRect,1,(10,10))
        self._interface = SpriteLib.Interface(self._screenRect,self._screen)
        self._interface.setHitPoints(100,100)
        
        self._allGroup.add(self._spaceShip)
        self._allGroup.add(self._alien1)
        
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
            
            #Temp - for testing
            if keystate[K_q]:
                SpriteLib.Alien(self._screenRect,1,(10,10))
        
            #Collision Detection - shots vs aliens
            collision = pygame.sprite.groupcollide(self._playerShotsGroup, self._aliensGroup, True, False)
            for shot in collision.iterkeys():
                shot.hit(collision[shot][0])
             
            #Collision Detection - player vs aliens
            for alien in pygame.sprite.spritecollide(self._spaceShip, self._aliensGroup, False):
                if alien.hit(self._spaceShip):
                    #game over - TODO, menu system
                    print "Game Over!!!"
                    return;
                self._interface.setHitPoints(self._spaceShip.getMaxHP(),self._spaceShip.getHP())
                alien.kill()
           
             # clear/erase the last drawn sprites
            self._allGroup.clear(self._screen, self._background)
        
            #update all the sprites
            self._allGroup.update()
            
            #screen.blit(spaceShip, spaceShipRect)
            #pygame.display.flip()
        
             #draw the scene
            dirty = self._allGroup.draw(self._screen)
            #pygame.display.update(dirty)
            pygame.display.update()
            
            #cap the framerate
            self._clock.tick(30)
    
        