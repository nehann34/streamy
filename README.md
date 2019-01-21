# Streamy
Uses Twitter Streaming API to track a given keyword and generate various reports about the tweets.

## Installation and Running
This works for python 3
Clone this repository and go the the streamy folder. Then do the following -
```
pip install -r requirements.txt
python twitter_streaming.py
```
After this follow the instruction in the program

## Tweaking
The code has two global variables for configuration
REPORT_FREQUENCY_IN_MIN - set this to control the report genaration frequency (default 1 min)
REPORT_WINDOW_IN_MIN  - set this to control the time window size for which the reports are generated (default 5 min)
