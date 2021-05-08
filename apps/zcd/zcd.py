import zapp
import zframe
import zborderframe
import zlabel
import zkeylabel
import zlineedit
import ztextedit
import zfilebrowser
import zutils
import zdialogbox
import zquerybox
import ztextbox


import subprocess
import os
import re
import pwd
import sys

import threading


class zcd(zapp.zapp):
	
	def file_select(self, sender, fn):
		#self.lbl.set_caption(fn)
		os.chdir(fn)
		print(fn, file=sys.stderr)
		exit()
	
	def do_run(self):
		cwd = os.getcwd() + "/"
		
		
		r = self._root_frame
		
		r.set_catch_focus(False)
		
		fb = zfilebrowser.zfilebrowser(r, (0,0), (r._size[0], r._size[1]), cwd, True, False)
		r.add_child(fb)
		
		fb.on_file_select = self.file_select
		
		#self.lbl = zlabel.zlabel(r, (0,r.get_size()[1]-1), (r.get_size()[0], 1), cwd)
		#r.add_child(self.lbl)
		
		while True:
			self.render()
			c, buf = self._get_char()
			
			if(c == zutils.KEY_ESC):
				break
			
			
			
			r.on_key(c, buf)


app = zcd()
app.run()
