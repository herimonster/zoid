import zborderframe
import zlabel
import zlineedit
import zwall
import zutils

class zdialogbox(zborderframe.zborderframe):
	def __init__(self, parent, pos=(0,0), size=(0,0), caption="", query="", answers=None):
		super().__init__(parent, pos, size, caption)
		if answers == None:
			answers = ["Ok"]
		
		self._caption = caption
		self._query = zlabel.zlabel(self, (1,2), (self._size[0]-2, 1), query)
		
		self.add_child(self._query)
		
		self.lbls = []
		w = (self._size[0]-2) // len(answers)
		for i in range(len(answers)):
			lbl = zlabel.zlabel(self, (1+i*w,4), (w-1,1), answers[i])
			self.lbls.append(lbl)
			self.add_child(lbl)
		self.set_focus(self.lbls[0])
		self.selected = 0
		
	def on_key(self, c, buf):
		super().on_key(c, buf)
		if c == zutils.KEY_LEFT:
			self.selected -= 1
			if self.selected < 0:
				self.selected = len(self.lbls)-1
			self.set_focus(self.lbls[self.selected])
		elif c == zutils.KEY_RIGHT:
			self.selected += 1
			if self.selected >= len(self.lbls):
				self.selected = 0
			self.set_focus(self.lbls[self.selected])
	
	def _on_enter(self):
		if self.on_enter != None:
			self.on_enter()
	
	def get_selected(self):
		return self.selected
	
	def do_paint(self, wall):
		self.clear_wall(wall)
		super().do_paint(wall)
	
def query(parent, caption, query, answers = None):
	r = parent._root_frame
	
	w = r.get_size()[0]
	h = 7
	y = int(r.get_size()[1] / 2 - 4)
	if y < 0:
		y = 0
		h = r.get_size()[1]
	
	wui = zdialogbox(r, (0,y), (w,h), caption, query, answers)
	r.add_child(wui)
	r.set_focus(wui)
	
	res = None
	c = None
	
	while True:
		parent.render(do_clear = False)
		c, buf = parent._get_char()
		
		if c == zutils.KEY_RETURN:
			res = wui.get_selected()
			break
		elif c == zutils.KEY_ESC:
			res = -1
			break
		
		#elif c == zutils.KEY_VT:
		#	break
		
		wui.on_key(c, buf)
	
	r.remove_child(wui)
	return res, c
