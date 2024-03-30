import json
import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
from werkzeug.datastructures import ImmutableMultiDict

SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDS_DIR = '.creds/'
CRED_FILE = CREDS_DIR + 'cred.json'
TOKEN_FILE = CREDS_DIR + 'token.json'
ACCOUNT_FILE = CREDS_DIR + 'account.json'
CREDS = None
SERVICE = None

with open(ACCOUNT_FILE) as account_file:
	account_data = json.load(account_file)
	account = account_data["account"]

calendar_id = account

def authentication():
	global CREDS, SERVICE
	if os.path.exists(TOKEN_FILE):
		CREDS = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
	if not CREDS or not CREDS.valid:
		if CREDS and CREDS.expired and CREDS.refresh_token:
			CREDS.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
			CREDS = flow.run_local_server(port=0)
	with open(TOKEN_FILE, "w") as token:
		token.write(CREDS.to_json())
	SERVICE = build("calendar", "v3", credentials=CREDS)

def send(event:'Event'):
	SERVICE.events().insert(calendarId=calendar_id, body=event.json).execute()

def color_info()->list[dict[str,str]]:
	colors = SERVICE.colors().get().execute()
	colors_dict = json.loads(json.dumps(colors))
	ans:dict[str,str] = dict()
	for colorId, colorInfo in colors_dict['event'].items():
		ans[str(colorId)] = colorInfo["background"]
	return ans

class Event:
	Keys = {"summary", "colorId", "location", "description", "start", "end", "reccurrence", "attendees", "reminders"}
	def __init__(self, jsondata:dict[str,str]=None) -> None:
		self.json:dict[str,str] = jsondata
	@classmethod
	def from_form(cls, form:ImmutableMultiDict)-> list['Event']:
		dict_data = dict()
		date = ("date" in form.keys())
		multi = ("multiple" in form.keys())
		if multi:
			events:list[Event] = []
			dict_data["colorId"] = '3'
			for key,item in form.items():
				# expected {'summary','colorId','location'}
				if key in Event.Keys:
					dict_data[key] = item
					continue
			try:
				key = "date_list"
				date_list:list[str] = form[key].split(',')
				for dl in date_list:
					# ValueError is raised
					datetime.datetime.strptime(dl, '%Y-%m-%d')

				if date:
					for dl in date_list:
						temp_data = dict_data.copy()
						temp_data["start"] = {
							"date" : dl,
							"timeZone" : "Asia/Tokyo"
						}
						temp_data["end"] = {
							"date" : dl,
							"timeZone" : "Asia/Tokyo"
						}
						events.append(Event(jsondata=temp_data.copy()))
				else:
					key = "start_time"
					item = form[key]
					item_start = datetime.datetime.strptime(item, "%H:%M")
					
					key = "end_time"
					item = form[key]
					item_end = datetime.datetime.strptime(item, "%H:%M")

					for dl in date_list:
						temp_data = dict_data.copy()
						temp_data["start"] = {
							"dateTime" : f"{dl}T{item_start.strftime('%H:%M:%S')}",
							"timeZone" : "Asia/Tokyo"
						}# RFC3339 format
						temp_data["end"] = {
							"dateTime" : f"{dl}T{item_end.strftime('%H:%M:%S')}",
							"timeZone" : "Asia/Tokyo"
						}
						events.append(Event(jsondata=temp_data.copy()))
			except KeyError:
				raise EventFormatError(field=key, statusinfo="Missing")
			except ValueError:
				raise EventFormatError(field=key, statusinfo="FormatError")
			return events
		else: # single event
			dict_data["colorId"] = '3'
			for key,item in form.items():
				# expected {'summary','clolorId','location'}
				if key in Event.Keys:
					dict_data[key] = item
					continue
			try:
				key = "event_date"
				item = form[key]
				# if the format is different, Valueerror is raised
				item_date = datetime.datetime.strptime(item, "%Y-%m-%d")
				if date:
					dict_data["start"] = {
						"date" : item_date.strftime('%Y-%m-%d'),
						"timeZone" : "Asia/Tokyo"
					}
					dict_data["end"] = {
						"date" : item_date.strftime('%Y-%m-%d'),
						"timeZone" : "Asia/Tokyo"
					}
				else:
					key = "start_time"
					item = form[key]
					item_start = datetime.datetime.strptime(item, "%H:%M")
					
					key = "end_time"
					item = form[key]
					item_end = datetime.datetime.strptime(item, "%H:%M")

					dict_data["start"] = {
						"dateTime" : f"{item_date.strftime('%Y-%m-%d')}T{item_start.strftime('%H:%M:%S')}",
						"timeZone" : "Asia/Tokyo"
					}# RFC3339 format
					dict_data["end"] = {
						"dateTime" : f"{item_date.strftime('%Y-%m-%d')}T{item_end.strftime('%H:%M:%S')}",
						"timeZone" : "Asia/Tokyo"
					}
			except KeyError:
				raise EventFormatError(field=key, statusinfo="Missing")
			except ValueError:
				raise EventFormatError(field=key, statusinfo="FormatError")
			return [Event(jsondata=dict_data)]
	def __str__(self):
		return self.json.__str__()
	def __repr__(self):
		return self.__str__()

class EventFormatError(Exception):
	StatusInfo = ["Invalid", "FormatError", "Blank", "Missing"]
	def __init__(self, message:str="", field:str="", status:int=0, statusinfo:str=None):
		super().__init__(message)
		self.message:str = message
		self.field:str = field
		self.status:int = status
		if statusinfo in EventFormatError.StatusInfo:
			self.status = EventFormatError.StatusInfo.index(statusinfo)
	
	def statusinfo(self):
		return EventFormatError.StatusInfo[self.status]

	def __str__(self):
		return f"{{{self.field}:{self.statusinfo()}}} {self.message}"

# auto run
authentication()