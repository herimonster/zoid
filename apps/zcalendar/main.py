import zapp
import zcalendar
import zweekview
import ztable
import zutils
import zlabel

import zquerybox
import zdialogbox

import datetime
import gcalendar
import dateutil.parser
from dateutil.relativedelta import relativedelta

HELP_STR= "n: New event,  d: Delete event,  t: show today,  r: refresh | Arrows: select day/week,  Shift+Arrows: select month/event"

class ztest(zapp.zapp):
	
	def on_date_change(self, year, month, day):
		self.year = year
		self.month = month
		self.day = day
		self.zw.set_date(year, month, day)
	
	def on_highlight_day(self, year, month, day):
		events = self.gcal.get_month_data(year, month)
		
		if len(events[day])>0:
			return zutils.CL_BLUE, zutils.CL_BG, zutils.AT_BOLD
		return zutils.CL_FG, zutils.CL_BG, zutils.AT_NORMAL
	
	def on_get_calendar_data(self, year, month, day):
		events = self.gcal.get_month_data(year, month)
		return events[day]
	
	def on_select_event(self, e, startdate, enddate):
		self.sel_event = e 
		zutils.debug(repr(e))
		self.zt.head[0]['caption'] = e['summary']
		if isinstance(startdate, datetime.datetime):
			self.zt.rows = [["Start: " + startdate.strftime("%d.%m.%Y %H:%M")], ["End:   " + enddate.strftime("%d.%m.%Y %H:%M")]]
		elif isinstance(startdate, datetime.date):
			self.zt.rows = [["Start: " + startdate.strftime("%d.%m.%Y")], ["End:   " + enddate.strftime("%d.%m.%Y")]]
	
	def set_update(self, do_update):
		self.zw.do_update = do_update
		self.zc.do_update = do_update
	
	def querybox(self, caption, query):
		self.render()
		self.set_update(False)
		out, buf = zquerybox.query(self, caption, query)
		self.set_update(True)
		return out, buf
	
	def dialogbox(self, caption, query, answers):
		self.render()
		self.set_update(False)
		out, buf = zdialogbox.query(self, caption, query, answers)
		self.set_update(True)
		return out, buf
	
	def create_event(self):
		startdated = None
		while not startdated:
			startdate, _ = self.querybox("Start date", "Enter start date, leave empty for " + datetime.date(self.year, self.month, self.day).strftime("%d.%m.%Y")+".")
			
			if startdate == None:
				return None
			if startdate == "":
				startdated = datetime.date(self.year, self.month, self.day)
			else:
				try:
					startdated = dateutil.parser.parse(startdate, parserinfo = dateutil.parser.parserinfo(True, False)).date()
				except Exception as e:
					self.zl.set_caption(str(e))
					pass
		
		self.zl.set_caption(startdated.strftime("%d.%m.%Y"))
		
		starttimed = None
		while not starttimed:
			starttime, _ = self.querybox("Start time", "Enter start time, leave empty for whole day event.")
			if starttime == None:
				return None
			if starttime == "":
				break
			
			try:
				starttimed = dateutil.parser.parse(starttime, parserinfo = dateutil.parser.parserinfo(True, False))
				self.zl.set_caption(str(starttimed))
			except Exception as e:
				self.zl.set_caption(str(e))
				pass
		
		if starttimed:
			startd = datetime.datetime(startdated.year, startdated.month, startdated.day, starttimed.hour, starttimed.minute)
		else:
			startd = startdated
		
		if isinstance(startd, datetime.datetime):
			self.zl.set_caption(startd.strftime("%d.%m.%Y %H:%M"))
		else:
			self.zl.set_caption(startd.strftime("%d.%m.%Y"))
		
		enddated = None
		while not enddated:
			enddate, _ = self.querybox("End date", "Enter end date, leave empty for " + datetime.date(self.year, self.month, self.day).strftime("%d.%m.%Y")+".")
			if enddate == None:
				return None
			if enddate == "":
				enddated = datetime.date(self.year, self.month, self.day)
			else:
				try:
					enddated = dateutil.parser.parse(enddate, parserinfo = dateutil.parser.parserinfo(True, False)).date()
				except Exception as e:
					self.zl.set_caption(str(e))
					pass
		
		self.zl.set_caption( self.zl.get_caption() + " to " + enddated.strftime("%d.%m.%Y") )
		
		endtimed = None
		while starttimed and not endtimed:
			endtime, _ = self.querybox("End time", "Enter end time, leave empty for " + (starttimed + relativedelta(minutes = 30)).strftime("%H:%M") + "." )
			if endtime == None:
				return None
			if endtime == "":
				endtimed = (starttimed + relativedelta(minutes = 30))
			else:
				try:
					endtimed = dateutil.parser.parse(endtime, parserinfo = dateutil.parser.parserinfo(True, False))
				except Exception as e:
					self.zl.set_caption(str(e))
					pass
		
		if starttimed:
			endd = datetime.datetime(enddated.year, enddated.month, enddated.day, endtimed.hour, endtimed.minute)
		else:
			endd = enddated
		
		if isinstance(startd, datetime.datetime):
			self.zl.set_caption(startd.strftime("%d.%m.%Y %H:%M") + " to " + endd.strftime("%d.%m.%Y %H:%M"))
		else:
			self.zl.set_caption(startd.strftime("%d.%m.%Y") + " to " + endd.strftime("%d.%m.%Y") )
		
		
		summaryt = None
		while summaryt == None:
			summary, _ = self.querybox("Summary", "Enter a summary for the event." )
			if summary == None:
				return None
			elif summary != "":
				summaryt = summary
		
		if isinstance(startd, datetime.datetime):
			self.zl.set_caption(startd.strftime("%d.%m.%Y %H:%M") + " to " + endd.strftime("%d.%m.%Y %H:%M") + ": '"+summary + "'")
		else:
			self.zl.set_caption(startd.strftime("%d.%m.%Y") + " to " + endd.strftime("%d.%m.%Y")  + ": '"+summary + "'" )
		
		
		rec, _ = self.dialogbox("Recurrence", "Choose a recurrence.", ["None", "Weekly", "Bi-Weekly", "Monthly"])
		if rec == -1:
			return None
		
		self.gcal.create_event(startd, endd, summary, rec)
		self.gcal.get_month_data(startd.year, startd.month, force_refresh = True)
		if endd.year != startd.year or endd.month != startd.month:
			self.gcal.get_month_data(endd.year, endd.month, force_refresh = True)
		
		self.zl.set_caption(HELP_STR)
	
	def delete_event(self):
		if self.sel_event == None:
			return
		res, _ = self.dialogbox("Delete event?", "Delete event '"+self.sel_event["summary"] + "'?", ["No", "Yes"])
		if res == 1:
			self.gcal.delete_event(self.sel_event["id"])
			self.gcal.get_month_data(self.year, self.month, force_refresh = True)
			
		
	def do_run(self):
		
		self.gcal = gcalendar.GCalendar()
		
		self.sel_event = None
		
		r = self._root_frame
		
		r.set_catch_focus(False)
		
		d = datetime.datetime.now()
		self.year = d.year
		self.month = d.month
		self.day = d.day
		self.zc = zcalendar.zcalendar(r, (0,0), (27,9), d.year, d.month, d.day, zcalendar.SM_DAY)
		self.zw = zweekview.zweekview(r, (28,0), (r._size[0]-28, r._size[1]-1), d.year, d.month, d.day)
		self.zt = ztable.ztable(r, (0,10), (27, r._size[1]-10-1))
		self.zt.head[0]['caption'] = "Event"
		self.zl = zlabel.zlabel(r, (0, r._size[1]-1), (r._size[0], 1), HELP_STR)
		self.zl.set_attr(zutils.AT_DIM)
		
		self.zc.on_date_change = self.on_date_change
		self.zc.on_highlight_day = self.on_highlight_day
		
		self.zw.on_get_calendar_data = self.on_get_calendar_data
		self.zw.on_select_event = self.on_select_event
		
		r.add_child(self.zc)
		r.add_child(self.zw)
		r.add_child(self.zt)
		r.add_child(self.zl)
		
		while True:
			self.render()
			c, buf = self._get_char()
			
			if(c == zutils.KEY_ESC):
				break
			elif (c == zutils.KEY_LEFT or c == zutils.KEY_RIGHT):
				self.zc.on_key(c, buf)
			elif (c == zutils.KEY_SUP or c == zutils.KEY_SDOWN):
				self.zw.on_key(c, buf)
			elif (buf == "n"):
				#NEW EVENT!
				self.create_event()
			elif (buf == "d"):
				#DELETE EVENT!
				self.delete_event()
			elif (buf == "r"):
				#REFRESH EVENT!
				self.gcal.get_month_data(self.year, self.month, force_refresh = True)
				
			else:
				r.on_key(c, buf)


app = ztest()
app.run()
