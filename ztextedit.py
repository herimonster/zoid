import zobj
import zwall
import zutils

import zregexhighlighter


class ztextedit(zobj.zobj):
	
	def __init__(self, parent, pos=(0,0), size=(0,0), text="", readonly=False):
		super().__init__(parent, pos, size)
		self._line = 0
		self._column = 0
		self._xborder = 4
		self._yborder = 0
		self._tabwidth = 4
		self.set_text(text)
		self.readonly = readonly
		self._autoindent = True
		self.highlighter = zregexhighlighter.zregexhighlighter()
		self.on_change = None
		self.on_cursor_change = None
		
		
	
	def set_text(self, text):
		self._lines = [x.replace("\r", "").replace("\n","") for x in text.split("\n")]
		

		if len(self._lines) == 0:
			self._lines=[""]
		self._selx = 0
		self._sely = 0
		self._cx = 0
		self._cy = 0
		self._changed = False
		self._lines_changed = [False for i in range(len(self._lines))]
	
	def get_text(self):
		str = ""
		for x in self._lines:
			str += x + "\n"
		return str
	
	def get_cursor(self):
		return self._cx, self._cy
	
	def get_sel(self):
		return self._selx, self._sely
	
	def get_cursor_limits(self):
		return len(self._lines[self._cy]), len(self._lines)
	
	def get_changed(self):
		return self._changed
	
	def set_cursor(self, cx, cy, keep_sel = False):
		self._cy = cy
		if self._cy < 0:
			self._cy = 0
		elif self._cy >= len(self._lines):
			self._cy = len(self._lines)-1
		
		self._cx = cx
		if(self._cx < 0):
			self._cx = 0
		elif(self._cx > len(self._lines[self._cy])):
			self._cx = len(self._lines[self._cy])
		
		if not keep_sel:
			self._selx = self._cx
			self._sely = self._cy
		self._cursor_change()
		
	def set_sel(self, selx, sely):
		self._sely = sely
		if self._sely < 0:
			self._sely = 0
		elif self._sely >= len(self._lines):
			self._sely = len(self._lines)-1
		
		self._selx = selx
		if(self._selx < 0):
			self._selx = 0
		elif(self._selx > len(self._lines[self._sely])):
			self._selx = len(self._lines[self._sely])
		
	def _cursor_change(self):
		if self.on_cursor_change != None:
			self.on_cursor_change(self)
			
	def _set_changed(self):
		self._changed = True
		self._lines_changed[self._cy] = True
		if self.on_change != None:
			self.on_change(self)
			
	def _set_unchanged(self):
		self._changed = False
		for i in range(len(self._lines)):
			self._lines_changed[i] = False
		
	
	def writechar(self, ch):
		if self.readonly:
			return
		
		self._set_changed()
		
		if self._cx > len(self._lines[self._cy]):
			self._cx = len(self._lines[self._cy])
		
		#TODO: Overwrite selected text!
		if ch != "\n":
			if self._cx > len(self._lines[self._cy]):
				self._cx = len(self._lines[self._cy])
				
			self._lines[self._cy] = self._lines[self._cy][:self._cx] + ch + self._lines[self._cy][self._cx:]
			self._cx += len(ch)
		else:
			#TODO: See above
			part2 = ""
			if self._autoindent:
				x = 0
				while x < len(self._lines[self._cy]) and self._lines[self._cy][x] in [" ", "\t"]:
					part2 += self._lines[self._cy][x]
					x+=1
			offset = len(part2)
			part2 += self._lines[self._cy][self._cx:]
			self._lines[self._cy] = self._lines[self._cy][:self._cx]
			self._lines.insert(self._cy+1, part2)
			self._lines_changed.insert(self._cy+1, True)
			
			self._cx = offset
			self._cy +=1
		
		self._selx = self._cx
		self._sely = self._cy
		self._cursor_change()
		
	def _get_text(self, column, row, width):
		res = self._lines[row].expandtabs(self._tabwidth)
		attr = self.highlighter.highlight(res)
		
		return res[column:column+width], attr[column:column+width]
	
	def _text_len(self, row):
		return len(self._lines[row].expandtabs(self._tabwidth))
	
	
	def get_real_col(self, row, col):
		return len(self._lines[row][:col].expandtabs(self._tabwidth))
	def get_real_col_current(self):
		return self.get_real_col(self._cy, self._cx)
		
	def do_paint(self, wall):
		textwidth = self._size[0] - self._xborder-1
		textheight = self._size[1] - self._yborder
		# fix field of view
		real_cx = self.get_real_col_current()
		if real_cx >= self._column + textwidth:
			self._column = real_cx - textwidth + min(8,textwidth) - (real_cx - textwidth)%min(8,textwidth)
		if real_cx < self._column:
			self._column = real_cx - real_cx%min(8,textwidth)
		
		if self._cy >= self._line + textheight-1: 
			self._line = self._cy - textheight+1
		if self._cy < self._line:
			self._line = self._cy
		
		#get selection
		sx, sy, ex, ey = self.untangle_selection()
		
		self._caret = (self._xborder + real_cx - self._column, self._yborder + self._cy - self._line)
		for i in range(textheight):
			if i + self._line >= len(self._lines):
				continue
			
			text, attr = self._get_text(self._column, self._line+i, textwidth)# self._lines[self._line+i][self._column:self._column+textwidth]
			if self._column+textwidth < self._text_len(self._line+i):
				text = text + "…"
				attr.append(attr[-1])
			if self._column > 0:
				
				if len(text) > 0:
					text = "…" + text[1:]
				
				
			extraattr = [0 for a in attr]
			if i + self._line >= sy and i + self._line <= ey:
				rsx = self.get_real_col(sy, sx)
				rex = self.get_real_col(ey, ex)
				selstart = (0 if i+self._line > sy else rsx) - self._column
				selend = (len(text) if i+self._line < ey else rex) - self._column
				for k in range(max(0,selstart), min(selend, textwidth)):
					if k >= len(text):
						continue
					extraattr[k] |= zutils.AT_REVERSE
			
			for a in range(len(text)):
				wall.write_text(self._xborder+a,self._yborder+i,text[a], attr[a][0], attr[a][1], attr[a][2] | extraattr[a])
		slidpos = int(self._cy *1.0 / len(self._lines) * textheight)
		for i in range(textheight): #border
			if i + self._line >= len(self._lines):
				continue
			text = ""
			
			
			
			if self._cy == self._line+i or (self._line+i+1) % 5 == 0 or self._line+i == 0:
				text = "{:>3}".format(str( (self._line+i+1)%1000))
			else:
				text = "  ·"
			
		
			if slidpos == i and len(self._lines) > textheight:
				text += "▒"
			elif self._line+i == 0:
				text += "┍"
			elif self._line+i == len(self._lines)-1:
				text += "┕"
			else:
				text += "│"
			color = zutils.CL_FG
			if self._lines_changed[self._line+i]:
				color = zutils.CL_YELLOW
			wall.write_text(0,self._yborder+i,text, color, zutils.CL_BG, zutils.AT_DIM)
	
	def untangle_selection(self):
		sx = self._selx
		sy = self._sely
		ex = self._cx
		ey = self._cy
		if ey < sy or (ey == sy and ex < sx):
			ex = sx
			ey = sy
			sx = self._cx
			sy = self._cy
		
		return sx, sy, ex, ey
	
	def clear_selection(self):
		if self.readonly:
			return False
		
		sx, sy, ex, ey = self.untangle_selection()
		
		if(sx == ex and sy == ey):
			return False
		
		self._lines[sy] = self._lines[sy][:sx] + self._lines[ey][ex:]
		for j in range(sy+1,ey+1):
			self._lines.pop(sy+1)
			self._lines_changed.pop(sy+1)
		self.set_cursor(sx, sy)
		self._set_changed()
		return True
	
	def is_text_selected(self):
		sx, sy, ex, ey = self.untangle_selection()
		return not (sx == ex and sy == ey)
	
	def copy_selection(self):
		
		sx, sy, ex, ey = self.untangle_selection()
		
		if(sx == ex and sy == ey):
			return
		
		text = ""
		if sy != ey:
			text += self._lines[sy][sx:]+"\n"
			for j in range(sy+1,ey):
				text += self._lines[j]+"\n"
			text += self._lines[ey][:ex]
		else:
			text = self._lines[sy][sx:ex]
		
		zutils.copy_cp(text)
	
	def paste(self):
		text = zutils.get_cp()
		self.clear_selection()
		for c in text:
			self.writechar(c)
		
	
	def on_key(self, key, char):
		textheight = self._size[1] - self._yborder
		
		ctrl = False
		if(key == zutils.KEY_CLEFT or key == zutils.KEY_SLEFT):
			key = zutils.KEY_LEFT
			ctrl = True
		if(key == zutils.KEY_CRIGHT or key == zutils.KEY_SRIGHT):
			key = zutils.KEY_RIGHT
			ctrl = True
		if(key == zutils.KEY_CUP or key == zutils.KEY_SUP):
			key = zutils.KEY_UP
			ctrl = True
		if(key == zutils.KEY_CDOWN or key == zutils.KEY_SDOWN):
			key = zutils.KEY_DOWN
			ctrl = True
		if(key == zutils.KEY_CPAGEUP or key == zutils.KEY_SPAGEUP):
			key = zutils.KEY_PAGEUP
			ctrl = True
		if(key == zutils.KEY_CPAGEDOWN or key == zutils.KEY_SPAGEDOWN):
			key = zutils.KEY_PAGEDOWN
			ctrl = True
		if(key == zutils.KEY_CEND or key == zutils.KEY_SEND):
			key = zutils.KEY_END
			ctrl = True
		if(key == zutils.KEY_CHOME or key == zutils.KEY_SHOME):
			key = zutils.KEY_HOME
			ctrl = True
		
		
		
		
		if(key == zutils.KEY_LEFT):
			if self._cx == 0 and self._cy > 0:
				self.set_cursor(len(self._lines[self._cy-1]), self._cy - 1, ctrl)
			else:
				self.set_cursor(self._cx-1, self._cy, ctrl)
		
		elif(key == zutils.KEY_RIGHT):
			if self._cx == len(self._lines[self._cy]) and self._cy < len(self._lines)-1:
				self.set_cursor(0, self._cy+1, ctrl)
			else:
				self.set_cursor(self._cx+1, self._cy, ctrl)
		elif(key == zutils.KEY_UP):
			self.set_cursor(self._cx, self._cy-1, ctrl)
		elif(key == zutils.KEY_DOWN):
			self.set_cursor(self._cx, self._cy+1, ctrl)
		elif(key == zutils.KEY_PAGEUP):
			self.set_cursor(self._cx, self._cy-(textheight-1), ctrl)
		elif(key == zutils.KEY_PAGEDOWN):
			self.set_cursor(self._cx, self._cy+(textheight-1), ctrl)
		elif(key == zutils.KEY_END):
			self.set_cursor(len(self._lines[self._cy]), self._cy, ctrl)
		elif(key == zutils.KEY_HOME):
			self.set_cursor(0, self._cy, ctrl)
		elif(key == zutils.KEY_DEL and not self.readonly):
			if not self.clear_selection():
				if self._cx < len(self._lines[self._cy]):
					self._set_changed()
					self._lines[self._cy] = self._lines[self._cy][:self._cx] + self._lines[self._cy][self._cx+1:]
				elif self._cy < len(self._lines)-1:
					self._set_changed()
					self._lines[self._cy] += self._lines[self._cy+1]
					self._lines.pop(self._cy+1)
					self._lines_changed.pop(self._cy+1)
			#changed = True
			
		elif(key == zutils.KEY_BACKSPACE and not self.readonly):
			if not self.clear_selection():
				if self._cx > 0:
					self._set_changed()
					self._lines[self._cy] = self._lines[self._cy][:self._cx-1] + self._lines[self._cy][self._cx:]
					self.set_cursor(self._cx-1, self._cy)
				elif self._cy > 0:
					self._set_changed()
					self.set_cursor(len(self._lines[self._cy-1]), self._cy - 1)
					self._lines[self._cy] += self._lines[self._cy+1]
					self._lines.pop(self._cy+1)
					self._lines_changed.pop(self._cy+1)
			
		elif(key == zutils.KEY_SHT) and not self.readonly:
			if self.is_text_selected():
				self._set_changed()
				sx, sy, ex, ey = self.untangle_selection()
				for i in range(sy, ey+1):
					self._lines[i] = "\t" + self._lines[i]
					self._lines_changed[i] = True
			else:
				self.writechar("\t")
		elif(key == zutils.KEY_CX):
			self.copy_selection()
			self.clear_selection()
		elif(key == zutils.KEY_CA):
			self.set_cursor(0, 0, False)
			self.set_cursor(len(self._lines[-1]), len(self._lines)-1, True)
		elif(key == zutils.KEY_VT): #ctrl+c
			self.copy_selection()
		elif(key == zutils.KEY_CV and not self.readonly):
			self.paste()
		elif(not zutils.is_control(key) and zutils.is_printable(char) and not key == -1 and not self.readonly):
			self.clear_selection()
			self.writechar(char)

	
	
