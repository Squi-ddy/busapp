import threading, time
from tkinter import *
from functools import partial


class loading(object):

	def __init__(self, root, canvas, dotsize):
		self.root = root
		self.canvas = canvas
		self.stopThreads = False
		self.dot = dotsize
		self.root.update()
		self.w = self.canvas.winfo_width()
		self.h = self.canvas.winfo_height()

	def drawAtX(self, x, tg):
		dotsize = self.dot
		self.canvas.create_oval(x-dotsize, self.h/2-dotsize, x+dotsize, self.h/2+dotsize, fill = "black", tags = tg)

	def startThread(self):
		dFast = (3/7)*self.w
		dSlow = (1/7)*self.w
		slowV = dSlow / 100 #in px/10ms
		fastV = 2 * dFast / 50 - slowV #in px/10ms
		fastA = (slowV-fastV)/50 #in px/10ms^2
		dots = []
		tick = 0

		while True:
			self.drawDots(tick, dots, fastA, fastV, slowV)
			time.sleep(0.01) #a tick every 10ms
			if self.stopThreads:
				self.canvas.delete(ALL) 
				break
			tick += 1

	def drawDots(self, tick, dots, accel, velocity, slowV):
		#render cycle
		remove = False
		for pva in dots:
			pva[1] += pva[2]
			pva[0] += pva[1]
			if pva[0] >= self.w:
				remove = True
				continue
			elif pva[0] >= (4/7)*self.w:
				pva[2] = -accel
			elif pva[1] <= slowV:
				pva[2] = 0
				pva[1] = slowV
			self.drawAtX(pva[0], "x"+str(tick%2))
		self.canvas.delete("x"+str((tick-1)%2))
		if remove:
			dots.pop(0)
		if tick % 300 in [0,15,45,30]:
			dots.append([0, velocity, accel]) #pos, vel, accel
			self.drawAtX(0, "x"+str(tick%2))



	def start(self):
		self.stopThreads = False
		self.currentThread = threading.Thread(target = self.startThread)
		self.currentThread.daemon = True
		self.currentThread.start()

	def stop(self):
		self.stopThreads = True

if __name__ == '__main__':
	class App(object):

		def __init__(self):
			self.root = Tk()
			self.root.title = 'Loadingbar Example'
			loadcanvas = Canvas(self.root, width = 700, height = 50, bg = '#FFFFFF')
			loadcanvas.pack()
			x = loading(self.root, loadcanvas, 3)
			x.start()
			self.root.mainloop()

	app = App()