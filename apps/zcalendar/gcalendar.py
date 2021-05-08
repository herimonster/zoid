import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dateutil.relativedelta import relativedelta
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
import zutils
import calendar
import datetime
import dateutil.parser
from tzlocal import get_localzone

import pickle

class GCalendar:
	def __init__(self):
		
		self.creds = None
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists('token.json'):
			self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
		# If there are no (valid) credentials available, let the user log in.
		if not self.creds or not self.creds.valid:
			if self.creds and self.creds.expired and self.creds.refresh_token:
				self.creds.refresh(Request())
			else:
				self.flow = InstalledAppFlow.from_client_secrets_file(
					'credentials.json', SCOPES)
				self.creds = self.flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open('token.json', 'w') as token:
				token.write(self.creds.to_json())
		
		self.service = build('calendar', 'v3', credentials=self.creds)
		
		calendars_result = self.service.calendarList().list().execute()
		
		self.calendars = calendars_result.get('items', [])
		
		self.calendars = [cal for cal in self.calendars if not "group.v.calendar.google.com" in cal['id']]
		
		
		try:
			self.eventcache = pickle.load(open("cache.p", "rb"))
		except:
			self.eventcache = {}
		
	def get_month_data(self, year, month, force_refresh = False):
		if (year, month) in self.eventcache and not force_refresh:
			zutils.debug("Using cached data for "+str(year)+"/"+str(month))
			return self.eventcache[(year,month)]
		# Call the Calendar API
		zutils.debug("Retreiving new data for "+str(year)+"/"+str(month))
		start = datetime.datetime(year, month, 1, 0, 0, 0)
		end = start + relativedelta(months=1)
		startt = start.isoformat() + 'Z' # 'Z' indicates UTC time
		endt = end.isoformat() + 'Z' # 'Z' indicates UTC time
		
		events = []
		for cal in self.calendars:
			events_result = self.service.events().list(calendarId=cal['id'], timeMin=startt,
												timeMax=endt, singleEvents=True,
												orderBy='startTime').execute()
			new_events = events_result.get('items', [])
			if new_events != None:
				events += new_events
		
		
		eventsofday = {}
		dayspermonth = calendar.monthrange(year, month)[1]
		for day in range(1, dayspermonth+1):
			eventsofday[day] = []
		for e in events:
			start = e['start'].get('dateTime', e['start'].get('date'))
			end = e['end'].get('dateTime', e['start'].get('date'))
			
			startdate = dateutil.parser.parse(start)
			enddate = dateutil.parser.parse(end)
			d = startdate.date()
			ed = enddate.date()
			
			while d <= ed:
				if d.year != year or d.month != month:
					d = d + relativedelta(days=1)
					continue
				eventsofday[d.day].append(e)
				d = d + relativedelta(days=1)
			
		self.eventcache[(year,month)] = eventsofday
		pickle.dump( self.eventcache, open( "cache.p", "wb" ) )
		return eventsofday

	def create_event(self, start, end, summary, recurrence):
		mytz = str(get_localzone())
		
		event = {
			'summary': summary,
		}
		
		if isinstance(start, datetime.datetime):
			event['start'] = {'dateTime': start.isoformat(), 'timeZone': mytz}
			event['end'] = {'dateTime': end.isoformat(), 'timeZone': mytz}
		else:
			event['start'] = {'date': start.isoformat(), 'timeZone': mytz}
			event['end'] = {'date': end.isoformat(), 'timeZone': mytz}
		
		if recurrence == 1:
			event['recurrence'] = ["RRULE:FREQ=DAILY"]
		elif recurrence == 2:
			event['recurrence'] = ["RRULE:FREQ=WEEKLY"]
		elif recurrence == 3:
			event['recurrence'] = ["RRULE:FREQ=WEEKLY;INTERVAL=2"]
		elif recurrence == 4:
			event['recurrence'] = ["RRULE:FREQ=MONTHLY"]
		event_result = self.service.events().insert(calendarId='primary', body=event).execute()
		return event_result
	
	def delete_event(self, eid):
		event_result = self.service.events().delete(calendarId='primary', eventId=eid).execute()
		return event_result
