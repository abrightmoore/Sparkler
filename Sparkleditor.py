# @TheWorldFoundry

import sys
from math import floor
import copy
from random import randint,random
import pygame
from pygame.locals import *
import time

pygame.init()

class Touch:
	def __init__(self,pos,age,vx,vy,colour):
		self.colour = colour
		self.pos = pos
		self.age = float(age)
		self.alive = True
		self.vectorx = vx
		self.vectory = vy
		colRange = randint(100,255)
		# self.colour = (colRange,colRange,255,255)
		
	def update(self):
		self.age -= 0.1
		if self.age < 1:
			self.alive = False
		else:
			x,y = self.pos
			x += self.vectorx
			y += self.vectory
			self.pos = x,y
		
		
			
	def draw(self,surface):
		x,y = self.pos
		delta = int(self.age)
		if self.alive:
			pygame.draw.circle(surface, self.colour.getCol(),(int(x),int(y)),delta)
			
			#pygame.draw.lines(surface, (0,0,0,0), False, [(x,y-20),(x,y+20)], 1)

class Colour:
	paletteFlame = [
		#(255,255,255),
		(100,100,255),
		(62,18,5), # Brown
		(230,34,12),
		(247,177,56),
		(238,255,137),
		(238,255,137),
		(241,255,213),
		(100,100,255),
		(255,255,255)

	]
	paletteDistance = 255# Number of colour gradients in each section of the palette
	
	def __init__(self,palette):
		self.gradient = 0.5+random()/2
		self.age = 0.5+random()/2
		self.palette = palette

	def clipBounds(self,val,min,max):
		if val < min:
			val = min
		if val > max:
			val = max
		return val
			
	def update(self):
		if self.age > 0:
			self.age -= 0.03*random()
		else:
			self.age = 0

	def getCol(self):
		paletteLen = self.paletteDistance*(len(self.palette)-1)
		colPos = self.age*paletteLen
		# if random() < 0.1: print colPos
		baseColIdx = int(floor(colPos/self.paletteDistance))
		baseCol = self.palette[baseColIdx]
		nextCol = self.palette[(baseColIdx+1)%len(self.palette)] # To Do: check bounds?
		percentDist = (colPos - self.paletteDistance*baseColIdx)/self.paletteDistance
		R1,G1,B1 = baseCol
		R2,G2,B2 = nextCol
		R = R1+(R2-R1)*percentDist
		G = G1+(G2-G1)*percentDist
		B = B1+(B2-B1)*percentDist
		self.update()
		return (self.clipBounds(int(R),0,255),self.clipBounds(int(G),0,255),self.clipBounds(int(B),0,255),255)

	def render(self,surface):
		height = 32
		width = surface.get_width()
		paletteLen = self.paletteDistance*(len(self.palette)-1)
		for i in xrange(0,width):
			colPos = float(float(i)/float(width)*(float(paletteLen)))
			baseColIdx = int(colPos/self.paletteDistance)
			print "BCI",baseColIdx
			baseCol = self.palette[baseColIdx]
			nextCol = self.palette[(baseColIdx+1)%len(self.palette)] # To Do: check bounds?
			percentDist = (float(colPos - self.paletteDistance*baseColIdx))/self.paletteDistance
			if random() < 0.1: print percentDist
			R1,G1,B1 = baseCol
			R2,G2,B2 = nextCol
			R = R1+(R2-R1)*percentDist
			G = G1+(G2-G1)*percentDist
			B = B1+(B2-B1)*percentDist			
			pygame.draw.lines(surface, (self.clipBounds(int(R),0,255),self.clipBounds(int(G),0,255),self.clipBounds(int(B),0,255),255), False, [(i,0),(i,height)], 1)


class Game:
	def __init__(self,size,label,FPS):
		self.size = size
		self.label = label
		self.FPS = FPS
		self.FTICKS = int(100/FPS)

	def setupScreen(self):		
		print "Creating Surface and Window"
		surface = pygame.display.set_mode(self.size,SRCALPHA)
		print "Converting the surface to optimise rendering"
		surface.convert()
		print "Changing the caption"
		pygame.display.set_caption(self.label)
		fpsClock = pygame.time.Clock()
		fpsClock.tick(self.FPS)
		return surface

	def addSparkle(self,objects,pos):
		x,y = pos
		sz = 20
		objects.append(Touch(pos,randint(5,sz>>1),0,randint(0,6)*0.13,Colour(Colour.paletteFlame)))
		for i in xrange(0,randint(1,23)):
				deltax = randint(-sz,sz)
				deltay = randint(-sz,sz)
				objects.append(Touch((x+deltax,y+deltay),randint(2,5),randint(-3,3)*0.5,randint(0,2)*0.5,Colour(Colour.paletteFlame)))	
		return objects

	def gameLoop(self):
		WIDTH,HEIGHT = self.size
		cx = WIDTH>>1
		cy = HEIGHT>>1
		
		objects = []
		
		# Setup objects
		
		surface = self.setupScreen()    
		iterationCount = 0
		keepGoing = True
		
		current_milli_time = pygame.time.get_ticks() #int(round(time.time() * 1000)) # Seed time tracker

		mousePath = []
		MOUSEPATHLIMIT = 1000
		OBJECTLIMIT = 10000
                ONSCREEN = False
                DRAW = False
		
		#COL = Colour()

		#staleObjects = []
		while keepGoing:
			iterationCount += 1
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					keepGoing = False
				elif event.type == MOUSEBUTTONUP:
					if event.button == 3: # 3 == Left
						mousePath = []
					elif event.button == 1: # 1 == Right
						if DRAW == False:
                                                        DRAW = True
                                                        print "Drawing enabled"
                                                elif DRAW == True:
                                                        DRAW = False

				elif event.type == MOUSEMOTION and ONSCREEN == True and DRAW == True:
					if random() <= 0.8:
						objects = self.addSparkle(objects,event.pos)
						if random() > 0.01 and len(mousePath) < MOUSEPATHLIMIT:
                                                        mousePath.append(event.pos)
                                elif event.type == ACTIVEEVENT:
                                        ONSCREEN = event.gain 
				else:
					print event

			surface.fill((0,40,60))
			newObjects = [] # This is a swap buffer
			for o in objects:
				o.update()
				if o.alive == True:
					o.draw(surface)
					newObjects.append(o)
			#COL.render(surface)					
			pygame.display.update()
			
			objects = newObjects
			# o.append(staleObjects[randint(0,len(staleObjects)-1)])
			
			current_milli_time2 = pygame.time.get_ticks() #int(round(time.time() * 1000))
			timeDelta = current_milli_time2-current_milli_time
			#print timeDelta
			if timeDelta > 1000:
                                print "System is running at or below 1FPS."
                                print "Dumping history!"
                                mousePath = []
 
			elif timeDelta < self.FTICKS:
				pygame.time.wait(self.FTICKS-timeDelta)

                        if len(mousePath) >= MOUSEPATHLIMIT:
                                for i in xrange(0,100):
                                        mousePath.pop() # discard
                                print "MousePath limit reached"

                        for i in xrange(0,randint(1,10)):
                                if random() < 0.9 and len(mousePath) > 100:
                                         if len(objects) < OBJECTLIMIT:
                                                 objects = self.addSparkle(objects,mousePath[randint(0,len(mousePath)-1)])			
			current_milli_time = current_milli_time2

		print "Shutting down."
		pygame.quit()
		sys.exit()	

g = Game((1000,700),"Game Name",10)
g.gameLoop()

