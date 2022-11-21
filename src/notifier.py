# write a slack bot to post world cup updates

import os
import time
import json
import requests
import math
import dateutil.parser
from requests import Request, Session

import dateutil.parser

from dotenv import load_dotenv

import slack
from pathlib import Path

env_path = './env/.env'
load_dotenv(dotenv_path=env_path)

# constants
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_CLIENT = slack.WebClient(token = SLACK_BOT_TOKEN)

#Change your slack channel name here
SLACK_CHANNEL="#gary-test"

#set the timezone to be the same as the in the FIFA API:
os.environ['TZ'] = 'UTC'
#time.tzset()
# FIFA API 2018 CONSTANTS
FIFA_API_URL = "https://api.fifa.com/api/v3/"
ID_COMPETITION = 17
#FIFA World Cup Russia 2018-> ID_SEASON = 254645 
#FIFA World Cup Qatar 2022-> ID_SEASON = 255711
ID_SEASON = 255711 

# Match Statuses
MATCH_STATUS_FINISHED = 0
MATCH_STATUS_NOT_STARTED = 1
MATCH_STATUS_LIVE = 3
MATCH_STATUS_PREMATCH = 12
# Event Types
EVENT_GOAL = 0
EVENT_YELLOW_CARD = 2
EVENT_STRAIGHT_RED = 3
EVENT_SECOND_YELLOW_CARD_RED = 4
EVENT_PERIOD_START = 7
EVENT_PERIOD_END = 8
EVENT_END_OF_GAME = 26
EVENT_OWN_GOAL = 34
EVENT_FREE_KICK_GOAL = 39
EVENT_PENALTY_GOAL = 41
EVENT_PENALTY_SAVED = 60
EVENT_PENALTY_CROSSBAR = 46
EVENT_PENALTY_MISSED = 65
EVENT_FOUL_PENALTY = 72
# Periods
PERIOD_1ST_HALF = 3
PERIOD_2ND_HALF = 5
PERIOD_1ST_ET = 7
PERIOD_2ND_ET = 9
PERIOD_PENALTY = 11
# Language
LOCALE = 'en-GB'

DATA_FILE = './data/worldCupData.json'

language = { 'en-GB': [
   'The match between',
   'is about to start',
   'Yellow card',
   'Red card',
   'Own goal',
   'Penalty',
   'GOOOOAL',
   'Missed penalty',
   'has started',
   'HALF TIME',
   'FULL TIME',
   'has resumed',
   'END OF 1ST ET',
   'END OF 2ND ET',
   'End of penalty shoot-out'
   ]}

def post_to_slack_gz(channel, body=None, attachment_text=None):
   SLACK_CLIENT.chat_postMessage(channel=channel, text=body, attachments=[{"text": attachment_text}], as_user=True) 

def get_url(url, do_not_use_etag=False):

   proxies = dict()
   s = Session()
   req = Request('GET', url)
   prepped = s.prepare_request(req)

   resp = s.send(prepped,
                 proxies=proxies,
                 timeout=10,
                 verify=False
                 )

   if resp.status_code == requests.codes.ok:
       content = resp.text

       if len(content.strip()) == 0:
              return False
       return content
   else:
       print(resp.status_code, resp.content)

def get_all_matches():
   return json.loads(get_url(f'{FIFA_API_URL}calendar/matches?idCompetition={ID_COMPETITION}&idSeason={ID_SEASON}&count=500&language={LOCALE}'))


def get_player_alias(player_id):

   resp = json.loads(get_url(f'{FIFA_API_URL}players/{player_id}', False))

   return resp["Alias"][0]["Description"]

def save_to_json(file):
   with open(DATA_FILE, 'w') as f:
       json.dump(file, f)

def microtime(get_as_float=False):
   """Return current Unix timestamp in microseconds."""
   gmt_unixtime = time.mktime(time.gmtime())
   if get_as_float:
       #return time.time()
       return gmt_unixtime
   else:
       x, y = math.modf(gmt_unixtime)
       #x, y = math.modf(time.gmtime())
       return f'{x} {y}'

# Let’s grab the data we have on our json file:
DB = json.loads(open(DATA_FILE).read())
resp = get_all_matches()

matches = {}

if resp != 'null':
   matches = resp.get("Results")

# Find live matches and update score
for match in matches:

   if match.get('MatchStatus') == MATCH_STATUS_LIVE and match.get("IdMatch") not in DB["live_matches"]:
       DB["live_matches"].append(match["IdMatch"])

       DB[match["IdMatch"]] = {
           'stage_id': match["IdStage"],
           'teamsById': {
               match["Home"]["IdTeam"]: match["Home"]["TeamName"][0]["Description"],
               match["Away"]["IdTeam"]: match["Away"]["TeamName"][0]["Description"]
           },
           'teamsByHomeAway': {
               'Home': match["Home"]["TeamName"][0]["Description"],
               'Away': match["Away"]["TeamName"][0]["Description"]
           },
           'last_update': microtime()
       }
       # send slack message about the match starting
       post_to_slack_gz(SLACK_CHANNEL, f'{language[LOCALE][0]} {match["Home"]["TeamName"][0]["Description"]} vs. {match["Away"]["TeamName"][0]["Description"]} {language[LOCALE][1]}!')

   if match["IdMatch"] in DB["live_matches"]:
       # update score
       DB[match["IdMatch"]]["score"] = f'{match["Home"]["TeamName"][0]["Description"]} {match["Home"]["Score"]} - {match["Away"]["Score"]} {match["Away"]["TeamName"][0]["Description"]} '
   # save to file to avoid loops
   save_to_json(DB)


