import zobj
import zwall
import zutils
import TermEmulator

import os
import pty
import fcntl
import termios
import select
import struct
import threading


strokes = {zutils.KEY_VT:		"?",
	   zutils.KEY_HT:		"\t",
	   zutils.KEY_SHT:		"\033[Z",
	   zutils.KEY_LEFT:		"\033[D",
	   zutils.KEY_CLEFT:		"\033[1;5D",
	   zutils.KEY_RIGHT:		"\033[C",
	   zutils.KEY_CRIGHT:		"\033[1;5C",
	   zutils.KEY_UP:		"\033[A",
	   zutils.KEY_CUP:		"\033|1;5A",
	   zutils.KEY_CSUP:		"?",
	   zutils.KEY_DOWN:		"\033[B",
	   zutils.KEY_CDOWN:		"\033[1;5B",
	   zutils.KEY_CSDOWN:		"?",
	   zutils.KEY_DEL:		"\033[3~",
	   zutils.KEY_SDEL:		"\033[3;2~",
	   zutils.KEY_CDEL:		"\033[3;5~",
	   zutils.KEY_HOME:		"\033[H",
	   zutils.KEY_SHOME:		"?",
	   zutils.KEY_CHOME:		"\033[1;5H",
	   zutils.KEY_END:		"\033[F",
	   zutils.KEY_SEND:		"?",
	   zutils.KEY_CEND:		"\033[1;5F",
	   zutils.KEY_BACKSPACE:	 "\b",
	   zutils.KEY_RETURN:		"\n",
	   zutils.KEY_SRETURN:		"\033[OM",
	   zutils.KEY_PAGEDOWN:		"\033[6~",
	   zutils.KEY_PAGEUP:		"\033[5~",
	   zutils.KEY_CPAGEDOWN:	"\033[5;5~",
	   zutils.KEY_CPAGEUP:		"\033[6;5~",
	   zutils.KEY_CW:		chr(23),
	   zutils.KEY_CD:		chr(4),
	   zutils.KEY_CN:		chr(14),
	   zutils.KEY_CX:		chr(24),
	   zutils.KEY_CV:		chr(22),
	   zutils.KEY_CA:		chr(1),
	   zutils.KEY_CF:		chr(6),
	   zutils.KEY_ESC:		"\033",
	   zutils.KEY_SPACE:		" "
}


