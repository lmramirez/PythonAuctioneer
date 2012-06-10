import socket, sys, select, curses, subprocess
from window import *

'''
change the client class so that when a user connects to bidding, it checks their
email address against the list of emails, if found in the list, it should add their
information to the dictionary if not send the client an error message
'''

class Client:
	clientTable = {}
	
	def __init__(self, e, con, ip):
		self.email = e	
		self.conn = con
		self.IP = ip
		self.newClient(ip)
		self.itemList = [] #list of items each client has won
	def newClient(self, ip):
		if not ip in Client.clientTable:
			Client.clientTable[ip] = self		
	def sendToClient(self, string):
		allC = [Client.clientTable[x].conn for x in Client.clientTable]
		for i in allC:
 			i.send(string)
	def addItem(self, item):
		self.itemList.append(item)

class Auctioneer:
        def __init__(self, top, bottom):
		self.top = top
		self.bottom = bottom
	def readInput(self, inputList):
		istr = ''.join(chr(i) for i in inputList)
		char, junk, dataString = istr.partition(' ')
		char = istr[0]
		
		if(char == '1'):
			self.postAnnouncement(dataString)	
		elif(char == '2'):
			self.beginItem(dataString)
		elif(char == '3'):
			self.endItem()
		elif(char=='4'):
			return self.endAuction()
		else:
			pass
		return True
	def beginItem(self, string):
		Item.biddingOpen = True
		self.postAnnouncement(string)#prints string to clients and auctioneer
		item=Item(string)
		self.top.window.addstr('Item Number is: ')
	        self.top.window.addstr(item.getItemNum()) 
		self.top.window.addstr('\n') 
		self.top.window.addstr('The bidding is now open.')
		self.top.window.addstr('\n')
		allC = [Client.clientTable[x].conn for x in Client.clientTable]
                for i in allC:	 
			i.send('Item Number is: ')
			i.send(item.getItemNum())
			i.send('\n')
			i.send('The bidding is open.')
			i.send('\n')
                return
        def endItem(self):
                #end bidding for a single item
		Item.biddingOpen = False
		if Item.currentItem.winner == None:
			self.postAnnouncement('The bidding is now closed for this item. No winner.\n')
		else:
			string = 'The bidding for this item is now closed. The winner is: '
			string += Client.clientTable[Item.currentItem.winner].email + '\n'
			self.postAnnouncement(string)	
		Item.allItems[Item.currentItem.num-1] = Item.currentItem
	
                return
        def endAuction(self):
		#update client table with items won
		#close all connections
		if Item.biddingOpen:
			self.top.window.addstr('error: trying to close auction before closing bidding\n')
			return True
		for item in Item.allItems:
			if item.winner != None:
				Client.clientTable[item.winner].itemList.append(item)
		self.emailClients()
                return False
        def postAnnouncement(self, string):
                	self.top.window.addstr(string)
                	self.top.window.addstr('\n')
                	#differentiates start bid (1) and comments (2)
                	allC = [Client.clientTable[x].conn for x in Client.clientTable]
                	for i in allC:
                	        i.send(string)
                	        i.send('\n')
		
        def emailClients(self):
                #this method will go through the dictionary of clients, generate
                #their itemized list of purchased items and send them an
                #email containing this information
		for client in Client.clientTable:

			message = ""
			subject = "Your\ Auction\ Results! "
			total = 0
			if len(Client.clientTable[client].itemList) > 0:

				message += "Congratulations! '\n' '\n' You have won the following items: '\n'"
				for item in Client.clientTable[client].itemList:
					message += "\ \  Item Description: " + item.description + "'\n'"
					message += "\ \  Final Price: \$" + item.highBid + "'\n'"
					total += int(item.highBid)		
					message += "'\n'"
				message += "___________________________'\n'"	
				message += "Grand Total:    \$" + str(total) 
				cmd = "echo " + message + " | mailx -s " + subject + Client.clientTable[client].email
				p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
				output, errors = p.communicate()
                return

                


class Item:
	'''
	holds all items that are being auctioned 
	and keeps track of the data for each one
	'''

	allItems = [] #dictionary {itemNum: Items}
	itemNum = 0;
	currentItem = None
	biddingOpen = False
	def __init__(self, description):
		self.description = description
		Item.itemNum += 1
		self.num = Item.itemNum
		self.winner = None
		self.highBid = 0
		Item.currentItem = self
		Item.allItems.append(self)
		#allItems[itemNum]=self
	def getItemNum(self):
		return str(self.num)



