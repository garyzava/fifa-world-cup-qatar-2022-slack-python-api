# fifa-world-cup-qatar-2022-slack-python-api
 Python script that reads data from the FIFA's API for World Cup Qatar 2022, then post the data on a slack channel through a slack bot (slack app).

## Overview

* [Disclaimer](#disclaimer)
* [Slack App](#slack-app)
* [Installation](#installation)
* [Usage](#usage)
* [Test](#test)
* [Credits And Useful Resources](#credits-and-useful-resources)

## Disclaimer
 Use it at your own risk. I am not responsible for any damage caused by this script. The script assumes that the FIFA API uses the UTC+0 timezone, gmtime() function is used to convert the date to UTC+0 timezone.

## Slack App
Create a bot following the twilio guide below, follow only the slack guide. 

## Installation
Run pip install to install the project, do not use install setup.py.
```python
pip install .
```
Create a subfolder 'env' and a file .env to store your slack bot token.
```python
#Slack Credentials
SLACK_BOT_TOKEN='xoxb-****'
```

## Usage
Create a cron job or a windows task to run the notifier.py every minute.

Example to run it from linux environments:
```python
cd [path_to_your_directory] && source [virtualenv_name]/bin/activate && python notifier.py >> ./notifier.log
```

## Test
The notifier-test.py has the code changed to run a backtest from a match from the 2018 world cup. It uses the wordcipData-test.json which contains a match between Uruguay and Fracen.
```python
cd [path_to_your_directory] && source [virtualenv_name]/bin/activate && python notifier-test.py
```

## Credits And Useful Resources:
* Worldcup Slack Bot in PHP https://github.com/j0k3r/worldcup-slack-bot/blob/master/worldCupNotifier.php
* Building a World Cup Bot with Python, Twilio SMS and Slack https://www.twilio.com/blog/2018/07/building-a-world-cup-bot-with-python-twilio-sms-and-slack.html