class zconsole(zobj.zobj):
	def __init__(self, parent, pos=(0,0), size=(0,0), cmd = '', folder = '', title = ''):
		super().__init__(parent, pos, size)
		self._cmd = cmd
		self._folder = folder
		self._title = title
		#self._fcolor = zutils.CL_FG
		#self._bcolor = zutils.CL_BG
		#self._attr = 0
		
		self.linesScrolledUp = 0
		self.scrolledUpLinesLen = 0
		
		self.termEmulator = TermEmulator.V102Terminal(size[1], size[0])
		self.termEmulator.SetCallback(self.termEmulator.CALLBACK_SCROLL_UP_SCREEN,    self.OnTermEmulatorScrollUpScreen)
		self.termEmulator.SetCallback(self.termEmulator.CALLBACK_UPDATE_LINES,        self.OnTermEmulatorUpdateLines)
		self.termEmulator.SetCallback(self.termEmulator.CALLBACK_UPDATE_CURSOR_POS,   self.OnTermEmulatorUpdateCursorPos)
		self.termEmulator.SetCallback(self.termEmulator.CALLBACK_UPDATE_WINDOW_TITLE, self.OnTermEmulatorUpdateWindowTitle)
		self.termEmulator.SetCallback(self.termEmulator.CALLBACK_UNHANDLED_ESC_SEQ,   self.OnTermEmulatorUnhandledEscSeq)
		
		self.isRunning = False
		
		self.resize(size)
	
	def get_title(self):
		return self._title
	
	def set_title(self, title):
		self._title = title
	
	def resize(self, size):		
		self.termEmulator.Resize(size[1], size[0])
		
		if self.isRunning:
			fcntl.ioctl(self.processIO, termios.TIOCSWINSZ,
			struct.pack("hhhh", size[1], size[0], 0, 0))
		
		self.dwall = zwall.zwall(size[0], size[1])

	def run(self):
		if self.isRunning:
			return
		
		path = self._cmd.split(' ')[0]
		basename = os.path.basename(path)
		arglist = [ basename ]
		
		arguments =self._cmd.split(' ')[1:]
		for arg in arguments:
			arglist.append(arg)
		
		
		rows, cols = self.termEmulator.GetSize()
		if rows != self.get_size()[1] or cols != self.get_size()[0]:
			self.termEmulator.Resize (self.get_size()[1], self.get_size()[0])
		
		processPid, processIO = pty.fork()
		if processPid == 0: # child process
			os.execl(path, *arglist)
		
		zutils.debug("Child process pid: " +str(processPid))
		
		# Sets raw mode
		#tty.setraw(processIO)
		
		# Sets the terminal window size
		fcntl.ioctl(processIO, termios.TIOCSWINSZ, struct.pack("hhhh", self.get_size()[1], self.get_size()[0], 0, 0))
		
		tcattrib = termios.tcgetattr(processIO)
		tcattrib[3] = tcattrib[3] & ~termios.ICANON
		termios.tcsetattr(processIO, termios.TCSAFLUSH, tcattrib)
			
		self.processPid = processPid
		self.processIO = processIO
		#self.processOutputNotifierThread = threading.Thread(target = self.__ProcessOuputNotifierRun)
		#self.waitingForOutput = True
		#self.stopOutputNotifier = False
		#self.processOutputNotifierThread.start()
		self.isRunning = True
	
	def process_is_alive(self):
		if not self.isRunning:
			return False
		try:
			pid, status = os.waitpid(self.processPid, os.WNOHANG)
			if pid == self.processPid and os.WIFEXITED(status):
				return False
		except:
			return False
		
		return True
	
	def check_for_output(self):
		zutils.debug("Checking...")
		if not self.isRunning:
			return
		inpSet = [ self.processIO ]
		
		inpReady, outReady, errReady = select.select(inpSet, [], [], 0)
		if self.processIO in inpReady:
			self.read_process_output()
		
		if not self.process_is_alive():
			zutils.debug("Process died :(")
			self.isRunning = False
			self.read_process_output()
		
        
	def update_cursor_pos(self):
		row, col = self.termEmulator.GetCursorPos()
		
		self._caret = (col, row)
		#self.txtCtrlTerminal.SetInsertionPoint(insertionPoint)
		
	def update_wall(self):
		# let's write to dwall!
		
		lines = self.termEmulator.GetLines()
		
		for y in range(self.get_size()[1]):
			
			line = lines[y]
			#zutils.debug("Ui: "+str(line))
			for x in range(self.get_size()[0]):
				attr = self.termEmulator.GetRendition(y, x)
				self.dwall.get_wall()[y][x].c = chr(line[x])
				#self.dwall.get_wall()[y][x].c = line[x]
	
	def OnTermEmulatorScrollUpScreen(self):
		self.dwall.scroll_up()
		self.linesScrolledUp += 1
        
	def OnTermEmulatorUpdateLines(self):
		self.update_wall()	
	
        
	def OnTermEmulatorUpdateCursorPos(self):
		self.update_cursor_pos()
        
	def OnTermEmulatorUpdateWindowTitle(self, title):
		self.set_title(title)
        
	def OnTermEmulatorUnhandledEscSeq(self, escSeq):
		zutils.debug("Unhandled escape sequence: [" + escSeq)
        
	def read_process_output(self):
		output = ""
		
		try:
			while True:
				data = os.read(self.processIO, 512)
				datalen = len(data)
				output += data.decode("UTF-8")
				
				if datalen < 512:
					break
		except:
			output = ""
		
		zutils.debug("Total: "+str(output))
		self.termEmulator.ProcessInput(output)
		
		self.waitingForOutput = True
	
	def on_key(self, key, char):
		super().on_key(key, char)
		
		keystrokes = ""

		if key in strokes:
			keystrokes = strokes[key]
		else:
			keystrokes = char
		
		os.write(self.processIO, keystrokes.encode("UTF-8"))
	
	
	def do_paint(self, wall):
		self.check_for_output()
		self.insert_wall(wall, self.dwall)
	
	

	
	