import zwall
import zutils

class zobj( object ):
	def get_pos(self):
		return self._pos
	
	def get_global_pos(self):
		if self._parent == None:
			return self._pos
		else:
			return (self._parent.get_global_pos()[0] + self._pos[0], self._parent.get_global_pos()[1] + self._pos[1])
	
	def get_size(self):
		return self._size
	
	def get_caret(self):
		return self._caret
	
	def get_focused(self):
		return self
	
	def is_focused(self):
		if self._parent != None:
			return self._parent.get_focused() == self
		else:
			return true
		
	def is_visible(self):
		return self._visible
	
	def wants_focus(self):
		if not self._visible:
			return False
		return self._wants_focus
	
	def set_visible(self, visible):
		self._visible = visible
		if not self._visible and self.is_focused() and self._parent != None:
			#exit()
			self._parent.next_focus()
		elif self._parent != None and self._parent._focused == -1:
			self._parent.next_focus()
			
	
	
	def do_paint(self, wall):
		return
	
	def on_get_focus(self):
		return
	
	def on_lost_focus(self):
		return
	
	def on_key(self, key, char):
		return
		
	def paint(self, wall):
		if(self._visible):
			self.do_paint(wall)
	
	def clear_wall(self, wall):
		ox = wall._offset[0]
		oy = wall._offset[1]
		for x in range(self._size[0]):
			for y in range(self._size[1]):
				wall.get_wall()[y+oy][x+ox].c = " "
				wall.get_wall()[y+oy][x+ox].fcolor = zutils.CL_FG
				wall.get_wall()[y+oy][x+ox].bcolor = zutils.CL_BG
				wall.get_wall()[y+oy][x+ox].attr = zutils.AT_NORMAL
	
	def insert_wall(self, wall_to, wall_from):
		ox = wall_to._offset[0]
		oy = wall_to._offset[1]
		
		ox2 = wall_from._offset[0]
		oy2 = wall_from._offset[1]
		
		for x in range(self._size[0]):
			for y in range(self._size[1]):
				wall_to.get_wall()[y+oy][x+ox].copy_from(wall_from.get_wall()[y+oy2][x+ox2])
	
	
	def __init__(self, parent, pos = (0,0), size = (0,0)):
		self._parent = parent
		self._pos = pos
		self._size = size
		self._caret = (0,0)
		self._visible = True
		self._wants_focus = True
