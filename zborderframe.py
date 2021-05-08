import zframe
import zwall
import zutils

class zborderframe(zframe.zframe):
	ch_h = ["─", "═"]
	ch_v = ["│", "║"]
	ch_tl= ["┌", "╔"]
	ch_tr= ["┐", "╗"]
	ch_bl= ["└", "╚"]
	ch_br= ["┘", "╝"]
	
	
	def __init__(self, parent, pos=(0,0), size=(0,0), caption=""):
		super().__init__(parent, pos, size)
		self._caption = caption
	
	def do_paint(self, wall):
		ox = wall._offset[0]
		oy = wall._offset[1]
		super().do_paint(wall)
		
		if(self._size[0] == 0 or self._size[1] == 0):
			return
		
		style = 1 if self.is_focused() else 0
		
		for x in range(self._size[0]):
			c = self.ch_h[style]
			if(x == 0): c =                 self.ch_tl[style]
			elif(x == self._size[0]-1): c = self.ch_tr[style]
			
			wall.get_wall()[oy][x+ox].c = c
			wall.get_wall()[oy][x+ox].fcolor = zutils.CL_FG
			wall.get_wall()[oy][x+ox].bcolor = zutils.CL_BG
			wall.get_wall()[oy][x+ox].attr   = zutils.AT_NORMAL
			#if(x >= 1 and x <= len(self._caption)):
			#	wall.get_wall()[0][x].c = self._caption[x-1]
			
			if(x == 0): c =                 self.ch_bl[style]
			elif(x == self._size[0]-1): c = self.ch_br[style]
			
			wall.get_wall()[oy + self._size[1]-1][x+ox].c = c
			wall.get_wall()[oy + self._size[1]-1][x+ox].fcolor = zutils.CL_FG
			wall.get_wall()[oy + self._size[1]-1][x+ox].bcolor = zutils.CL_BG
			wall.get_wall()[oy + self._size[1]-1][x+ox].attr   = zutils.AT_NORMAL
		
		wall.write_text(1,0,self._caption)
		
		for y in range(1,self._size[1]-1):
			c = self.ch_v[style]
			
			wall.get_wall()[oy+y][ox].c = c
			wall.get_wall()[oy+y][ox+self._size[0]-1].c = c
		
		#wall.get_wall()[0][0].c = "Y" if self.is_focused() else "N"
		
	def set_caption(self, caption):
		self._caption = caption
	def get_caption(self):
		return self._caption
