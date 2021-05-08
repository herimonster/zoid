import zapp
import zframe
import zborderframe
import zlabel
import zkeylabel
import zlineedit
import ztextedit
import ztable
import zutils

import os
import re
import pwd


class zop(zapp.zapp):
	PROC_DIR = "/proc"
	
	def get_user(self, id):
		try:
			return str(pwd.getpwuid( id ).pw_name)
		except:
			return str(id)
	
	def rebuild(self):
		pattern = re.compile("^[0-9]+$")
		listing = os.listdir(self.PROC_DIR)
		res = []
		for infile in listing:
			if not pattern.match(infile):
				continue
			if not os.path.isdir(self.PROC_DIR + "/" + infile):
				continue
			#print(infile)
			data  = ""
			with open(self.PROC_DIR+"/"+infile+"/status", 'r') as f:
				data = f.read()
			with open(self.PROC_DIR+"/"+infile+"/cmdline", 'r') as f:
				data += "CmdLine: " + f.read()
				
			#d = [item.split(":") for item in data.split("\n")]
			d = []
			for pair in [item.split(":", 1) for item in data.split("\n")]:
				if len(pair) < 2:
					continue
				
				pair[0] = pair[0].strip()
				
				pair[1] = pair[1].strip()
				
				d.append(pair)
				
			data = dict(d)
			res.append(data)
			
		return res
	
	def reinsert(self, tab):
		procs = self.rebuild()
		
		tab.rows.clear();
		
		for i in range(len(procs)):
			#tab.add_row([str(i), "Test", "root", "1024", "43", "1", "/bin/Test"])
			self.HUI = i
			self.HUI2 = procs[i]
			
			pid = int(procs[i]["Pid"])
			name = procs[i]["Name"]
			owner = self.get_user(int(procs[i]["Uid"].split("\t")[0]))
			mem = procs[i]["VmRSS"] if "VmRSS" in procs[i] else ""
			if mem != "":
				#mem = str(int(float(mem.split(" ")[0]) / 1000.0))
				mem = int(mem.split(" ")[0])
			else:
				mem = 0;
			cpu = "43"
			parent = int(procs[i]["PPid"])
			
			#tab.rows.append([str(i), procs[i]["Name"], self.get_user(int(procs[i]["Pid"])), procs[i]["VmSize"] if "VmSize" in procs[i] else "", "43", procs[i]["PPid"], procs[i]["CmdLine"]])
			tab.rows.append([pid, name, owner, mem, cpu, parent, ""])
			tab.resort()
	
	def do_run(self):
		r = self._root_frame
		
		tab = ztable.ztable(r, (0,0), r._size, 7)
		r.add_child(tab)
		tab.head[0]["caption"] = "PID"
		tab.head[0]["width"]   =  6
		tab.head[0]["align"]   = ztable.ztable.AL_RIGHT
		
		tab.head[1]["caption"] = "Name"
		tab.head[1]["width"]   =  16
		
		
		tab.head[2]["caption"] = "Owner"
		tab.head[2]["width"]   =  10
		
		tab.head[3]["caption"] = "Mem"
		tab.head[3]["width"]   =  9
		tab.head[3]["align"]   = ztable.ztable.AL_RIGHT
		
		tab.head[4]["caption"] = "CPU"
		tab.head[4]["width"]   =  4
		tab.head[4]["align"]   = ztable.ztable.AL_RIGHT
		
		tab.head[5]["caption"] = "Parent"
		tab.head[5]["width"]   =  6
		tab.head[5]["align"]   = ztable.ztable.AL_RIGHT
		
		w = 0
		for i in range(6):
			w += tab.head[i]["width"]
		
		w = tab._size[0] - w
		
		tab.head[6]["caption"] = "Command Line"
		tab.head[6]["width"]   =  w
		

		
		#wupp = ztextedit.ztextedit(r, (10,5), (20, 8), "")
		#r.add_child(wupp)
		
		r.next_focus()
		
		#bf = zborderframe.zborderframe(self._root_frame, (2,2), (70,20), "Hallo")
		#bf2 = zborderframe.zborderframe(self._root_frame, (75,2), (20,10), "Hallo2")
		
		#lbl = zkeylabel.zkeylabel(bf2, (1,1), (18,1), "HUHU")
		#ed = zlineedit.zlineedit(bf, (1,1), (18,1), "Test text" )
		#tab = ztable.ztable(bf, (1,2), (68,17), 4)
		#bf2.add_child(lbl)
		#bf.add_child(ed)
		#bf.add_child(tab)
		
		
			#tab.add_row(["Test " + str(i), "i*i = " + str(i*i), "i^i = " + str(i**i), "Ende", ])
		
		#bf = zborderframe.zborderframe(None, (2,2), (20,20), "Hallo")
		#self._root_frame.add_child(bf)
		#self._root_frame.add_child(bf2)
		
		#ed.on_enter = lambda sender: tab.add_row([ed.get_text(), "2", "3", "4"]) or ed.set_text("")
		#ed.on_change = lambda sender: lbl2.set_caption(sender.get_text()) or lbl2.set_fcolor(-1)
		
		
		self.reinsert(tab)
		while True:
			self.render()
			c, buf = self._get_char()
			
			if(buf == "r"):
				self.reinsert(tab)
			elif(buf == "d"):
				tab.set_desc(not tab.get_desc())
			elif(buf == ">"):
				tab.set_order_by(tab.get_order_by()+1)
			elif(buf == "<"):
				tab.set_order_by(tab.get_order_by()-1)
				
			self._root_frame.on_key(c, buf)


app = zop()
app.run()
