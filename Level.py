import sys, pygame
import os
from pygame.locals import *
import pyganim
import random
import xml.etree.cElementTree as ET
import copy

class EnviornmentImage:
    globalYPos = 0
    xPos = 0
    type = 0
    movementX = 0
    movementY = 0

class Enemy:
    globalYPos = 0
    xPos = 0
    type = 0
    
class Level:
    _levelNumber=1
    _levelHeight=1000
    _currentLevelPosition=0
    _levelNode=None
    _levelName=""
    _enviornmentImages = []
    _enemies = []
    _screenHeight = 0
    
    def __init__(self,levelData,levelNumber,screenHeight):
        self._levelNumber = levelNumber
        self._levelNode = levelData.find(".//level[@number='" + str(levelNumber) + "']")
        if self._levelNode == None:
            print "Failed to load level data."
            return
        self._levelHeight =  self._levelNode.attrib["height"]
        self._levelName = self._levelNode.attrib["name"]
        self._currentLevelPosition = 0
        self._screenHeight = screenHeight
        #load the background images
        for eImage in self._levelNode.iterfind("enviornmentImages/enviornmentImage"):
            temp = EnviornmentImage()
            temp.globalYPos = int(eImage.attrib["globalYPos"])
            temp.xPos = int(eImage.attrib["xPos"])
            temp.type = int(eImage.attrib["type"])
            temp.movementX = int(eImage.attrib["movementX"])
            temp.movementY = int(eImage.attrib["movementY"])
            self._enviornmentImages.append(temp)
        #load the enemies
        for enemy in self._levelNode.iterfind("enemies/enemy"):
            temp = Enemy()
            temp.globalYPos = int(eImage.attrib["globalYPos"])
            temp.xPos = int(eImage.attrib["xPos"])
            temp.type = int(eImage.attrib["type"])
            self._enemies.append(temp)
            
    def update(self,speed):
        self._currentLevelPosition += speed
        returnedEnvImages = []
        returnedEnemies = []
        for image in self._enviornmentImages:
            if (self._currentLevelPosition + self._screenHeight) > image.globalYPos:
                returnedEnvImages.append(copy.deepcopy(image))
                self._enviornmentImages.remove(image)
            else:
                break;
            
        for enemy in self._enemies:
            if (self._currentLevelPosition + self._screenHeight) > enemy.globalYPos:
                returnedEnemies.append(copy.deepcopy(enemy))
                self._enemies.remove(enemy)
            else:
                break;
            
        return returnedEnvImages, returnedEnemies