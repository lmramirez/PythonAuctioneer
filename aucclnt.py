import sys, socket, select, curses
from window import *



def main():
	screen.scrn = curses.initscr()
        curses.cbreak()

        border = Window("border")
        border2 = Window("border2")
        top=Window("top")
        menu = Window("menu")
        bottom = Window("bottom")

        bottom.window.move(0,0)
        bottom.window.refresh()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	host = sys.argv[1]
	port = int(sys.argv[2])
	


	bottom.window.addstr('Enter your email address to connect to the server: ')
	bottom.window.addstr('\n')
	email = bottom.window.getstr()
	bottom.window.addstr('\n')
	sock.connect((host, port))
	bottom.window.addstr('socket.connect')
	sock.send(email)
	curses.noecho()


	rlist = [sock, bottom]
	inString = []


	bottom.window.clear()
        y_pos, x_pos = bottom.window.getyx()
        #x_pos += 20
        #bottom.window.move(y_pos, x_pos)
	bottom.window.refresh()

	running = True	
	while running:
		inputs, outputs, excepts = select.select(rlist, [], [])

		for s in inputs:
			if s==bottom:
                		bottom.window.nodelay(1)
                		char = bottom.window.getch() #fix this later if needed
                		if char != -1:
                		        if char == 10:
						inStr = ''.join(chr(i) for i in inString)
						inStr=inStr.split(' ')
						if inStr[0]=='2':
							running = False
						if inStr[0]=='1':#it's a bid
							inStr = inStr[1:]
					
							if len(inStr)==2:
								inStr = ' '.join(inStr)
								sock.send(inStr) 
								bottom.window.addstr('\n')
								bottom.window.clear()
							else:
								top.window.addstr('Incorrect bid. Should be: 1 item_number bid_amount\n')
								bottom.window.clear()
						x_pos = 0;
						bottom.window.move(0,0)
						bottom.window.refresh()
						inString = []
                        		elif char == 127:
						if inString:
							x_pos -= 1
							bottom.window.delch(y_pos, x_pos)
							bottom.window.move(y_pos, x_pos)
							del inString[-1]
					else:
						bottom.window.addch(y_pos, x_pos, char)
						x_pos += 1
						bottom.window.move(y_pos, x_pos)
						inString.append(char)
				
			elif s==sock:
				data = sock.recv(1024)
				if data:
					top.window.addstr(data)
					top.window.refresh()

	
	sock.close()

	return





if __name__=='__main__':
	main()
