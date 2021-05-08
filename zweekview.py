import zborderframe
import zlabel
import zwall
import zutils
from calendar import *
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import dateutil.parser
import pytz
from tzlocal import get_localzone


daynames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

evcolors = [zutils.CL_BLUE, zutils.CL_CYAN, zutils.CL_MAGENTA, zutils.CL_RED, zutils.CL_GREEN, zutils.CL_YELLOW, zutils.CL_GREY, zutils.CL_WHITE ]


def do_intersect(s1, e1, s2, e2):
	return (s1 <= s2 <= e1) or (s2 <= s1 <= e2)

class zweekview(zborderframe.zborderframe):
	def __init__(self, parent, pos=(0,0), size=(0,0),  year = 2000, month=1, day=1, starttime = 8, endtime = 20):
		super().__init__(parent, pos, size, "")
		
		self.starttime = starttime
		self.endtime = endtime
		
		
		
		self.set_date(year, month, day)
		
		self.on_get_calendar_data = None
		self.on_select_event = None
		self.lz = get_localzone()
		
		self.do_update = True
		
	def set_date(self, year, month, day):
		self.year = year
		self.month = month
		self.day = day
		self.selected_event = -1
		
	
	
	def do_paint(self, wall):
		if not self.do_update:
			return
		self.clear_wall(wall)
		super().do_paint(wall)
		
		
		width = self.get_size()[0]
		cwidth = width-5
		height = self.get_size()[1]
		cheight = height - 2 - 4
		wpd = int((cwidth-2) / 7)
		d = date(self.year, self.month, self.day)
		dow = d.weekday()
		
		cd = d + relativedelta(days=-dow)
		for day in range(7):
			dx = wpd*day + 5
			if day == 6:
				wpd = wpd + cwidth-2 - wpd*7 
			
			
			att = zutils.AT_NORMAL
			if cd == d:
				att = zutils.AT_REVERSE
			wall.write_text(dx+2, 1, daynames[day].center(wpd-3)[:wpd-2], attr=att)
			wall.write_text(dx+2, 2, cd.strftime('%d.%m').center(wpd-3)[:wpd-2], attr=att)
			wall.write_text(dx+1, 4, "─"*wpd)
			
			wall.write_text(dx, 0, "┬" if day > 0 else "┌")
			for y in range(1, self.get_size()[1]-1):
				wall.write_text(dx, y, "│")
			
			wall.write_text(dx, self.get_size()[1]-1, "┴" if day > 0 else "└")
			
			events = []
			if self.on_get_calendar_data != None:
				events = self.on_get_calendar_data(cd.year, cd.month, cd.day)
			
			for e in events:
				e['line'] = 0
				e['txtrest'] = ""
				e['numev'] = -2
			
			if len(events) > 0:
				dayevents = []
				
				for e in events:
					if not 'date' in e['start']: #only non-whole-day events
						continue
					dayevents.append(e)
				
				nevents = len(dayevents)
				i = 0
				
				if nevents > 0:				
					wpe = int((wpd-1.)/nevents)
					for e in dayevents:
						wall.write_text(dx+1+i*wpe, 3, e['summary'][:wpe], evcolors[i%len(evcolors)], zutils.CL_BG, zutils.AT_REVERSE if i != self.selected_event or cd != d else zutils.AT_UNDERLINE)
						if self.on_select_event != None and i == self.selected_event and d == cd:
							start = e['start']['date']
							end = e['end']['date']
							startdate = dateutil.parser.parse(start).date()
							enddate = dateutil.parser.parse(end).date()
							self.on_select_event(e, startdate, enddate)
						i+=1
				
				for line in range(cheight):
					
					atime = self.starttime + (self.endtime - self.starttime)*line*1.0/cheight
					ahour = int(atime)
					aminute = int((atime-int(atime))*60)
					
					etime = self.starttime + (self.endtime - self.starttime)*(line+1)*1.0/cheight
					ehour = int(etime)
					eminute = int((etime-int(etime))*60)
					
					atimed = self.lz.localize(datetime(cd.year, cd.month, cd.day, ahour, aminute, 0))
					etimed = self.lz.localize(datetime(cd.year, cd.month, cd.day, ehour, eminute, 59))
					
					#wall.write_text(dx, 5 + line, "?")
					colori = 1
					extradeltax = 0
					numevents = 0
					for e in events:
						if not 'dateTime' in e['start']: #only non-whole-day events
							continue
						
						start = e['start'].get('dateTime', e['start'].get('date'))
						end = e['end'].get('dateTime', e['start'].get('date'))
						startdate = dateutil.parser.parse(start)
						enddate = dateutil.parser.parse(end)
						
						if do_intersect(startdate, enddate, atimed, etimed):
							l = e['line']
							txt = ""
							if l == 0:
								txt = startdate.strftime("%H:%M") + " "
								txt += e['summary']
								if self.on_select_event != None and i == self.selected_event and d == cd:
									self.on_select_event(e, startdate, enddate)
									
								if e['numev'] == -2:
									e['numev'] = i
									i += 1
								
								
							else:
								txt = " "+e['txtrest']
							txt = txt.ljust(wpd-1-extradeltax)
							
							wall.write_text(dx+1+extradeltax, 5 + line, txt[:wpd-1-extradeltax], evcolors[colori%len(evcolors)], zutils.CL_BG, zutils.AT_REVERSE if e['numev'] != self.selected_event or cd != d  else zutils.AT_UNDERLINE)
							txtrest = txt[wpd-1-extradeltax:]
							e['txtrest'] = txtrest
							
							
							
							e['line'] += 1
							
							numevents += 1
							
							extradeltax = int((1.-1./2**numevents)*(wpd-1))
							
						colori += 1
						
						#else:
						#	wall.write_text(dx, 5 + line, str(len(events)))
					
			
			cd = cd + relativedelta(days=1)
		
		for line in range(height):
			wall.write_text(0, line, " "*5)
		
		
		for line in range(cheight):
			atime = self.starttime + (self.endtime - self.starttime)*line*1.0/cheight
			fullhour = str(int(atime))
			minutes = str(int((atime-int(atime))*60))
			if len(minutes) == 1:
				minutes = "0"+minutes
			wall.write_text(0, 5 + line, (fullhour+":"+minutes).rjust(5)[:5], attr = zutils.AT_DIM)
		
		
		
	def on_key(self, c, buf):
		if c == zutils.KEY_SDOWN:
			self.selected_event += 1
		elif c == zutils.KEY_SUP:
			self.selected_event -= 1
			if self.selected_event < -1:
				self.selected_event = -1
		pass
