import sys, pygame
import os
from pygame.locals import *
import pyganim
import SpriteLib
import xml.etree.cElementTree as ET
import Level

class GameState:
    GameMenu, LevelSelect, GamePlay, GameOver = range(4)
    
#################################################################
#Game Class
#   Primary object in the system - controls all aspects of the game
#
#################################################################
class Game():
    _currentLevelNumber=1
    _levelData=None
    _currentLevel=None
    _currentMode = GameState.GameMenu 
    
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
        SpriteLib.PowerUp.containers = self._aliensGroup, self._allGroup
        
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
        
        #init the first level
        self.initLevel(1)
        
    #####################################################################
    #initLevel
    #   Read the level information out of the stored xml level data and
    #       populate the level-specific data
    #####################################################################
    def initLevel(self,levelNumber):
        self._currentLevel = Level.Level()
        self._currentLevel.readLevelData(self._levelData,1,self._screenRect.height)
        
    #####################################################################
    #gameLoop
    #   Primary loop for the game
    #####################################################################
    def gameLoop(self):
        
        while 1:
            
            #TEMP###########################
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
            #################################
            
            if self._currentMode == GameState.GameMenu:
                if self.doGameMenu():
                    return
            elif self._currentMode == GameState.LevelSelect:
                self.doLevelSelect()
            elif self._currentMode == GameState.GamePlay:
                self.doGamePlay()
            elif self._currentMode == GameState.GameOver:
                self.doGameOver()
            
            #cap the framerate
            self._clock.tick(30)
    
    def doGameMenu(self):
        # Fill background
	background = pygame.Surface(self._screen.get_size())
	background = background.convert()
	background.fill((250, 250, 250))

        #load logo image
        if not hasattr(self, '_logo'):
            self._logo = SpriteLib.SimpleSprite(236,103,"Logo.png",self._screenRect)
            self._menuFont = pygame.font.Font(None, 40)
            self._selectedMenuItem = 0
            self._keypressed = False
            
	# Display menu
        if self._selectedMenuItem == 0:
            menu1 = self._menuFont.render("Start Game", 1, (10, 10, 240))
        else:
            menu1 = self._menuFont.render("Start Game", 1, (10, 10, 10))
        if self._selectedMenuItem == 1:
            menu2 = self._menuFont.render("Quit Game", 1, (10, 10, 240))
        else:
            menu2 = self._menuFont.render("Quit Game", 1, (10, 10, 10))
            
	textpos = menu1.get_rect()
	textpos.centerx = background.get_rect().centerx
        textpos.centery = (background.get_rect().centery) - textpos.height
	background.blit(menu1, textpos)
        textpos = menu2.get_rect()
	textpos.centerx = background.get_rect().centerx
        textpos.centery = (background.get_rect().centery) + textpos.height
	background.blit(menu2, textpos)
        pos = self._logo.image.get_rect()
        pos.centerx = background.get_rect().centerx
        background.blit(self._logo.image,pos)
        
        #handle input
        keystate = pygame.key.get_pressed()
        keypressed = False
        if keystate[K_UP]:
            keypressed = True
            self._keypressed = True
            self._selectedMenuItem -= 1
            if self._selectedMenuItem < 0:
                self._selectedMenuItem = 0
        if keystate[K_DOWN]:
            keypressed = True
            self._keypressed = True
            self._selectedMenuItem += 1
            if self._selectedMenuItem > 1:
                self._selectedMenuItem = 1
        if keystate[K_RETURN]:
            if self._selectedMenuItem == 0:
                self._currentMode = GameState.GamePlay
                background.fill((0, 0, 0))
            elif self._selectedMenuItem == 1:
               return True
                
        if not keypressed:
            self._keypressed = keypressed
            
	# Blit everything to the screen
	self._screen.blit(background, (0, 0))
	pygame.display.flip()
        
        return False
    
    def doLevelSelect(self):
        return
    
    def doGamePlay(self):
        #update level data
        envImages, enemies = self._currentLevel.update(1)
        
        for envImage in envImages:
            SpriteLib.EnviornmentComponent(int(envImage.type),self._screenRect,(-100,envImage.xPos),
                                           (envImage.movementX,envImage.movementY))
        
        for enemy in enemies:
            SpriteLib.Alien(int(enemy.type),self._screenRect,(-10,enemy.xPos))
        
        #get key state                
        keystate = pygame.key.get_pressed()
        
        #handle player movement
        self._spaceShip.handleInput(keystate)
        
        #Temp - for testing
        if keystate[K_q]:
            SpriteLib.Alien(1,self._screenRect,(10,10))
        if keystate[K_w]:
            SpriteLib.Alien(2,self._screenRect,(50,10))
        if keystate[K_h]:
            SpriteLib.Alien(3,self._screenRect,(70,10))
        if keystate[K_o]:
            SpriteLib.Alien(4,self._screenRect,(10,10))
        if keystate[K_y]:
            SpriteLib.PowerUp(self._screenRect,self._screen,(0,50),(0,10),1)
        if keystate[K_k]:
             SpriteLib.Alien(5,self._screenRect,(10,10))
        
    
    
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

        #draw the scene
        dirty = self._allGroup.draw(self._screen)
        #pygame.display.update(dirty)
        pygame.display.update()
        
    def doGameOver(self):
        return