import sys, pygame
import os
from pygame.locals import *
import pyganim
import random

class BaseSprite(pygame.sprite.Sprite):
    _speed = 10,0
    
    def __init__(self,width,height,filename,speed,screenRect,hitPoints=10):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image = pygame.image.load(os.path.join('images', filename)).convert()
        self.image.set_colorkey(self.image.get_at((0,0)), RLEACCEL)
        self.reloading = 0
        self._screen = screenRect
        self._hitPoints = hitPoints
        
    def move(self):
        self.rect.move_ip(self._speed[0], self._speed[1])
    
    def damage(self,hitPoints):
        self._hitPoints -= hitPoints;
        if self._hitPoints <= 0:
            self.kill()
            return True;
        return False;

class AnimatedSprite(BaseSprite):
    _images = []
    
    def __init__(self,width,height,filename,timings,speed,screenRect,hitPoints=10):
        BaseSprite.__init__(self,width,height,filename,speed,screenRect,hitPoints)
        
        self._images = self.load_sliced_sprites(width,height,filename)
        self._anim = pyganim.PygAnimation(zip(self._images,timings))
        self._anim.play()
        self.image = self._anim.getCurrentFrame()
        self._speed = speed
        self.rect = self.image.get_rect(midbottom=screenRect.midbottom)
        
    def update(self):
        self.image = self._anim.getCurrentFrame()
    
        
    def load_sliced_sprites(self, width, height, filename):
        images = []
        master_image = pygame.image.load(os.path.join('images', filename)).convert()
    
        master_width, master_height = master_image.get_size()
        for i in xrange(int(master_width/width)):
            image = master_image.subsurface((i*width,0,width,height))
            image.set_colorkey(image.get_at((0,0)), RLEACCEL)
            images.append(image)
        return images

class SpaceShip(AnimatedSprite):
    def __init__(self, screenRect):
        AnimatedSprite.__init__(self,63,63,"SpaceShip5.png",[.05,.05],(10,10),screenRect)
    
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
        
class FireBall(AnimatedSprite):
    _damage = 10
    
    def __init__(self, screenRect,location):
        AnimatedSprite.__init__(self,18,28,"FireBall2.png",[.05,.05],(0,-10),screenRect)
        self.rect.left = location[0]
        self.rect.top = location[1]
        
    def update(self):
        AnimatedSprite.update(self)
        self.move()
        
        if self.rect.top  < 0:
            self.kill()
    
    def hit(self,target):
        if target.damage(self._damage):
            Explosion(self._screen,1,self.rect)
            return True;
        else:
            return False;

class Explosion(AnimatedSprite):
    def __init__(self, screenRect,type,location):
        if type == 1:
            AnimatedSprite.__init__(self,23,23,"Explosion2.png",[.05] * 8,(0,0),screenRect)
        
        self.rect = location
        
    def update(self):
        AnimatedSprite.update(self)
        if self._anim.currentFrameNum == (self._anim.numFrames-1):
            self.kill()
            
class Alien(AnimatedSprite):
    
    def __init__(self, screenRect,alienType,loc):
        if alienType == 1:
            AnimatedSprite.__init__(self,60,38,"Bug1.png",[.2,.2],(10,0),screenRect,1)
            
        self.facing = random.choice((-1,1)) * self._speed[0]
        self.rect.top = loc[0]
        self.rect.left = loc[1]
        
    def update(self):
        AnimatedSprite.update(self)
        
        self.rect.move_ip(self.facing, 0)
        if not self._screen.contains(self.rect):
            self.facing = -self.facing;
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(self._screen)
            

class Interface(BaseSprite):
    
    def __init__(self, screenRect):
        BaseSprite.__init__(self,458,88,"Interface2.png",[0,0],screenRect)
        self.rect = self.image.get_rect(midbottom=screenRect.midbottom)
       