from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import threading
import json
import time
import nltk
from urllib.parse import urlparse

# Variable to adjust the report frequency
REPORT_FREQUENCY_IN_MIN = 1
# Variable to set the report window size
REPORT_WINDOW_IN_MIN = 5

# Variables that contains the user credentials to access Twitter API 
access_token = "2717892802-5YpJgPK4XyoTt0fTyz8h7yduYIrsyg2Goc7h0dD"
access_token_secret = "De9d0WAfIvi966PKWjrvdwt9ccCs3Yd846p3FiYpfDcAf"
consumer_key = "LkFkdnjA2GoXrUShct4Ufvhsa"
consumer_secret = "tSlzkwAe8co1P75Npvybg0KkCcio9plnLnoKCa1s8clfjZdt2Z"

# Buffer that contains realtime tweet data
bufferLock = threading.Lock()
buffer = []

# Dictionaries to store data for
# various reports
users = {}
allUrls = {}
allWords = {}
totalNumberOfLinks = 0

# A set of stop words (commonly used words)
stopwords = set()
# This is a basic listener to receive tweets from tweepy.
class StdOutListener(StreamListener):

    def on_data(self, data):
        d = json.loads(data)
        # Adding local timestamp in incoming data
        d["received_time"] = time.time()
        # Only process tweet data
        if "user" not in d.keys():
            return True
        with bufferLock:
            # Produce the data at the end
            # of the buffer
            buffer.append(d)
        return True

    def on_error(self, status):
        print (status)

# Function to get a list of domains
# from a list of urls
def getAllDomains(urlList):
    allurls = []
    for u in urlList:
        domain = urlparse(u["expanded_url"])
        if len(domain.netloc) > 0:
            allurls.append(domain.netloc)
    return allurls

# Generic function to add a list to a dictionary
# where each element is a key in the dictionary
# and the dictionary stores the count of each key
def addToDict(elementsDict, elementsList):
    for i in elementsList:
        if i in elementsDict.keys():
            elementsDict[i] += 1
        else:
            elementsDict[i] = 1

# Generic function to substract a list from a dictionary
# where each element is a key in the dictionary
# and the dictionary stores the count of each key
def removeFromDict(elementsDict, elementsList):
    for i in elementsList:
        elementsDict[i] -=1
        if elementsDict[i] == 0:
            del elementsDict[i]
    
# Given a text and a list of ranges
# return a string which removes the substrings
# in the ranges
def filterString(text, ranges):
    if len(ranges) == 0:
        return text
    ret = ""
    prev = 0
    for range in ranges:
        ret += text[prev:range[0]]
        prev = range[1]
    ret += text[prev:]
    return ret

# Get all the relevant words
# excluding the commonly used words
def getAllRelevantWords(data):
    # A list to hold the starting and
    # ending incides of entities (links, media, etc)
    # in the tweet text 
    filterList = []
    for entity in data['entities']:
        for obj in data['entities'][entity]:
            filterList += obj['indices']

    text = data['text']
    # A list to hold the index ranges of
    # every entity in a list of tuples
    ranges = []
    j = 1
    while j < len(filterList):
        ranges += [(filterList[j-1], filterList[j])]
        j += 2
    
    # Sorting for easy filtering later
    ranges = sorted(ranges)
    # A text with all the entities removed
    text = filterString(text, ranges)
    return [word for word in filter(lambda w: len(w) > 1 and not w in stopwords,text.split())]

# Clear the data from the front of the buffer
# and consume the NEW data that arrived BEFORE
# thresholdTime (local timestamp)
def clearAndConsume(thresholdTime):
    global totalNumberOfLinks
    with bufferLock:
        # Clear the outdated data from the front of the
        # buffer and update the dictionaries storing
        # reports accordingly
        while len(buffer) > 0: 
            data = buffer[0]
            if data["received_time"] >= thresholdTime - REPORT_WINDOW_IN_MIN * 60:
                break
            
            # Get all the relevant data from this tweet
            userName = data["user"]["name"]
            urls = getAllDomains(data["entities"]["urls"])
            words = getAllRelevantWords(data)
            totalNumberOfLinks -= len(urls)
            
            # Update the user data report
            removeFromDict(users, [userName])
            # Update the links data report
            removeFromDict(allUrls, urls)
            # Update the words data report
            removeFromDict(allWords, words)
            # Delete the data from the buffer
            buffer.pop(0)
        
        # Consume the new data from the end of the queue
        # and update the dictionaries storing
        # the reports accordingly
        i = len(buffer) - 1
        while(i >= 0):
            data = buffer[i]
            if data["received_time"] >= thresholdTime:
                i -=1
                continue
            elif data["received_time"] < thresholdTime - (REPORT_FREQUENCY_IN_MIN * 60):
                break
            # Get all the relevant data from this tweet
            userName = data["user"]["name"]
            urls = getAllDomains(data["entities"]["urls"])
            words = getAllRelevantWords(data)
            totalNumberOfLinks += len(urls)

            # Update the user data report
            addToDict(users, [userName])
            # Update the links data report
            addToDict(allUrls, urls)
            # Update the words data report
            addToDict(allWords, words)
            i -=1

# Print the user report
def printUserReport():
    print("\t", "User Report")
    for k in users.keys():
        print("\t\t", k, users[k])

# Print the links report      
def printLinksReport():
    print("\t", "Links Report")
    print("\t", "Total number of urls:", totalNumberOfLinks)
    sortedByValue = sorted(allUrls.items(), key=lambda kv: kv[1], reverse = True)
    for k in sortedByValue:
        print("\t\t", k)

# Print the words report
def printWordsReport():
    print("\t", "Content Report")
    sortedByValue = sorted(allWords.items(), key=lambda kv: kv[1], reverse = True)
    print("\t", "Total unique words:", len(sortedByValue))
    for i in range(10):
        if i >= len(sortedByValue):
            break
        print("\t\t", sortedByValue[i])

# The function which generates
# report after every REPORT_FREQUENCY_IN_MIN
def generateReport():
    startTime = time.time()
    endTime = startTime + (REPORT_FREQUENCY_IN_MIN * 60)
    counter = 1
    while True:
        while time.time() < endTime:
            pass
        startTime = endTime
        endTime += REPORT_FREQUENCY_IN_MIN * 60
        
        # Update the old reports
        clearAndConsume(startTime)
        # Print all the reports
        print("Report number:", counter)
        printUserReport()
        printLinksReport()
        printWordsReport()
        counter += 1

        


if __name__ == '__main__':

    #This handles Twitter authetication and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    # Downloading stopwords
    nltk.download('stopwords')
    stopWordsList = nltk.corpus.stopwords.words('english')
    capitals = []
    for word in stopWordsList:
        capitals.append(word.capitalize())
    stopWordsList += capitals

    stopwords = set(stopWordsList)

    keyWord= input("Enter a keyword to be searched for reports: ")
    #This line filter Twitter Streams to capture data by the keywords: kw

    # Starting the consumer thread
    reportGeneratorThread = threading.Thread(target = generateReport, name = "reportGeneratorThread")
    reportGeneratorThread.start()

    # A blocking call that runs the producer thread which
    # consumes data from twitter and populates the buffer
    stream.filter(track=[keyWord])