def acceptClient(sock, ins, rlist, elist):
	'''
	accept the socket connection for the client
	'''

	clnt, addr = sock.accept()
	rlist.append(clnt)
	#when connecting, client will send a message containg an email address
	#read it in here and check it with elist andcreate an email-IP mapping
	email = clnt.recv(1024)
	if email in elist:
		Client(email, clnt, addr[0])
	else:
		clnt.send('Email not registered, please type ^c to restart and try again.\n')
		


def clientInput(data, ip, auctioneer):
	'''
	Takes the data given by the user and parses is to
	process the bid.
	'''

	itemNum, junk, bidAmnt = data.partition(' ')
	try: bidAMnt = int(bidAmnt)
	except: Client.clientTable[ip].conn.send('Your bid has been rejected because your bidAmnt is not an integer.\n')
	itemNum = int(itemNum)
	if itemNum != Item.currentItem.num:
		#error wrong item
		Client.clientTable[ip].conn.send('Your bid has been rejected due to incorrect item number.\n')
	elif not Item.biddingOpen:
		Client.clientTable[ip].conn.send('Your bid has been rejected, because bidding is currently closed\n')
	elif ip == Item.currentItem.winner:
		Client.clientTable[ip].conn.send('Your bid has been rejected because you are currently the highest bidder.\n')
	else:	#accept bid
		if int(bidAmnt) > int(Item.currentItem.highBid):
			#accept bid
			Item.currentItem.highBid = bidAmnt
			Item.currentItem.winner = ip

			string = 'New bid by ' + Client.clientTable[ip].email + ': ' + bidAmnt
	
                        auctioneer.top.window.addstr(string)
                        auctioneer.top.window.addstr('\n')
                        #differentiates start bid (1) and comments (2)
                        allC = [Client.clientTable[x].conn for x in Client.clientTable]
                        for i in allC:
                                i.send(string)
                                i.send('\n')
				
		else: 		#error, another higher bid has already been placed
			Client.clientTable[ip].conn.send('Your bid has been rejected due to a higher bid already placed.\n')	
	return


def main():
	'''create windows '''
        screen.scrn = curses.initscr()
        curses.noecho()
        curses.cbreak()
        border = Window("border")
        border2 = Window("border2")        
	top=Window("top")
        menu2 = Window("menu2")
        bottom = Window("bottom")
	bottom.window.move(0,0)
	'''end create windows'''

	#set up listening socket
	lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = int(sys.argv[2])	
	dataSize = 1024 

	# opens the port for receiving messages through it for the server
	lsock.bind(('', port))

	#open and process email file
	emails = open(sys.argv[1], 'r')
	elist = emails.readlines()
	elist = [x.rstrip('\n') for x in elist]
	
	lsock.listen(5)

	rlist = [lsock, bottom] #list of interfaces to read from
	inString = []

	
	y_pos, x_pos = bottom.window.getyx()
	bottom.window.move(y_pos, x_pos)
	bottom.window.refresh()
	
	auctioneer = Auctioneer(top, bottom)
	running = True
	while running:
		inputs, outputs, excepts = select.select(rlist, [], [])	

		for s in inputs:
			if s==lsock: 
				acceptClient(lsock, inputs, rlist, elist)
			elif s==bottom: #try to et input from bottom window 
				bottom.window.nodelay(1)
				char = bottom.window.getch(y_pos, x_pos)
				if char != -1:
					if char == 10: #enter key pressed
						running = auctioneer.readInput(inString)
						bottom.window.addstr('\n')
						bottom.window.clear()
						x_pos = 0
						bottom.window.move(0, 0)
						bottom.window.refresh()
						inString = []
					elif char == 127: #backspace key pressed
						if len(inString):
							x_pos -= 1
							bottom.window.delch(y_pos, x_pos)
							bottom.window.move(y_pos, x_pos)
							bottom.window.refresh()
							del inString[-1]
					else:
						bottom.window.addch(y_pos, x_pos, char)
						bottom.window.refresh()
						x_pos += 1
						bottom.window.move(y_pos, x_pos)
						inString.append(char)	
			else:
				data = s.recv(dataSize)
				if data:
					ip, port = s.getpeername()
					clientInput(data, ip, auctioneer)
				else:
					s.close()
					rlist.remove(s)



	lsock.close()

	return




if __name__=='__main__':
	main()
