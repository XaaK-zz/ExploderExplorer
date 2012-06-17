import sys, pygame
import os
from pygame.locals import *
import pyganim
import SpriteLib
import xml.etree.cElementTree as ET
import Level

#################################################################
#Game Class
#   Primary object in the system - controls all aspects of the game
#
#################################################################
class Game():
    _currentLevelNumber=1
    _levelData=None
    _currentLevel=None
    
    ###########################################
    #Game Constructor
    #   Initialize the object but doesn't
    #       start game until initGame called
    ###########################################
    def __init__(self,width,height,levelXMLDoc):
        
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
        self._backgroundGroup = pygame.sprite.Group()
    
        SpriteLib.SpaceShip.containers = self._allGroup
        SpriteLib.FireBall.containers = self._playerShotsGroup, self._allGroup
        SpriteLib.Alien.containers = self._aliensGroup, self._allGroup
        SpriteLib.Explosion.containers = self._allGroup
        SpriteLib.Interface.containers = self._allGroup
        SpriteLib.EnviornmentComponent.containers = self._backgroundGroup, self._allGroup
        
        #level doc
        self._levelData = ET.parse(levelXMLDoc)
        
    ################################################
    #initGame
    #   Initializes a new game.  This would be
    #       called each time a new game starts
    ################################################
    def initGame(self):
        
        #create player object
        self._spaceShip = SpriteLib.SpaceShip(self._screenRect)
        #create UI interface objects
        self._interface = SpriteLib.Interface(self._screenRect,self._screen)
        self._interface.setHitPoints(100,100)
        
        #temp - create placeholder alien
        self._alien1 = SpriteLib.Alien(self._screenRect,1,(10,10))
        
        #temp - create background image
        #self._back1 = SpriteLib.EnviornmentComponent(self._screenRect,self._screen,(100,517),(0,1))
    
        self.initLevel(1)
        
    #####################################################################
    #initLevel
    #   Read the level information out of the stored xml level data and
    #       populate the level-specific data
    #####################################################################
    def initLevel(self,levelNumber):
        self._currentLevel = Level.Level(self._levelData,1,self._screenRect.height)
        #self._currentLevelNumber=levelNumber
        #temp = self._levelData.findall("//level[@number='" + str(levelNumber) + "']")
        #print temp
        
    def gameLoop(self):
        
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
        
            #update level data
            envImages, enemies = self._currentLevel.update(1)
            
            for envImage in envImages:
                print "creating backgound image"
                SpriteLib.EnviornmentComponent(self._screenRect,self._screen,(0,envImage.xPos),
                                               (envImage.movementX,envImage.movementY))
            
            for enemy in enemies:
                SpriteLib.Alien(self._screenRect,int(enemy.type),(0,enemy.xPos))
            
            #get key state                
            keystate = pygame.key.get_pressed()
            
            #handle player movement
            self._spaceShip.handleInput(keystate)
            
            #Temp - for testing
            if keystate[K_q]:
                SpriteLib.Alien(self._screenRect,1,(10,10))
            if keystate[K_w]:
                SpriteLib.Alien(self._screenRect,2,(50,10))
            if keystate[K_h]:
                SpriteLib.Alien(self._screenRect,3,(70,10))
        
            #Collision Detection - shots vs aliens
            collision = pygame.sprite.groupcollide(self._playerShotsGroup, self._aliensGroup, False, False)
            for shot in collision.iterkeys():
                if pygame.sprite.collide_mask(shot,collision[shot][0]):
                    shot.hit(collision[shot][0])
                    shot.kill()
             
            #Collision Detection - shots vs background
            pygame.sprite.groupcollide(self._playerShotsGroup, self._backgroundGroup, True, False,pygame.sprite.collide_mask)
    
            #Collision Detection - player vs aliens
            for alien in pygame.sprite.spritecollide(self._spaceShip, self._aliensGroup, False):
                if alien.hit(self._spaceShip):
                    #game over - TODO, menu system
                    print "Game Over!!!"
                    return;
                self._interface.setHitPoints(self._spaceShip.getMaxHP(),self._spaceShip.getHP())
                alien.kill()
           
            #Collision Detection - player vs background 
            for backgroundImage in pygame.sprite.spritecollide(self._spaceShip, self._backgroundGroup, False):
                if pygame.sprite.collide_mask(self._spaceShip,backgroundImage):
                    if backgroundImage.hit(self._spaceShip):
                        print "ouch."
                        return
                    self._interface.setHitPoints(self._spaceShip.getMaxHP(),self._spaceShip.getHP())
                
                
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
    
        