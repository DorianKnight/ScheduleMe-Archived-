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
        self.compareList = self.filterUserSchedule()
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

    def filterUserSchedule(self):
        #Create a list containing all of the event titles within the template list
        templateEventNames = []
        filteredUser = []
        for item in self.templateSchedule:
            title = item[0]
            templateEventNames.append(title)
        
        #Search for the template event names within the user schedule and append found lists to the filtered user schedule
        # for item in templateEventNames:
        #     for listItem in self.userSchedule:
        #         if item == listItem[0]:
        #             filteredUser.append(listItem)

        #Create a list where each index contains the template event and its user event counterpart
        for tItem in self.templateSchedule:
            for uItem in self.userSchedule:
                if tItem[0] == uItem[0]:
                    filteredUser.append([tItem,uItem])

        return filteredUser

    def correlationCoefficient(self):
        #This function follows the process written on the notion document to determine how similar both schedules are to eachother
        SSfit = 0.0
        SSmean = 0.0

        #Treat start time as y and duration as z while the individual discontinuous event represents x
        for pair in self.compareList:
            userStart = datetime.datetime.strptime(pair[1][1],"%H:%M")
            templateStart = datetime.datetime.strptime(pair[0][1],"%H:%M") 

            userDuration = pair[1][2]
            templateDuration = pair[0][2]

            ydiff = (userStart - templateStart).total_seconds()/3600
            zdiff = userDuration - templateDuration

            SSfit += pow(ydiff,2) + pow(zdiff,2)
        
        #Calculate the mean start time and duration within the template schedule
        #Then take the difference between the mean and each individual event on the user schedule

        n = len(self.compareList)
        #print(n)
        totalStartTime = 0.0
        zeroTime = datetime.datetime.strptime('00:00',"%H:%M")
        totalDuration = 0.0
        for item in self.compareList:
            startTime = datetime.datetime.strptime(item[0][1],"%H:%M")
            timeDelta = (startTime - zeroTime).total_seconds()/3600
            print(timeDelta)
            totalStartTime += timeDelta
            duration = item[0][2]
            totalDuration += duration

        averageStartTime = totalStartTime/n #This is the average hour that I have an event at
        averageDuration = totalDuration/n

        # print("Total start time: ", totalStartTime)
        # print("Average start time: ", averageStartTime)
        # print("Average duration: ", averageDuration)

        #Calculate the SSmean by finding the distance from each user schedule point to the average line on the template schedule    

        for userVal in self.compareList:
            userStart = datetime.datetime.strptime(userVal[1][1],"%H:%M")
            userDuration = userVal[1][2]

            timeDiff = averageStartTime - (userStart - zeroTime).total_seconds()/3600
            # print("\nAverage start time: ",averageStartTime)
            # print("User start time: ",userStart)
            # print("Time diff: ",timeDiff)
            durationDiff = averageDuration - userDuration

            SSmean += pow(timeDiff,2) + pow(durationDiff,2)
        
        corellationCoeff = (SSmean - SSfit)/SSmean
        print(SSmean)
        print(SSfit)

        return corellationCoeff



def main():
    Controller = Schedule()
    # print(Controller.userSchedule)
    # print(Controller.compareList)
    print("\n\n","Your correlation coefficient is",Controller.correlationCoefficient())

if __name__ == '__main__':
    main()