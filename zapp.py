import zobj
import zwall
import zframe

import curses
#import curses.wrapper
import curses.ascii
import locale
import time

import zutils

class zapp:
	def __init__(self):
		self._width = 0
		self._height = 0
		self._wall = None
		self._old_wall = None
		self._root_frame = None
		self._scr = None
		self.cp = 0
		self.color_pairs = {}
		self.color_pairs[(-1, -1)] = 0
		self._render = 0
	
	def unget_char(self, ch):
		curses.ungetch(ch)
	
	def _get_char(self): 
		def get_check_next_byte(): 
			c = self._scr.getch() 
			if 128 <= c <= 191: 
				return c 
			else: 
				raise UnicodeError 

		bytes = []
		c = self._scr.getch()
		if c >= 0 and c <= 127: 
			# 1 bytes 
			bytes.append(c)
		elif 194 <= c <= 223: 
			# 2 bytes 
			bytes.append(c) 
			bytes.append(get_check_next_byte()) 
		elif 224 <= c <= 239: 
			# 3 bytes 
			bytes.append(c) 
			bytes.append(get_check_next_byte()) 
			bytes.append(get_check_next_byte()) 
		elif 240 <= c <= 244: 
			# 4 bytes 
			bytes.append(c) 
			bytes.append(get_check_next_byte()) 
			bytes.append(get_check_next_byte()) 
			bytes.append(get_check_next_byte())
			
		buf = bytearray(bytes).decode('utf-8')
		return c, buf
	
	def do_run(self):
		
		return
			
	
	def _do_run(self, stdscr):

		self._scr = stdscr
		locale.setlocale(locale.LC_ALL, '')
		self._code = locale.getpreferredencoding()
		self._height,self._width=stdscr.getmaxyx()
		curses.start_color()
		#curses.use_default_colors()
		
		
		self._wall = zwall.zwall(self._width, self._height)
		self._old_wall = zwall.zwall(self._width, self._height)
		self._root_frame = zframe.zframe(None, (0,0), (self._width,self._height))
		
		self.do_run()
		
		
		
		
	def render(self, do_clear = True):
		self._render += 1
		if do_clear:
			self._wall.clear()
		else:
			self._wall.copy_from(self._old_wall)
		
		
		self._root_frame.paint(self._wall)
		
		w1 = self._wall.get_wall()
		w2 = self._old_wall.get_wall()
		for y in range(self._height):
			for x in range(self._width):
				if y == self._height-1 and x == self._width-1:
					continue
				brick = w1[y][x]
				old_brick = w2[y][x]
				
				if(brick != old_brick):
					#look up color
					if not (brick.fcolor, brick.bcolor) in self.color_pairs:
						self.cp += 1
						zutils.debug("Could not find color! init "+str(brick.fcolor) +":"+str( brick.bcolor ))
						zutils.debug(str(x)+","+str(y)+","+brick.c)
						curses.init_pair(self.cp, brick.fcolor, brick.bcolor)
						self.color_pairs[(brick.fcolor, brick.bcolor)] = self.cp
						zutils.debug("Could not find color! next i "+str(self.cp+1) +":"+str( self.color_pairs[(brick.fcolor, brick.bcolor)]) )
						
					attr = curses.color_pair(self.color_pairs[(brick.fcolor, brick.bcolor)]) | brick.attr
					#attr = brick.attr
					self._scr.addstr(y,x, brick.c, attr)
					#self._scr.addstr(y,x, str(self._render % 10)[0], attr)
					
		sel = self._root_frame.get_focused()
		if(sel != None):
			pos = (sel.get_global_pos()[0] + sel.get_caret()[0], sel.get_global_pos()[1] + sel.get_caret()[1])
			self._scr.move( pos[1], pos[0] )
		
		
		tmp = self._old_wall
		self._old_wall = self._wall
		self._wall = tmp
		
		
		
	
	def run(self):
		curses.wrapper(self._do_run)
	def get_root(self):
		return self._root_frame
	
	
