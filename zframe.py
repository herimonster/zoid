import zobj
import zwall
import zutils
import traceback

class zframe(zobj.zobj):
	## private
	def _set_focused(self, new_foc):
		if(len(self._children) == 0):
			self._focused = -1
			return
		
		if self._focused != -1:
			self._children[self._focused].on_lost_focus()
		
		if(new_foc < 0 or new_foc >= len(self._children)):
			self._focused = -1
			return
		
		self._focused = new_foc
		self._children[self._focused].on_get_focus()
	
	## public
	def __init__(self, parent, pos = (0,0), size = (0,0)):
		super().__init__(parent, pos, size)
		self._children = []
		self._focused = -1
		self._do_catch_focus = True
	
	def do_paint(self, wall):
		oo = wall._offset
		for c in self._children:
			o = [oo[0] + c.get_pos()[0], oo[1] + c.get_pos()[1]]
			wall._offset = o
			#cwall = zwall.zwall(c.get_size()[0], c.get_size()[1])
			c.paint(wall)
			#wall.integrate(cwall, c.get_pos()[0], c.get_pos()[1])
		wall._offset = oo
	
	def add_child(self, c):
		self._children.append(c)
		if(self._focused == -1):
			self._set_focused(0)
			
	
	def remove_child(self, c):
		
		idx = self._children.index(c)
		
		if(self._focused == idx):
			self.next_focus()
			if(self._focused == idx): #still...
				self._focused = -1
			
		if(self._focused > idx):
			self._focused -= 1 #todo: always holds?
		self._children.pop(idx)
	
	def get_focused(self, recurse=True):
		if(self._focused == -1):
			return self
		
		if recurse:
			return self._children[self._focused].get_focused()
		else:
			return self._children[self._focused]
	
	def is_focused(self):
		if self._parent != None:
			return self._parent.get_focused(False) == self
		else:
			return true
		
	def next_focus(self, reverse = False):
		delta = 1 if not reverse else -1
		if len(self._children) == 0:
			return
		
		starti = self._focused
		nexti = (self._focused+delta) % len(self._children)
		
		
		while nexti != starti and not self._children[nexti].wants_focus():
			nexti = (nexti+delta) % len(self._children)
		
		#zutils.debug("\n".join(traceback.format_stack()))
		if nexti == starti and self._children[nexti].wants_focus() :
			self._set_focused( nexti )
		elif nexti != starti:
			self._set_focused( nexti )
		else:
			self._set_focused( -1 )
	
	def set_focus(self, child):
		if not child in self._children:
			return False
		if not child.wants_focus():
			return False
		i = self._children.index(child)
		self._set_focused(i)
		return True
	
	def set_catch_focus(self, do_catch_focus):
		self._do_catch_focus = do_catch_focus
	
	def get_catch_focus(self):
		return self._do_catch_focus
	
	def on_key(self, key, char):
		if self._do_catch_focus:
			if(key == zutils.KEY_SHT):
				self.next_focus()
				return
		#elif(key == zutils.KEY_HT):
		#	key = zutils.KEY_SHT
		
		if(self._focused != -1):
			self._children[self._focused].on_key(key, char)
		
	
	def get_children(self):
		return self._children
