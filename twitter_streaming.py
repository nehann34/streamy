from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import threading
import json
import time

REPORT_FREQUENCY_IN_MIN = 0.1
WINDOW_SIZE_IN_MIN = 0.2
#Variables that contains the user credentials to access Twitter API 
access_token = "2717892802-5YpJgPK4XyoTt0fTyz8h7yduYIrsyg2Goc7h0dD"
access_token_secret = "De9d0WAfIvi966PKWjrvdwt9ccCs3Yd846p3FiYpfDcAf"
consumer_key = "LkFkdnjA2GoXrUShct4Ufvhsa"
consumer_secret = "tSlzkwAe8co1P75Npvybg0KkCcio9plnLnoKCa1s8clfjZdt2Z"

bufferLock = threading.Lock()
buffer = []
users = {}
#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        d = json.loads(data)
        d["received_time"] = time.time()
        with bufferLock:
            buffer.append(d)
            print("Got -> ", d["user"]["name"], d["text"], d["received_time"])
        #print (json.dumps(d))
        return True

    def on_error(self, status):
        print status


def sanitize(thresholdTime):
    print ("Sanitizing")
    with bufferLock:
        while len(buffer) > 0: 
            data = buffer[0]
            if data["received_time"] >= thresholdTime - WINDOW_SIZE_IN_MIN * 60:
                break
            print("Clearing for", data["received_time"])
            users[data["user"]["name"]] -=1
            buffer.pop(0)
        # updating with new values
        i = len(buffer) - 1
        print("i = ", i)
        while(i >= 0):
            print(i)
            data = buffer[i]
            if data["received_time"] >= thresholdTime:
                i -=1
                continue
            elif data["received_time"] < thresholdTime - (REPORT_FREQUENCY_IN_MIN * 60):
                break
            if data["user"]["name"] in users.keys():
                print("updating user", data["user"]["name"], data["text"], data["received_time"])
                users[data["user"]["name"]] += 1
            else:
                print ("Creating user", data["user"]["name"], data["text"], data["received_time"])
                users[data["user"]["name"]] = 1
            i -=1


def generateReport1():
    print("Report1")
    for k, v in users.items():
        if v == 0:
            print("Deleting user", k)
            del users[k]
        else:
            print(k, v)
        
def generateReport2():
    pass

def generateReport3():
    pass

def generateReport():
    startTime = time.time()
    endTime = startTime + (REPORT_FREQUENCY_IN_MIN * 60)
    print("startTime", startTime, "endTime", endTime)
    while True:
        while time.time() < endTime:
            pass
        print("Timer ends")
        startTime = endTime
        endTime += REPORT_FREQUENCY_IN_MIN * 60
        
        sanitize(startTime)
        generateReport1()
        generateReport2()
        generateReport3()
        print("startTime", startTime, "endTime", endTime)

        


if __name__ == '__main__':

    #This handles Twitter authetication and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    #kw= raw_input("Enter a keyword to be searched!!!")
    #This line filter Twitter Streams to capture data by the keywords: kw


    reportGeneratorThread = threading.Thread(target = generateReport, name = "reportGeneratorThread")
    reportGeneratorThread.start()

    stream.filter(track=['modi'])
    print ("Here")
