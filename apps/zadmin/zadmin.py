import zapp
import zframe
import zborderframe
import zlabel
import zkeylabel
import zlineedit
import ztextedit
import ztable
import zutils
import zdialogbox
import zquerybox
import ztextbox


import subprocess
import os
import re
import pwd

import threading
	

def sshopen(host, cmd):
		p = subprocess.Popen(["ssh", "-o", "ConnectTimeout=1", "-o", "StrictHostKeyChecking=no", "root@"+host, cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		
		rc = p.returncode
		
		reachable = rc == 0
		return (reachable, out.decode("utf-8"), err.decode("utf-8"))

class sshThread(threading.Thread):
	def __init__(self, host, cmd):
		threading.Thread.__init__(self)
		self.host = host
		self.cmd = cmd
	
	def run(self):
		self.result = sshopen(self.host, self.cmd)

class zadmin(zapp.zapp):
	PC_DIR = "tp-hosts"
	
	def wakeonlan(self, mac):
		mac = mac.replace(mac, '')
		mac = mac.upper()
		if not re.search('[0-9a-fA-F]{12}', mac):
			return False
		
		magic_packet = ''.join(['FF' * 6, mac * 16])
		send_data = ''
		for i in range(0, len(magic_packet), 2):
			send_data = ''.join([send_data, struct.pack('B', int(magic_packet[i: i + 2], 16))])
		
		dgramSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		dgramSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		dgramSocket.sendto(send_data, ("255.255.255.255", 9))
		return True
	
	def rebuild(self):
		entries = []
		with open(self.PC_DIR, "r") as f:
			for line in f:
				if line.strip().startswith("#"):
					continue
				l = line.split("\t")
				if len(l) < 2:
					continue
				
				if len(l) < 3:
					entries.append([l[0].strip(), l[1].strip(), ""])
				else:
					entries.append([l[0].strip(), l[1].strip(), l[2].strip()])
		
		return entries
	
	def reinsert(self, tab):
		self.entries = self.rebuild()
		
		tab.rows.clear();
		
		sshresults = []
		threads = []
		for i in range(len(self.entries)):
			name = self.entries[i][0]
			t = sshThread(name, "who && tail -1 /var/log/dpkg.log | awk '{print $1}'")
			t.start()
			threads.append(t)
		for i in range(len(self.entries)):
			threads[i].join()
			sshresults.append(threads[i].result)
		
		for i in range(len(self.entries)):
			name = self.entries[i][0]
			(is_running, who_out, who_err) = sshresults[i]
			
			running = "●" if is_running else "○"
			place = self.entries[i][1]
			
			if is_running:
				users = 0
				lines = who_out.split("\n")
				for l in lines:
					if not l.startswith("(unknown)") and not l == "" and not l[0].isdigit():
						users += 1
				users = str(users)
				if len(lines)>=2:
					last_update = lines[-2] if lines[-2][:1].isdigit() else "last month"
				else:
					last_update = "last month"
			else:
				users = ""
				last_update = ""
			
			#name=str(info[1])
			tab.rows.append([running, name, place, users, last_update, str(i)])
		
		
		tab.resort()
	
	def do_run(self):
		r = self._root_frame
		
		tab = ztable.ztable(r, (0,0), (r._size[0], r._size[1]-1), 6)
		r.add_child(tab)
		tab.head[0]["caption"] = "R"
		tab.head[0]["width"]   =  2
		tab.head[0]["align"]   = ztable.ztable.AL_RIGHT
		
		tab.head[1]["caption"] = "Name"
		tab.head[1]["width"]   =  0
		
		tab.head[2]["caption"] = "Place"
		tab.head[2]["width"]   =  6
		
		tab.head[3]["caption"] = "Users"
		tab.head[3]["width"]   =  9
		tab.head[3]["align"]   = ztable.ztable.AL_RIGHT
		
		tab.head[4]["caption"] = "Last Upd."
		tab.head[4]["width"]   =  11
		tab.head[4]["align"]   = ztable.ztable.AL_RIGHT
		
		tab.head[5]["caption"] = "id"
		tab.head[5]["width"]   =  3
		tab.head[5]["align"]   = ztable.ztable.AL_RIGHT
		
		
		w = 0
		for i in range(6):
			w += tab.head[i]["width"]
		
		w = tab._size[0] - w
		
		tab.head[1]["width"] = w
		
		lbl = zlabel.zlabel(r, (0,r.get_size()[1]-1), (r.get_size()[0], 1), "Keys: q=Quit r=Refresh b=Boot s=Shutdown c=Run Command")
		r.add_child(lbl)
		
		#r.next_focus()
		
		self.reinsert(tab)
		tab.set_order_by(1)
		
		lastcmd = ""
		lasttime = "now"
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
			elif(buf == "q"):
				break
			elif(buf == "b"):
				i = int(tab.get_row_entry()[-1])
				mac = self.entries[i][2]
				if mac != "":
					res, c = zdialogbox.query(self, "Sure?", "Do you really want to boot " + mac + "?", ["Yes!", "No!"])
					if res == 0:
						self.wakeonlan(mac)
					else:
						pass
			elif(buf == "s"):
				i = int(tab.get_row_entry()[-1])
				name = self.entries[i][0]
				
				res, c = zquerybox.query(self, "When?", "Enter time for reboot (ESC to cancel)", lasttime)
				if res != None:
					lasttime = res
					(r, out, err) = sshopen(name, "shutdown -h "+res)
					if not r:
						if not "closed by remote host" in err:
							zdialogbox.query(self, "Error!", err)
			
			elif(buf == "c"):
				i = int(tab.get_row_entry()[-1])
				name = self.entries[i][0]
				
				res, c = zquerybox.query(self, "Command?", "Which command? (ESC to cancel)", lastcmd)
				
				if res != None:
					lastcmd = res
					(r, out, err) = sshopen(name, res)
					if r:
						ztextbox.query(self, "Output", out, True)
					else:
						ztextbox.query(self, "Error!", err, True)
						
				
			self._root_frame.on_key(c, buf)


app = zadmin()
app.run()


