

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz
import re

#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================


#  NewsStory
class NewsStory(object):

    def __init__(self,guid,title,description,link,pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        return self.guid

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_link(self):
        return self.link

    def get_pubdate(self):
        return self.pubdate
#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        
        raise NotImplementedError

# PHRASE TRIGGERS


# PhraseTrigger
class PhraseTrigger(Trigger):
    '''
    abstract class word trigger
    '''
    def __init__(self, word):
        self.word = word

    def isPhraseIn(self, text):
        '''
        returns true if the whole word is present in text
        case insensitive and treating punctuation as spaces
        '''
        def remove_punc(str):
            new_str = str
            for char in new_str:
                if char in string.punctuation:
                    new_str = new_str.replace(char, ' ')
            return new_str

        # case insensitive for both words
        word = self.word.lower()
        haystack = remove_punc(text)
        haystack = haystack.lower()

        # get list of words to search
        haystack = haystack.split()
        text = ' '.join(haystack)

        def found(phrase, text):
            return re.search(r"\b{}\b".format(phrase), text, re.IGNORECASE)
        if found(word,text) != None:
            return True
        return False


class TitleTrigger(PhraseTrigger):
    def evaluate(self, story):
        return self.isPhraseIn(story.get_title())


# DescriptionTrigger
class DescriptionTrigger(PhraseTrigger):
    def evaluate(self,story):
        return self.isPhraseIn(story.get_description())
# TIME TRIGGERS

# 
# TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.
class TimeTrigger(Trigger):

    def __init__(self,time):
        format = '%d %b %Y %H:%M:%S'
        time = datetime.strptime(time,format)
        time = time.replace(tzinfo=pytz.timezone("EST"))
        self.time = time
# 
# BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
    def evaluate(self,story):
        return self.time > story.get_pubdate().replace(tzinfo=pytz.timezone("EST"))

class AfterTrigger(TimeTrigger):
    def evaluate(self,story):
        return self.time < story.get_pubdate().replace(tzinfo=pytz.timezone("EST"))

# COMPOSITE TRIGGERS


# NotTrigger
class NotTrigger(Trigger):

    def __init__(self,othertrigger):
        self.othertrigger = othertrigger

    def evaluate(self,story):
        return not self.othertrigger.evaluate(story)



#  AndTrigger
class AndTrigger(Trigger):
    def __init__(self,ftrig,strig):
        self.ftrig = ftrig
        self.strig = strig

    def evaluate(self,story):
        return self.ftrig.evaluate(story) and self.strig.evaluate(story)


# OrTrigger
class OrTrigger(Trigger):
    def __init__(self,ftrig,strig):
        self.ftrig = ftrig
        self.strig = strig

    def evaluate(self,story):
        return self.ftrig.evaluate(story) or self.strig.evaluate(story)

#======================
# Filtering
#======================


def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    # TODO: Problem 10
    # This is a placeholder
    # (we're just returning all the stories, with no filtering)
    rstories=[]
    for story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(story) == True:
                    rstories.append(story)
    return rstories



#======================
# User-Specified Triggers
#======================

def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)
    print(lines)
    
    # line is the list of lines that you need to parse and for which you need
    # to build triggers
    trig_dict = {}
    trig_list = []

    for i in range(len(lines)):
        trig = lines[i].split(',')
        if trig[1] == 'TITLE':
            trig_dict[trig[0]] = TitleTrigger(trig[2])
        elif trig[1] == 'DESCRIPTION':
            trig_dict[trig[0]] = DescriptionTrigger(trig[2])
        elif trig[1] == 'AFTER':
            trig_dict[trig[0]] = AfterTrigger(trig[2])
        elif trig[1] == 'BEFORE':
            trig_dict[trig[0]] = BeforeTrigger(trig[2])
        elif trig[1] == 'NOT':
            trig_dict[trig[0]] = NotTrigger(trig[2])
        elif trig[1] == 'AND':
            trig_dict[trig[0]] = AndTrigger(trig_dict[trig[2]],trig_dict[trig[3]])
        elif trig[0] == 'ADD':
            for i in range(1,len(trig)):
                x = trig[i]
                val = trig_dict[x]
                trig_list.append(val)

    return trig_list


SLEEPTIME = 120 #seconds -- how often we poll

def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        t1 = TitleTrigger("YES BANK")
        t2 = DescriptionTrigger("Trump")
        t3 = DescriptionTrigger("Clinton")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1, t4]

        
        # TODO: After implementing read_trigger_config, uncomment this line
        triggerlist = read_trigger_config('triggers.txt')

        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")

            # Get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://news.yahoo.com/rss/topstories"))

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()