live_matches = DB["live_matches"]
for live_match in live_matches:
   for key, value in DB[live_match].items():
       if not DB.get(live_match):
           continue
       home_team_name = DB[live_match]['teamsByHomeAway']["Home"]
       away_team_name = DB[live_match]['teamsByHomeAway']["Away"]
       last_update_secs = DB[live_match]["last_update"].split(" ")[1]

       # retrieve match events
       response = json.loads(get_url(
           f'{FIFA_API_URL}timelines/{ID_COMPETITION}/{ID_SEASON}/{DB[live_match]["stage_id"]}/{live_match}?language={LOCALE}'))
       # in case of 304
       if response is None:
           continue
       events = response.get("Event")
       for event in events:
           event_type = event["Type"]
           period = event["Period"]
           #event_timestamp = event_timestamp = dateutil.parser.parse(event["Timestamp"])
           event_timestamp = dateutil.parser.parse(event["Timestamp"])

           event_time_secs = time.mktime(event_timestamp.timetuple())

           if event_time_secs > float(last_update_secs):
           #if 1==1:
               match_time = event["MatchMinute"]
               _teams_by_id = DB[live_match]['teamsById']
               for key, value in _teams_by_id.items():           
                   try:
                    if key == event["IdTeam"]:
                        event_team = value
                    else:
                        event_other_team = value                
                   except:
                       event_other_team = value
                       pass                    
                   #if key == event["IdTeam"]:
                   #    event_team = value
                   #else:
                   #    event_other_team = value
               event_player_alias = None
               score = f'{home_team_name} {event["HomeGoals"]} - {event["AwayGoals"]} {away_team_name}'
               subject = ''
               details = ''
               interesting_event = True

               if event_type == EVENT_PERIOD_START:
                   if period == PERIOD_1ST_HALF:
                       subject = f'{language[LOCALE][0]} {home_team_name} vs. {away_team_name} {language[LOCALE][8]}!'

                   elif period == PERIOD_2ND_HALF or period == PERIOD_1ST_ET or period == PERIOD_2ND_ET or period == PERIOD_PENALTY:
                       subject = f'{language[LOCALE][0]} {home_team_name} vs. {away_team_name} {language[LOCALE][11]}!'

               elif event_type == EVENT_PERIOD_END:
                   if period == PERIOD_1ST_HALF:
                       subject = f'{language[LOCALE][9]} {score}'
                       details = match_time
                   elif period == PERIOD_2ND_HALF:
                       subject = f'{language[LOCALE][10]} {score}'
                       details = match_time
                   elif period == PERIOD_1ST_ET:
                       subject = f'{language[LOCALE][12]} {score}'
                       details = match_time
                   elif period == PERIOD_2ND_ET:
                       subject = f'{language[LOCALE][13]} {score}'
                       details = match_time
                   elif period == PERIOD_PENALTY:
                       subject = f'{language[LOCALE][13]} {score} ({event["HomePenaltyGoals"]} - {event["AwayPenaltyGoals"]})'
                       details = match_time


               elif event_type == EVENT_GOAL or event_type == EVENT_FREE_KICK_GOAL or event_type == EVENT_PENALTY_GOAL:
                   event_player_alias = get_player_alias(event["IdPlayer"])
                   subject = f'{language[LOCALE][6]} {event_team}!!!'
                   details = f'{event_player_alias} ({match_time}) {score}'

               elif event_type == EVENT_OWN_GOAL:
                   event_player_alias = get_player_alias(event["IdPlayer"])
                   subject = f'{language[LOCALE][4]} {event_team}!!!'
                   details = f'{event_player_alias} ({match_time}) {score}'

               # cards

               elif event_type == EVENT_YELLOW_CARD:
                   event_player_alias = get_player_alias(event["IdPlayer"])
                   subject = f'{language[LOCALE][2]} {event_team}'
                   details = f'{event_player_alias} ({match_time})'


               elif event_type == EVENT_SECOND_YELLOW_CARD_RED or event_type == EVENT_STRAIGHT_RED:
                   event_player_alias = get_player_alias(event["IdPlayer"])
                   subject = f'{language[LOCALE][3]} {event_team}'
                   details = f'{event_player_alias} ({match_time})'


               elif event_type == EVENT_FOUL_PENALTY:
                   subject = f'{language[LOCALE][5]} {event_other_team}!!!'

               elif event_type == EVENT_PENALTY_MISSED or event_type == EVENT_PENALTY_SAVED:
                   event_player_alias = get_player_alias(event["IdPlayer"])
                   subject = f'{language[LOCALE][7]} {event_team}!!!'
                   details = f'{event_player_alias} ({match_time})'

               elif event_type == EVENT_END_OF_GAME:
                   DB['live_matches'].remove(live_match)
                   del DB[live_match]
                   save_to_json(DB)
                   interesting_event = False

               else:
                   interesting_event = False
                   continue
                
               if interesting_event:
                   post_to_slack_gz(SLACK_CHANNEL, subject, details)
                   DB[live_match]['last_update'] = microtime()

               if not DB["live_matches"]:
                   DB["live_matches"] = []

save_to_json(DB)
exit(0)