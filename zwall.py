import zutils

class zbrick:
	def __init__(self):
		self.c = ' '
		self.fcolor = zutils.CL_FG
		self.bcolor = zutils.CL_BG
		self.attr   = 0
	
	def str(self):
		return str(c)
	
	def copy_from(self, other):
		self.c = other.c
		self.fcolor = other.fcolor
		self.bcolor = other.bcolor
		self.attr   = other.attr
	
	def equals(self, other):
		return self.c == other.c and self.fcolor == other.fcolor and self.bcolor == other.bcolor and self.attr == other.attr
	
	def __eq__(self, other):
		return self.equals(other)


class zwall:

	def __init__(self, width, height):
		self._width = width
		self._height = height
		self._wall = [[0]*width for i in range(height)]
		self._offset = [0,0]
		self.clear()
		
				
		
	
			
	def get_wall(self):
		return self._wall
	def get_width(self):
		return self._width
	def get_height(self):
		return self._height
	
	def write_text(self, x, y, text, fg = -1, bg = -1, attr = 0):
		x += self._offset[0]
		y += self._offset[1]
		
		if fg == -1:
			fg = zutils.CL_FG
		if bg == -1:
			bg = zutils.CL_BG
		
		if(y < 0 or y >= self._height):
			return
		for _x in range( min(len(text), self._width - x) ):
			self._wall[y][x+_x].c = text[_x]
			self._wall[y][x+_x].fcolor = fg
			self._wall[y][x+_x].bcolor = bg
			self._wall[y][x+_x].attr = attr
			
			
	
	
	def scroll_up(self):
		old = self._wall.pop(0)
		
		for x in range(self._width):
			old[x] = zbrick()
		
		self._wall += (old)
	
	
	def clear(self):
		for y in range(self._height):
			for x in range(self._width):
				self._wall[y][x] = zbrick()
		
	
	def copy_from(self, otherwall):
		for y in range(self._height):
			for x in range(self._width):
				self._wall[y][x].copy_from(otherwall._wall[y][x])
	
	def __str__(self):
		res = ""
		for y in range(self._height):
			for x in range(self._width):
				 res += self._wall[y][x].c
			res += "\n"
		return res
	
