import zborderframe
import zlabel
import zwall
import zutils
from calendar import *
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

monthnames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
daynames = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

SM_MONTH = 0
SM_WEEK = 1
SM_DAY = 2

class zcalendar(zborderframe.zborderframe):
	def __init__(self, parent, pos=(0,0), size=(0,0),  year = 2000, month = 1, day = 1, selmode = SM_MONTH):
		if size == (0,0):
			size = (27,9)
		
		super().__init__(parent, pos, size, "")
		
		self.year = 0
		self.month = 0
		self.day = 0
		
		
		self.selmode = selmode
		self.on_highlight_day = None
		self.on_date_change = None
		
		self.set_date(year, month, day)
		
		self.do_update = True
		
		
	def set_date(self, year, month, day):
		if year != self.year or month != self.month or day != self.day:
			self.year = year
			self.month = month
			self.day = day
			self._caption = " "+monthnames[month-1] + " " +str(year)+" "
			if self.on_date_change != None:
				self.on_date_change(self.year, self.month, self.day)
		
	
	
	def do_paint(self, wall):
		if not self.do_update:
			return
		self.clear_wall(wall)
		super().do_paint(wall)
		
		wall.write_text(1, 1, "CW ")
		c = 5
		for day in daynames:
			wall.write_text(c, 1, day, zutils.CL_FG, zutils.CL_BG, zutils.AT_UNDERLINE)
			c += 3
		
		numdays = monthrange(self.year, self.month)
		wd = numdays[0]
		r = 2
		
		cw = date(self.year, self.month, self.day).isocalendar()[1]
		
		for day in range(1, numdays[1]+1):
			fg = zutils.CL_FG
			bg = zutils.CL_BG
			att = zutils.AT_NORMAL
			if self.on_highlight_day != None:
				fg, bg, att = self.on_highlight_day(self.year, self.month, day)
			
			if (self.selmode == SM_DAY or self.selmode == SM_WEEK) and day == self.day:
				att = zutils.AT_REVERSE
			if self.selmode == SM_WEEK and cw == date(self.year, self.month, day).isocalendar()[1]:
				att = zutils.AT_REVERSE
			
			
			dstr = str(day).rjust(2)
			
			wall.write_text(3*wd + 5, r, dstr, fg, bg, att)
			wd = (wd + 1) % 7
			if wd == 0:
				r += 1
		
		cw = date(self.year, self.month, 1).isocalendar()[1]
		for r in range(2, 8):
			cwstr = str(cw).rjust(2)
			wall.write_text(1, r, cwstr, zutils.CL_FG, zutils.CL_BG, zutils.AT_DIM)
			cw += 1
	
	def on_key(self, c, buf):
		newdate = date(self.year, self.month, self.day)
		
		if (self.selmode != SM_DAY and c == zutils.KEY_LEFT) or (self.selmode == SM_DAY and c == zutils.KEY_SLEFT):
			newdate = newdate + relativedelta(months = -1)
		
		elif (self.selmode != SM_DAY and c == zutils.KEY_RIGHT) or (self.selmode == SM_DAY and c == zutils.KEY_SRIGHT):
			newdate = newdate + relativedelta(months = +1)
		
		elif self.selmode == SM_DAY and c == zutils.KEY_LEFT:
			newdate = newdate + relativedelta(days=-1)
			
		elif self.selmode == SM_DAY and c == zutils.KEY_RIGHT:
			newdate = newdate + relativedelta(days=1)
		
		elif self.selmode != SM_MONTH and c == zutils.KEY_UP:
			olddate = newdate
			newdate = newdate + relativedelta(weeks=-1)
			if self.selmode == SM_WEEK:
				if olddate.month != newdate.month and olddate.day != 1:
					newdate = date(olddate.year, olddate.month, 1)
				elif olddate.month != newdate.month and olddate.day == 1:
					newdate = date(newdate.year, newdate.month, monthrange(newdate.year, newdate.month)[1])
				
				
			
		elif self.selmode != SM_MONTH and c == zutils.KEY_DOWN:
			olddate = newdate
			newdate = newdate + relativedelta(weeks=1)
			if self.selmode == SM_WEEK:
				lastday = monthrange(olddate.year, olddate.month)[1]
				if olddate.month != newdate.month and olddate.day != lastday:
					newdate = date(olddate.year, olddate.month, lastday)
				elif olddate.month != newdate.month and olddate.day == lastday:
					newdate = date(newdate.year, newdate.month, 1)
		
		#elif buf == "m":
			#self.selmode = (self.selmode + 1) % 3
		elif buf == "t":
			newdate = datetime.now()
			
		
		else:
			super().on_key(c, buf)
		self.set_date(newdate.year, newdate.month, newdate.day)
