# Google Calendar
# from __future__ import print_function
# import datetime
# import pickle
# import os.path
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

# import os
# import sys
# import time
# import pyttsx3
# import speech_recognition as sr
# import pytz
# import subprocess

# import json

# import system


#####
import speech_recognition as sr
import os
import sys
import re
import webbrowser
import smtplib
import requests
import subprocess
from pyowm import OWM
import youtube_dl
import vlc
import urllib
import urllib2
import json
from bs4 import BeautifulSoup as soup
from urllib2 import urlopen
import wikipedia
import random
from time import strftime



# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

# Speak back text to user
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
    engine.setProperty('rate', 175)
    engine.say(text)
    engine.runAndWait()

# Listen to user
def get_audio():
    # print("Ready to listen...")
    r = sr.Recognizer()
    with sr.Microphone(1) as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception" + str(e))
    
    # speak("Yes")
    print("Ready to listen...")
            
    return said.lower()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Say something...')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio).lower()
        print('You said: ' + command + '\n')
    #loop back to continue to listen for commands if unrecognizable speech is received
    except sr.UnknownValueError:
        print('....')
        command = myCommand();
    return command

def respond(audio):
    print(audio)
    for line in audio.splitlines():
        os.system("say " + audio)


def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone()
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "AM"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(":")[1]
                start_time = start_time + "PM"

            speak(event["summary"] + " at " + start_time)

def get_date(text):
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:
        year += 1
    
    if day < today.day and month == -1 and day != -1:
        month += 1

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") > 0:
                dif += 7 
        
        return today + datetime.timedelta(dif)

    if month == -1 or day == -1:
        return None

    return datetime.date(month=month, day=day, year=year)

# Change computer status (shutdown, sleep, restart)
def computer(text):
    if "set to" in text:
        response = "y"
    else:
        speak(f"Do you want to {phrase}?")
        response = get_audio()

    if response[0] == "y":
        if "sleep" in phrase:
            print("Attempting to sleep...")
            system.Window().sleep()
        elif "restart" in phrase:    
            print("Attempting to restart...")
            system.Window().restart()
        elif "shut down" in phrase or "turn off" in phrase:
            print("Attempting to shut down...")
            system.Window().shutdown()

        listen = False

# Change computer volume
def volume(text):
    if "get" in text:
        sys.tracebacklimit = -1
        speak("The current volume is " + system.Audio().getVolume())
    elif "mute" in text or "unmute" in text:
        system.Audio().toggleMute("unmute") if "unmute" in text else system.Audio().toggleMute("mute")
    else:
        text = text.replace("%", "").replace("the", "") # remove misc
        level = [i for i in text.split() if i.isdigit()][0] # extract volume level
        level = ("-" + level) if "lower" in text else level # switch signs
        
        if "by" in text:
            system.Audio().setVolume(pre="by",level=level)
        else:
            system.Audio().setVolume(pre="to",level=level)

# while True:
#     assistant(myCommand())

#     if 'open' in command:
#         reg_ex = re.search('open (.+)', command)
#         if reg_ex:
#             domain = reg_ex.group(1)
#             print(domain)
#             if "twitter" in command:
#                 domain = "twitter.com"
#             elif "facebook" in command:
#                 domain = "fb.com"
#             url = 'https://www.' + domain
#             webbrowser.open(url)
#             respond('Website has been opened.')
#         else:
#             pass


'''
WAKE = "serena"
SERVICE = authenticate_google()

listen = True
while listen:
    print("Initiate... Listening")
    text = get_audio()
    if text.count(WAKE) > 0:
        text = get_audio()

        CALENDAR_STRS = ["today", "plan", "planned", "plans",
                            "am i busy", "what do i have"]
        for phrase in CALENDAR_STRS:
            if phrase in text:
                date = get_date(text)
                if date:
                    get_events(get_date(text), SERVICE)
                else:
                    speak("I don't understand.")
                break

        NOTE_STRS = ["make a note", "write this down", "remind me", "listen to me"]
        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down?")
                txt = get_audio()
                note(txt)
                speak("I have just made a note.")
                break

        if "change brightness" in text or "lower brightness" in text:
            # Run system.screen.setBrightness()
            # num = [i for i in list(text) if i.isdigit()]
            # brightness = int("".join(num))
            # wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(brightness, 0)
            pass


        COMPUTER = ["sleep", "restart", "turn off", "shut down"]
        for phrase in COMPUTER:
            if phrase in text:
                computer(text)
                break
        

        VOLUME = ["change volume to", "change volume by", 
                  "lower volume to", "lower volume by",
                  "increase volume to", "increase volume by",
                  "get volume", "mute", "unmute"]
        for phrase in VOLUME:
            if phrase in text:
                volume(text)
                break
'''


if __name__ == '__main__':
    command = "open facebook"
    if 'open' in command:
        reg_ex = re.search('open (.+)', command)
        if reg_ex:
            domain = reg_ex.group(1)
            print(domain)
            if "twitter" in command:
                domain = "twitter.com"
            elif "facebook" in command:
                domain = "fb.com"
            url = 'https://www.' + domain
            webbrowser.open(url)
            respond('Website has been opened.')
        else:
            pass