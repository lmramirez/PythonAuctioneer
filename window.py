import curses, sys

class screen:
	scrn = None
	row = None
	col = None

class Window:
	""" objects of Window class have: window, text[], string, nlines, ncols """
        def __init__(self, string):
		self.printedlines = 1
                self.nlines = 25
                self.ncols = 80
		self.text = []
		if string == "top":
			self.makeTop()
		elif string == "bottom":
			self.makeBottom()
		elif string == "border":
			self.makeBorder()
		elif string == "border2":
			self.makeBorder2()
		elif string == "menu":
			self.makeMenu()
		elif string == "menu2":
			self.makeMenu2()
		else:
			print "weird"

	def makeMenu(self):
		self.window = curses.newwin(20, 20, 26, 1)
		self.window.addstr("Enter 1 to bid:\n")
		self.window.addstr("Enter 2 to exit:\n")
		self.window.refresh()
		return self
	
	def makeMenu2(self):	
		self.window=curses.newwin(20, 20, 26, 1)
		self.window.addstr("1: Make Announcement")
                self.window.addstr("2: New Item\n")
                self.window.addstr("3: End Item\n")
                self.window.addstr("4: Close Auction\n")
		self.window.refresh()
		return self

	def makeTop(self):
		self.nlines=self.nlines-2
		self.ncols=self.ncols-2
		self.window = curses.newwin(self.nlines, self.ncols,1,1)
                self.window.scrollok(True)
		#self.window.refresh()
		self.window.immedok(True)
		return self

        def makeBottom(self):
		self.nlines=self.nlines-2
		self.ncols=self.ncols-28
                self.window = curses.newwin(self.nlines, self.ncols, 26, 23)
		self.window.scrollok(True)
		self.window.immedok(True)
                return self

	def makeBorder(self):
		self.window = curses.newwin(self.nlines, self.ncols, 0, 0)
		self.window.border()
		self.window.refresh()
		return self
		
	def makeBorder2(self):
                self.window = curses.newwin(self.nlines, self.ncols, 25, 0)
                self.window.border()
                self.window.refresh()
                return self


	def fileno(self):
		return 1



