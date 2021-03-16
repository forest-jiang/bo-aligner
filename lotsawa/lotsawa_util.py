# bible_util

from collections import defaultdict
from bs4 import BeautifulSoup
import requests, os

def get_first_href_check_dup(elem):
    a_tags = elem.select("a")
    if not a_tags: return ""
    ret = a_tags[0]['href']
    for a in a_tags[1:]:
        if a['href'] not in ret:
            print("Warning: uncaptured url: ", a['href'], " not in ", ret)
    return ret

def get_all_urls_from_one_topic(topic_url, host = "https://www.lotsawahouse.org"):
    tmp = []
    print("requesting...", topic_url)
    r = requests.get(topic_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    for t in soup.select('#content > div.index-container > ul.index-entry'):
        tmp.append((topic_url, host + get_first_href_check_dup(t)))
    return tmp

def process_one_url(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    # remove unwanted element
    for unwanted in soup.find_all("sup"):
        _ = unwanted.extract()
    pairs = []
    opening = ""
    opening_class = ""
    startings = {'TibetanExplanation', 'HeadingTib', 'TibetanVerse'}
    endings = {'Explanation', 'Heading3', 'EnglishText'}
    tags_no_class = []
    for t in soup.select("#maintext > p"):
        if 'class' not in t.attrs:
            if t.text.strip(): tags_no_class.append(str(t))
        else:
            classname = t['class'][0]
            if classname in endings and opening:
                pairs.append((opening, t.text, opening_class + "|" + classname))
                opening, opening_class = "", ""
            elif classname in startings:
                opening, opening_class = t.text, classname
    for i, tag_no_class in enumerate(tags_no_class):
        if i > 2: break
        print("No class??", tag_no_class[:30])

    if len(tags_no_class):
        print("No class tags: ", len(tags_no_class))

    print("Get %d pairs" % len(pairs))
    return pairs