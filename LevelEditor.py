import  wx
import  wx.lib.scrolledpanel as scrolled
import SpriteLib
from pygame.locals import *
import sys, pygame
import Level

#----------------------------------------------------------------------

class DragShape:
    def __init__(self, bmp,spriteType,spriteSubType):
        self.bmp = bmp
        self.pos = (0,0)
        self.shown = True
        self.text = None
        self.fullscreen = False
        self.spriteType = spriteType
        self.spriteSubType = spriteSubType
        
    def HitTest(self, pt):
        rect = self.GetRect()
        return rect.InsideXY(pt.x, pt.y)

    def GetRect(self):
        return wx.Rect(self.pos[0], self.pos[1],
                      self.bmp.GetWidth(), self.bmp.GetHeight())

    def Draw(self, dc, op = wx.COPY):
        if self.bmp.Ok():
            memDC = wx.MemoryDC()
            memDC.SelectObject(self.bmp)

            dc.Blit(self.pos[0], self.pos[1],
                    self.bmp.GetWidth(), self.bmp.GetHeight(),
                    memDC, 0, 0, op, True)

            return True
        else:
            return False



#----------------------------------------------------------------------

class DragableCanvasBitmap(wx.StaticBitmap):
    def __init__(self, parent):
        self.shapes = []
        self.dragImage = None
        self.dragShape = None
        self.hiliteShape = None
        
        #self.img = wx.Image("temp.png", wx.BITMAP_TYPE_ANY)
        self.img = wx.EmptyImage(320, 1000)
        self.img = wx.BitmapFromImage(self.img)
        wx.StaticBitmap.__init__(self,parent, wx.ID_ANY,self.img)
        
        #bmp = wx.Bitmap('images/LapisLazuMonster.png')
        #shape = DragShape(bmp)
        #shape.pos = (5, 5)
        #self.shapes.append(shape)
        
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)

    def AddImage(self,sprite,type,subType):
        width,height = sprite.getSize()
        s = pygame.image.tostring(sprite.image, 'RGB')
        img = wx.ImageFromData(width, height, s)
        color = sprite.image.get_at((0,0))
        img = img.Scale(width/2,height/2,wx.IMAGE_QUALITY_HIGH)
        bmp = wx.BitmapFromImage(img)
        mask = wx.Mask(bmp, (color.r,color.g,color.b))
        
        bmp.SetMask(mask)
        shape = DragShape(bmp,type,subType)
        shape.pos = (5, 5)
        self.shapes.append(shape)
        self.Refresh()
            
    # Go through our list of shapes and draw them in whatever place they are.
    def DrawShapes(self, dc):
        for shape in self.shapes:
            if shape.shown:
                shape.Draw(dc)

    # This is actually a sophisticated 'hit test', but in this
    # case we're also determining which shape, if any, was 'hit'.
    def FindShape(self, pt):
        for shape in self.shapes:
            if shape.HitTest(pt):
                return shape
        return None


    # Clears the background, then redraws it. If the DC is passed, then
    # we only do so in the area so designated. Otherwise, it's the whole thing.
    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

    # Fired whenever a paint event occurs
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.img,0,0,True)
        self.PrepareDC(dc)
        self.DrawShapes(dc)
        #evt.Skip()
        
    # Left mouse button is down.
    def OnLeftDown(self, evt):
        # Did the mouse go down on one of our shapes?
        shape = self.FindShape(evt.GetPosition())

        # If a shape was 'hit', then set that as the shape we're going to
        # drag around. Get our start position. Dragging has not yet started.
        # That will happen once the mouse moves, OR the mouse is released.
        if shape:
            self.dragShape = shape
            self.dragStartPos = evt.GetPosition()

    # Left mouse button up.
    def OnLeftUp(self, evt):
        if not self.dragImage or not self.dragShape:
            self.dragImage = None
            self.dragShape = None
            return

        # Hide the image, end dragging, and nuke out the drag image.
        self.dragImage.Hide()
        self.dragImage.EndDrag()
        self.dragImage = None

        if self.hiliteShape:
            self.RefreshRect(self.hiliteShape.GetRect())
            self.hiliteShape = None

        self.dragShape.pos = (
            self.dragShape.pos[0] + evt.GetPosition()[0] - self.dragStartPos[0],
            self.dragShape.pos[1] + evt.GetPosition()[1] - self.dragStartPos[1]
            )
            
        self.dragShape.shown = True
        self.RefreshRect(self.dragShape.GetRect())
        self.dragShape = None


    # The mouse is moving
    def OnMotion(self, evt):
        # Ignore mouse movement if we're not dragging.
        if not self.dragShape or not evt.Dragging() or not evt.LeftIsDown():
            return

        # if we have a shape, but haven't started dragging yet
        if self.dragShape and not self.dragImage:

            # only start the drag after having moved a couple pixels
            tolerance = 2
            pt = evt.GetPosition()
            dx = abs(pt.x - self.dragStartPos.x)
            dy = abs(pt.y - self.dragStartPos.y)
            if dx <= tolerance and dy <= tolerance:
                return

            # refresh the area of the window where the shape was so it
            # will get erased.
            self.dragShape.shown = False
            self.RefreshRect(self.dragShape.GetRect(), True)
            self.Update()

            if self.dragShape.text:
                self.dragImage = wx.DragString(self.dragShape.text,
                                              wx.StockCursor(wx.CURSOR_HAND))
            else:
                self.dragImage = wx.DragImage(self.dragShape.bmp,
                                             wx.StockCursor(wx.CURSOR_HAND))

            hotspot = self.dragStartPos - self.dragShape.pos
            self.dragImage.BeginDrag(hotspot, self, self.dragShape.fullscreen)

            self.dragImage.Move(pt)
            self.dragImage.Show()


        # if we have shape and image then move it, posibly highlighting another shape.
        elif self.dragShape and self.dragImage:
            onShape = self.FindShape(evt.GetPosition())
            unhiliteOld = False
            hiliteNew = False

            # figure out what to hilite and what to unhilite
            if self.hiliteShape:
                if onShape is None or self.hiliteShape is not onShape:
                    unhiliteOld = True

            if onShape and onShape is not self.hiliteShape and onShape.shown:
                hiliteNew = True

            # if needed, hide the drag image so we can update the window
            if unhiliteOld or hiliteNew:
                self.dragImage.Hide()

            if unhiliteOld:
                dc = wx.ClientDC(self)
                self.hiliteShape.Draw(dc)
                self.hiliteShape = None

            if hiliteNew:
                dc = wx.ClientDC(self)
                self.hiliteShape = onShape
                self.hiliteShape.Draw(dc, wx.INVERT)

            # now move it and show it again if needed
            self.dragImage.Move(evt.GetPosition())
            if unhiliteOld or hiliteNew:
                self.dragImage.Show()

