import zobj
import zwall
import zutils
import zlabel


class zcheckbox(zlabel.zlabel):
	def __init__(self, parent, pos=(0,0), size=(0,0), caption=""):
		super().__init__(parent, pos, size, caption)
		self._checked = False
	
	def set_checked(self, checked):
		self._checked = checked
	
	def is_checked(self):
		return self._checked
	
	def do_paint(self, wall):
		#✗
		box = "✗" if self._checked else " "
		
		wall.write_text(0,0,box, self.get_fcolor(), self.get_bcolor(), self.get_attr() | zutils.AT_UNDERLINE)
		
		wall.write_text(1,0," "+self._caption, self.get_fcolor(), self.get_bcolor(), self.get_attr())
	
	def on_key(self, key, char):
		super().on_key(key, char)
		
		if key == zutils.KEY_SPACE:
			self.set_checked(not self.is_checked())
