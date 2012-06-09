import sys, pygame
import os
from pygame.locals import *
import pyganim
import random

class BaseSprite(pygame.sprite.Sprite):
    _images = []
    _speed = 10,0
    
    def __init__(self,width,height,filename,timings,speed,screenRect):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self._images = self.load_sliced_sprites(width,height,filename)
        self._anim = pyganim.PygAnimation(zip(self._images,timings))
        self._anim.play()
        self.image = self._anim.getCurrentFrame()
        self.rect = self.image.get_rect(midbottom=screenRect.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1
        self._speed = speed
        self._screen = screenRect
        
    def move(self):
        self.rect.move_ip(self._speed[0], self._speed[1])
        #self.rect = self.rect.clamp(self._screen)
    
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

class SpaceShip(BaseSprite):
    def __init__(self, screenRect):
        BaseSprite.__init__(self,63,63,"SpaceShip5.png",[.05,.05],(10,10),screenRect)
    
    def handleInput(self,keystate):
        self._speed = (keystate[K_RIGHT] - keystate[K_LEFT]) * 10, (keystate[K_DOWN] - keystate[K_UP]) * 10
        self.move()
        
class FireBall(BaseSprite):
    def __init__(self, screenRect):
        BaseSprite.__init__(self,18,28,"FireBall2.png",[.05,.05],(0,-10),screenRect)

    def update(self):
        BaseSprite.update(self)
        self.move()
        
        #self.rect.left += self._speed[0]
        #self.rect.top += self._speed[1]
        if self.rect.top  < 0:
            self.kill()
                
class Alien(BaseSprite):
    
    def __init__(self, screenRect,alienType,loc):
        if alienType == 1:
            BaseSprite.__init__(self,60,38,"Bug1.png",[.2,.2],(10,0),screenRect)
            
        self.facing = random.choice((-1,1)) * self._speed[0]
        self.rect.top = loc[0]
        self.rect.left = loc[1]
        
    def update(self):
        BaseSprite.update(self)
        
        self.rect.move_ip(self.facing, 0)
        if not self._screen.contains(self.rect):
            self.facing = -self.facing;
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(self._screen)
            
        