#----------------------------------------------------------------------

class LevelEditorWindow(wx.ScrolledWindow):
    def __init__(self, parent, ID):
        wx.ScrolledWindow.__init__(self, parent, ID)  

        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)    
        self.scrollPnlSizer = wx.BoxSizer(wx.VERTICAL)
        self.contentSizer = wx.FlexGridSizer(rows=2, cols=2, hgap=10, vgap=5)
        
        #create panel for level data
        self.levelPanel = scrolled.ScrolledPanel(self, -1, size=(350,400),
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="levelPanel" )
        
        self.staticBitmap = DragableCanvasBitmap(self.levelPanel)
        
        self.scrollPnlSizer.Add(self.staticBitmap, 0, wx.ALL, 5)
        self.levelPanel.SetSizer(self.scrollPnlSizer)
        
        self.mainSizer.Add(self.levelPanel,flag=wx.EXPAND)
        
        #add buttons for images
        self.contentSizer.Add(self.addButton(SpriteLib.Alien(1),"1"))
        self.contentSizer.Add(self.addButton(SpriteLib.Alien(2),"2"))
        self.contentSizer.Add(self.addButton(SpriteLib.Alien(3),"3"))
        self.contentSizer.Add(self.addButton(SpriteLib.Alien(4),"4"))
        self.contentSizer.Add(self.addButton(SpriteLib.Alien(5),"5"))
        self.contentSizer.Add(self.addButton(SpriteLib.EnviornmentComponent(1),"Env1"))
        
        b = wx.Button(self, 10, "Save Level", (20, 20))
        self.Bind(wx.EVT_BUTTON, self.OnSaveClick, b)
        b.SetDefault()
        b.SetSize(b.GetBestSize())
        self.contentSizer.Add(b)

        self.mainSizer.Add(self.contentSizer)
        
        self.SetSizer(self.mainSizer)
        
        self.levelPanel.SetupScrolling()
        
    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.levelPanel, 1, wx.EXPAND, 2)
        sizer_2.Add(self.imagePanel, 1, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.levelPanel.FitInside()
         
    def OnSaveClick(self,event):
        lvl = Level.Level()
        lvl.setLevelNumber(1)
        lvl.setLevelName("First Level")
        lvl.setLevelHeight(self.staticBitmap.GetSize()[1] * 2)
        
        for shape in self.staticBitmap.shapes:
            if shape.spriteType == 1:
                #enemy
                newEnemy = Level.Enemy()
                newEnemy.globalYPos = (self.staticBitmap.GetSize()[1] * 2) - (shape.pos[1] * 2)
                newEnemy.xPos = shape.pos[0] * 2
                newEnemy.type = shape.spriteSubType 
                lvl.addEnemy(newEnemy)
                
            elif shape.spriteType == 2:
                newEnv = Level.EnviornmentImage()
                newEnv.globalYPos = (self.staticBitmap.GetSize()[1] * 2) - (shape.pos[1] * 2)
                newEnv.xPos = shape.pos[0] * 2
                newEnv.type = shape.spriteSubType
                lvl.addImage(newEnv)
                
        lvl.writeLevelData()
        
    def onButton(self, event):
        button = event.GetEventObject()
        name = button.GetName()
        if name == "1":
            temp = SpriteLib.Alien(1)
            type = 1
            subType = 1
        elif name == "2":
            temp = SpriteLib.Alien(2)
            type = 1
            subType = 2
        elif name == "3":
            temp = SpriteLib.Alien(3)
            type = 1
            subType = 3
        elif name == "4":
            temp = SpriteLib.Alien(4)
            type = 1
            subType = 4
        elif name == "5":
            temp = SpriteLib.Alien(5)
            type = 1
            subType = 5
        elif name == "Env1":
            temp = SpriteLib.EnviornmentComponent(1)
            type = 2
            subType = 1
        self.staticBitmap.AddImage(temp,type,subType) 

    def convertImage(self,image):
        s = pygame.image.tostring(image, 'RGB')
        img = wx.ImageFromData(image.get_size()[0], image.get_size()[1], s)
        bmp = wx.BitmapFromImage(img)
        color = image.get_at((0,0))
        mask = wx.Mask(bmp, (color.r,color.g,color.b))
        bmp.SetMask(mask)
        return bmp   

    def addButton(self,spriteObj,btnName):
        bmp = self.convertImage(spriteObj.image)
        b = wx.BitmapButton(self, -1, bmp, (20, 20),
                           (bmp.GetWidth()+10, bmp.GetHeight()+10),
                           name=btnName)
        b.Bind(wx.EVT_BUTTON, self.onButton)
        return b
    
    
class MyApp(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, wx.ID_ANY, title='Exploder Explorer Level Editor')

        self.panel = LevelEditorWindow(self.frame, wx.ID_ANY)

        self.frame.Show()


if __name__ == '__main__':
   app = MyApp()
   app.MainLoop()


