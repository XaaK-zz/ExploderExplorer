import sys, pygame
import os
from pygame.locals import *
import pyganim
import random


class SimpleSprite(pygame.sprite.Sprite):
    def __init__(self,width,height,filename,screenRect,transparent=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images', filename)).convert()
        if transparent:
            self.image.set_colorkey(self.image.get_at((0,0)), RLEACCEL)
        self._screen = screenRect
        
class BaseSprite(pygame.sprite.Sprite):
    
    def __init__(self,width,height,filename,speed,screenRect,hitPoints=10,transparent=True,location=None):
        try:
            pygame.sprite.Sprite.__init__(self,self.containers)
        except AttributeError:
            pygame.sprite.Sprite.__init__(self)
        
        try:
            self.image = pygame.image.load(os.path.join('images', filename)).convert()
        except pygame.error:
            self.image = pygame.image.load(os.path.join('images', filename))
            
        if transparent:
            self.image.set_colorkey(self.image.get_at((0,0)), RLEACCEL)
        self.reloading = 0
        self._screen = screenRect
        self._hitPoints = hitPoints
        self._maxHitPoints = hitPoints
        self._speed = speed
        if location != None:
            self.rect = self.image.get_rect(top=location[0],left=location[1])
            
            #self.rect.top = location[0]
            #self.rect.left = location[1]
        
    def move(self):
        self.rect.move_ip(self._speed[0], self._speed[1])
    
    def damage(self,hitPoints):
        self._hitPoints -= hitPoints;
        if self._hitPoints <= 0:
            self.kill()
            return True;
        return False;
    
    def getMaxHP(self):
        return self._maxHitPoints
    
    def getHP(self):
        return self._hitPoints
    
    def addHP(self,hitPoints):
        self._hitPoints += hitPoints
        if self._hitPoints > self._maxHitPoints:
            self._hitPoints = self._maxHitPoints
            
    def getSpeed(self):
        return self._speed
    
    def getSize(self):
        return self.image.get_size()
    
class DamagingSprite:
    _damage = 10
    
    def __init__(self, damage):
        self._damage = damage
        
    def hit(self,target):
        if target.damage(self._damage):
            #Explosion(self._screen,1,self.rect)
            self.doExplosion(target,True)
            return True
        else:
            self.doExplosion(target,False)
            return False
    
    def doExplosion(self,target,destroyedTarget):
        return
    
class AnimatedSprite(BaseSprite):
    _images = []
    
    def __init__(self,width,height,filename,timings,speed,screenRect,hitPoints=10,loc=None):
        BaseSprite.__init__(self,width,height,filename,speed,screenRect,hitPoints,location=loc)
        
        #self._images = self.load_sliced_sprites(width,height,filename)
        self._images = self.load_sliced_sprites(width,height,self.image)
        self._anim = pyganim.PygAnimation(zip(self._images,timings))
        self._anim.play()
        self.image = self._anim.getCurrentFrame()
        self._speed = speed
        if loc == None:
            self.rect = self.image.get_rect(midbottom=screenRect.midbottom,width=width,height=height)
        else:
            self.rect.width = width
            self.rect.height = height
            
    def update(self):
        self.image = self._anim.getCurrentFrame()
        
    def load_sliced_sprites(self, width, height, master_image):
        images = []
        #master_image = pygame.image.load(os.path.join('images', filename)).convert()
    
        master_width, master_height = master_image.get_size()
        for i in xrange(int(master_width/width)):
            image = master_image.subsurface((i*width,0,width,height))
            image.set_colorkey(image.get_at((0,0)), RLEACCEL)
            images.append(image)
        return images

class SpaceShip(AnimatedSprite):
    def __init__(self, screenRect):
        AnimatedSprite.__init__(self,63,63,"SpaceShip5.png",[.05,.05],(10,10),screenRect,hitPoints=100)
    
    def handleInput(self,keystate):
        self._speed = (keystate[K_RIGHT] - keystate[K_LEFT]) * 10, (keystate[K_DOWN] - keystate[K_UP]) * 10
        self.move()
        
        firing = keystate[K_SPACE]
        
        if not self.reloading and firing:
            self.fireGun()
            
        self.reloading = firing
            
    def fireGun(self):    
        FireBall(self._screen,(self.rect.left + 4,self.rect.top - 4))
        FireBall(self._screen,(self.rect.left + 45,self.rect.top - 4))
        
class FireBall(AnimatedSprite,DamagingSprite):
    
    def __init__(self, screenRect,location):
        AnimatedSprite.__init__(self,18,28,"FireBall2.png",[.05,.05],(0,-10),screenRect)
        DamagingSprite.__init__(self,10)
        self.rect.left = location[0]
        self.rect.top = location[1]
        
    def update(self):
        AnimatedSprite.update(self)
        self.move()
        
        if self.rect.top  < 0:
            self.kill()
    
    def doExplosion(self,target,destroyedTarget):
        Explosion(self._screen,1,self.rect)
    

class Explosion(AnimatedSprite):
    def __init__(self, screenRect,type,location):
        if type == 1:
            AnimatedSprite.__init__(self,23,23,"Explosion2.png",[.05] * 8,(0,0),screenRect)
        
        self.rect = location
        
    def update(self):
        AnimatedSprite.update(self)
        if self._anim.currentFrameNum == (self._anim.numFrames-1):
            self.kill()
            
class Alien(AnimatedSprite,DamagingSprite):
    
    def __init__(self, alienType, screenRect = None,newLoc = None):
        if screenRect is None:
            screenRect = Rect(0,0,0,0)
        if newLoc is None:
            newLoc = (0,0)
            
        if alienType == 1:
            AnimatedSprite.__init__(self,60,38,"Bug1.png",[.2,.2],(10,0),screenRect,1,loc=newLoc)
            DamagingSprite.__init__(self,20)
        elif alienType == 2:
            AnimatedSprite.__init__(self,139,84,"SpikyBlob.png",[.2,.2],(3,0),screenRect,1,loc=newLoc)
            DamagingSprite.__init__(self,100)
        elif alienType == 3:
            AnimatedSprite.__init__(self,200,131,"SpikyMan.png",[.2,.2],(10,0),screenRect,1,loc=newLoc)
            DamagingSprite.__init__(self,1)
        elif alienType == 4:
            AnimatedSprite.__init__(self,144,104,"RedStoneMonster.png",[.2,.2],(15,0),screenRect,1,loc=newLoc)
            DamagingSprite.__init__(self,5)
        elif alienType == 5:
            AnimatedSprite.__init__(self,23,40,"LapisLazuMonster.png",[.2,.2],(5,0),screenRect,1,loc=newLoc)
            DamagingSprite.__init__(self,10)
        self.facing = random.choice((-1,1)) * self._speed[0]
        #self.rect.top = loc[0]
        #self.rect.left = loc[1]
        
    def update(self):
        AnimatedSprite.update(self)
        
        self.rect.move_ip(self.facing, 0)
        if not self._screen.contains(self.rect):
            self.facing = -self.facing;
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(self._screen)  
    
    def doExplosion(self,target,destroyedTarget):
        Explosion(self._screen,1,self.rect)
    
class Interface(BaseSprite):
    _hitPointXOffset = 103
    _hitPointYOffset = 12
    _currentMax = 0
    _currentHP = 0
    _currentPercentVisible = 1.0
    
    def __init__(self, screenRect,screen):
        BaseSprite.__init__(self,458,88,"Interface2.png",[0,0],screenRect)
        self.rect = self.image.get_rect(midbottom=screenRect.midbottom)
        self._hitPointImage = SimpleSprite(50,76,"HitPointsFull.png",screenRect,transparent=False)
        self._screenSurface = screen
        
    def update(self):
        BaseSprite.update(self)
        yPosMax = self._screen.height - self.image.get_rect().height + self._hitPointYOffset
        yCurrent = yPosMax + (float(self.image.get_rect().height - self._hitPointYOffset) * (1-self._currentPercentVisible))
        #print str(yPosMax) + " " + str(temp) + " " + str(yCurrent)
        self._screenSurface.blit(self._hitPointImage.image,(self._hitPointXOffset,yCurrent))
    
    def setHitPoints(self,max,current):
        self._currentHP = current
        self._currentMax = max
        #print "currentHP: " + str(self._currentHP) + " Max: " + str(self._currentMax)
        self._currentPercentVisible = float(float(self._currentHP)/float(self._currentMax))
        if self._currentPercentVisible < 0:
            self._currentPercentVisible = 0
        #print self._currentPercentVisible
        
class EnviornmentComponent(BaseSprite,DamagingSprite):

    def __init__(self, envType, screenRect=None,newlocation=None,speed=None):
        if screenRect is None:
            screenRect = Rect(0,0,0,0)
        if newlocation is None:
            newlocation = (0,0)
        if speed is None:
            speed = (0,0)
            
        if int(envType) == 1:
            BaseSprite.__init__(self,137,28,"SpikyBackground1.png",speed,screenRect,transparent=True,location=newlocation)
        DamagingSprite.__init__(self,100)
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self):
        BaseSprite.update(self)
        self.move()
        
class PowerUp(BaseSprite,DamagingSprite):
    
    def __init__(self, screenRect,screen,newlocation,speed,type):
        print "ff"
                
        self._type = type
        if type == 1:
            BaseSprite.__init__(self,14,15,"PowerUp.png",speed,screenRect,transparent=True,location=newlocation)
        DamagingSprite.__init__(self,0)
    
    def hit(self,target):
        if self._type == 1:
            target.addHP(10)
            
    def update(self):
        BaseSprite.update(self)
        self.move()