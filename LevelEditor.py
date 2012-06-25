
import  wx
import  wx.lib.scrolledpanel as scrolled
import SpriteLib
from pygame.locals import *
import sys, pygame

#----------------------------------------------------------------------

class DragShape:
    def __init__(self, bmp):
        self.bmp = bmp
        self.pos = (0,0)
        self.shown = True
        self.text = None
        self.fullscreen = False

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

    def AddImage(self,imageType):
        if imageType == 2:
            temp = SpriteLib.Alien(Rect(0,0,0,0),2,(0,0))
            s = pygame.image.tostring(temp.image, 'RGB')
            img = wx.ImageFromData(temp.image.get_size()[0], temp.image.get_size()[1], s)
            img = img.Scale(temp.image.get_size()[0]/2,temp.image.get_size()[1]/2,wx.IMAGE_QUALITY_HIGH)
            bmp = wx.BitmapFromImage(img)
            shape = DragShape(bmp)
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
        self.contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #create panel for level data
        self.levelPanel = scrolled.ScrolledPanel(self, -1, size=(350,400),
                                 style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER, name="levelPanel" )
        
        self.staticBitmap = DragableCanvasBitmap(self.levelPanel)
        
        self.scrollPnlSizer.Add(self.staticBitmap, 0, wx.ALL, 5)
        self.levelPanel.SetSizer(self.scrollPnlSizer)
        
        self.mainSizer.Add(self.levelPanel,flag=wx.EXPAND)
        
        #add buttons for images
        temp = SpriteLib.Alien(Rect(0,0,0,0),2,(0,0))
        s = pygame.image.tostring(temp.image, 'RGB')
        img = wx.ImageFromData(temp.image.get_size()[0], temp.image.get_size()[1], s)
        bmp = wx.BitmapFromImage(img)
        
        #bmp = wx.Bitmap(temp.image)
        mask = wx.Mask(bmp, wx.WHITE)
        bmp.SetMask(mask)
        b = wx.BitmapButton(self, -1, bmp, (20, 20),
                           (bmp.GetWidth()+10, bmp.GetHeight()+10),
                           name="2")
        b.Bind(wx.EVT_BUTTON, self.onButton)
        
        self.contentSizer.Add(b)
        
        self.mainSizer.Add(self.contentSizer)
        
        self.SetSizer(self.mainSizer)
        #self.levelPanel.SetAutoLayout(1)
        #self.levelPanel.SetupScrolling()
        
        #self.imagePanel = wx.Panel(self, -1)
        
        #self.scrollPanelSizer = wx.BoxSizer(wx.VERTICAL) 
        #self.levelPanel.SetSizer(self.scrollPanelSizer) 
        
        self.levelPanel.SetupScrolling()
        #self.__do_layout()
  
       

        
        #self.Bind(wx.EVT_SIZE, self.OnSize)
    
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
         
    def onButton(self, event):
        button = event.GetEventObject()
        name = button.GetName()
        if name == "2":
            print "2 button pressed"
            self.staticBitmap.AddImage(2)
             
    #def OnSize(self, event):
        #print "onSize"
        #self.levelPanel.Height = event.GetSize()[0]
        #hsize = event.GetSize()[0] * 0.75
        #self.SetSizeHints(minW=-1, minH=hsize, maxH=hsize)
        #self.SetTitle(str(event.GetSize()))
        
    


class MyApp(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, wx.ID_ANY, title='Exploder Explorer Level Editor')

        self.panel = LevelEditorWindow(self.frame, wx.ID_ANY)

        self.frame.Show()


if __name__ == '__main__':
   app = MyApp()
   app.MainLoop()


