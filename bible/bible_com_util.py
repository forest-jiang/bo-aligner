from collections import defaultdict
from bs4 import BeautifulSoup
import requests, os, re

def find_verse_idx(tag):
    if 'verse' in tag['class']:
        return tag['class'][1][1:]
    return ''

def find_tag_idx(tag):
    # is_verse, idx
    if 'content' in tag['class'] and 'verse' in tag.parent['class']:
        return True, find_verse_idx(tag.parent)
    if 'heading' in tag['class']:
        return False, tag.parent['class'][0]
    if 'body' in tag['class']:
        return False, 'note'
    return False, ''

def pre_process_lord(elem):
    for lord_elem in elem.select("span.nd"):
        tmp = list(lord_elem.select("span"))
        if not tmp or len(tmp) > 1 or tmp[0].text.upper().strip() != "LORD": print("Warning: should contain only one LORD span sub-tag", lord_elem)
        lord_elem.insert_before(tmp[0])
        _ = lord_elem.extract()


def process_intro(elem):
    out = []
    for h_tag in elem.select("h1"):
        out.append(("intro" + str(len(out)+1), h_tag.text))
    for t in elem.select("div.chapter div"):
        if t.text:
            out.append(("intro" + str(len(out)+1), t.text))
    return out
    
def process_chapter(elem):
    pre_process_lord(elem)
    outv = []
    outnv = []
    nv_indices = defaultdict(int) # how many are there
    for i, span in enumerate(elem.find_all("span", recursive=True)):
        if 'label' in span['class']:  # label means just a number "2"
            continue
        if 'body' in span.parent['class']:  # for note text
            continue
        if 'p' in span.parent['class']:  # There are div's under <p>
            continue
        text = span.text.strip()
        is_verse, idx = find_tag_idx(span)
        if text and idx:
            if is_verse:
                if len(outv) > 0 and outv[-1][0] == idx:
                    outv[-1] = (idx, outv[-1][1] + " " + text)
                else:
                    outv.append((idx, text))
            else:
                nv_indices[idx] += 1
                if nv_indices[idx] > 1:
                    outnv.append((idx + str(nv_indices[idx]), text))
                else:
                    outnv.append((idx, text))
    return outv + outnv
def process_chapter_url(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    next_link = soup.select("body a.bible-nav-button.nav-right")
    if 'INTRO' in url:
        return next_link, process_intro(soup.select("body div.reader")[0])
    return next_link, process_chapter(soup.select("body div.reader")[0])

def scrape_all_sentences(url):
    url_prefix = os.path.dirname(url)
    url_basename = os.path.basename(url)

    def get_index_prefix(url_basename):
        tmp = url_basename.split('.')
        return tmp[0] + " " + tmp[1] + ":"
    data = []
    try:
        while True:
            url = url_prefix + "/" + url_basename
            index_prefix = get_index_prefix(url_basename)
            print('Scraping... ' + url)
            next_link, sentences_one_chap = process_chapter_url(url)
            data += [[index_prefix+idx, text, url] for idx, text in sentences_one_chap]
            if len(next_link) > 0:
                next_chap = next_link[0]
                url_basename = next_chap['href'].split('/')[-1]
            else:
                print("Not found any more")
                break
    except:
        pass
    return data
