#Imports 
from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


#From quickstart guide and allows for successful set up of the client interface
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

try:
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + '-04:00'
    startOfDay = str(datetime.date.today())+'T00:00:00-04:00'
    endOfDay = str(datetime.date.today())+'T23:59:00-04:00'
except HttpError as error:
    print('An error occurred: %s' % error)

class Schedule:
    def __init__(self):
        self.templateSchedule = self.getTemplate()
        self.userSchedule = self.getUser()
    def getTemplate(self):
        rawData = self.getEventsList('utg1uq5vc83biaq2p9n9cqq32k@group.calendar.google.com')
        return self.FormatItems(rawData)
    def getUser(self):
        rawData = self.getEventsList('primary')
        return self.FormatItems(rawData)
    def getEventsList(self, address):
        #Uses the api client to retrieve the google calendar data
        apiEventReturnUser = service.events().list(calendarId=address,
                                               timeMin = startOfDay,
                                               timeMax = endOfDay,
                                               singleEvents = True,
                                               orderBy = 'startTime').execute()
        return apiEventReturnUser.get('items',[])
    
    def FormatItems(self,rawData):
        #Takes the calendaritem data and constructs a simplified list containing the event description, start time and duration
        schedule = []
        for item in rawData:
            if item['start'].get('dateTime') != "None":
                eventTitle = item['summary']
                eventStart = item['start'].get('dateTime')
                eventEnd = item['end'].get('dateTime')
                dtObjectEventStart = datetime.datetime.strptime(eventStart,"%Y-%m-%dT%H:%M:%S-04:00")
                formattedEventStart = dtObjectEventStart.strftime("%H:%M")
                dtObjectEventEnd = datetime.datetime.strptime(eventEnd,"%Y-%m-%dT%H:%M:%S-04:00")
                eventDuration = (dtObjectEventEnd - dtObjectEventStart).total_seconds()/3600
                #print(eventTitle)
                #print(dtObjectEventStart.strftime("%H:%M")+"\n")
                schedule.append([eventTitle, formattedEventStart, eventDuration])
        return schedule




def main():
    Controller = Schedule()
    print(Controller.userSchedule)

if __name__ == '__main__':
    main()