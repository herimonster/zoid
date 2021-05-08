import zobj
import zwall
import zutils
import zframe
import ztextedit
import zlabel

class ztextframe(zframe.zframe):
	def __init__(self, parent, pos = (0,0), size = (0,0)):
		super().__init__(parent, pos, size)
		self._textedit =  ztextedit.ztextedit(self, (0,0), (self._size[0], self._size[1]-1), "")
		self.add_child(self._textedit)
		self._status = zlabel.zlabel(self, (0,self._size[1]-1), (self._size[0], 1), " - ")
		#self._status.set_fcolor(zutils.CL_FG)
		#self._status.set_bcolor(zutils.CL_BG)
		self._status.set_attr(zutils.AT_DIM)
		self.add_child(self._status)
		
		self.update_status()
		
		self._textedit.on_cursor_change = self._cursor_changed
		self._textedit.on_change = self._on_changed
		
		self.on_change = None
	
	def _cursor_changed(self, sender):
		self.update_status()
	def _on_changed(self, sender):
		self.update_status()
		if self.on_change != None:
			self.on_change(self)
	
	def resize(self, size):
		self._size = size
		self._textedit._size = (self._size[0],  self._size[1]-1)
		self._status._size = (self._size[0], 1)
		self._status._pos = (0, self._size[1]-1)
	
	def update_status(self):
		cx, cy = self._textedit.get_cursor()
		mx, my = self._textedit.get_cursor_limits()
		changed = self._textedit.get_changed()
		s = "  "+ ("*" if changed else " ") + " ("+str(cy+1)+":"+str(cx+1)+") / ("+str(my)+":"+str(mx+1)+")"
		self._status.set_caption(s)
