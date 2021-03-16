import re

from pybo import Text
def tokenize(s):
    return Text(s).tokenize_words_raw_text

def get_en_doc(s):
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    return nlp(s)

def get_nlp():
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    return nlp
    
# def en_tokenize(nlp, s):
#     return " ".join([t.text for t in nlp(s)])

def split_to_pieces_bo(s):
    sent_punc = "([།༎༑༏༐༒ ]+)"
    pattern = re.compile(sent_punc)
    pieces = []
    pieces_raw = re.split(pattern, s)
    assert(len(pieces_raw) % 2 == 1)
    for i in range(int((len(pieces_raw)-1)/2)):
        pieces.append((pieces_raw[2*i]+pieces_raw[2*i+1]).strip())
    if pieces_raw[-1].strip():
        pieces.append(pieces_raw[-1].strip())
    return pieces


nlp = get_nlp()

def remove_prefix(text, pattern):
    return re.sub(r'^{0}'.format(pattern), '', text)

def en_tokenize(s):
    return " ".join([t.text for t in nlp(s)])

def get_lines_en(en_text):
    lines = []
    for line_raw in en_text.split("\n"):
        line = remove_prefix(line_raw, "#+|>").strip()
        if line: lines.append(line)
    return lines

def split_shay_pieces(line):
    sents = []
    chunks = Chunks(line).make_chunks()
    if chunks[-1][0]!=105:
        t_tmp = chunks[-1]
        chunks[-1] = (105, t_tmp[1], t_tmp[0])
        print("Added punct: ", line)
    punct_positions = [(c[1], c[2]) for c in chunks if c[0]==105] # PUNCT==105
    if len(punct_positions) == 0 or punct_positions[0][0] != 0: punct_positions = [(0,0)] + punct_positions\

    for i in range(len(punct_positions)-1):
        sent = line[punct_positions[i][0]+punct_positions[i][1]:punct_positions[i+1][0]+punct_positions[i+1][1]]
        sents.append(sent.strip())
    return sents

from botok import Chunks
def get_sents_bo(bo_text):
    sents = []
    for line in bo_text.replace("\xa0", " ").split("\n"):
        if line:
            sents += split_shay_pieces(line)
    return sents


def lotsawa_en_line_filter(lines):
    if len(lines) < 2: return
    for i in [1,2,3]:
        if lines[i].lower().startswith("by "):
            del lines[i]
            break
    if "Bibliography" in lines:
        while True:
            del lines[-1]
            if lines[-1] == "Bibliography":
                del lines[-1]
                break
    if (lines[-1].startswith("Translated by") or lines[-1].startswith("| ")) and "translat" in lines[-1].lower():
        del lines[-1]
    else: print("Warning unremoved: "+lines[-1])
    return

def get_sents_en(en_text):
    sents = []
    lines = get_lines_en(en_text)
    lotsawa_en_line_filter(lines)
    for line in lines:
        doc = nlp(line)
        sents += [sent.text for sent in doc.sents if sent.text]
    return sents

def get_bo_url(url):
    tmp = url.split("/")
    bo_url = "/".join(tmp[:3] + ["bo"] + tmp[3:])
    return bo_url

def get_name_from_url(url):
    return "_".join(url.split("/")[3:])

def get_syl_distribution(bo_text):
    lens = []

    from botok import Chunks
    c = Chunks(bo_text)
    chunks = c.make_chunks()
    ct = 0
    from collections import Counter
    counter = Counter()
    for label, _ in c.get_readable(chunks):
        if label=="TEXT": ct+=1
        if label=="PUNCT":
            if ct > 0: counter[ct] += 1
            ct = 0
    return counter.most_common(10)


import requests
from bs4 import BeautifulSoup
import html2text
h = html2text.HTML2Text()
h.body_width = 0
h.ul_item_mark = ''
h.emphasis_mark = ''
h.strong_mark = ''

# put en url
def get_bitext_from_url(url):
    bo_url = get_bo_url(url)
    print("Processing: ", url, " ", bo_url)
    r = requests.get(bo_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    for div in soup.find_all(["div", 'a'], {'class':['footnotes', 'footnote']}): 
        div.decompose()
    bo_text = soup.select("#maintext")[0].text

    error_elem = soup.select("#maintext")[0].find("div", {"class": 'error'})
    if error_elem: bo_text = ''
    
    r = requests.get(url)   
    soup = BeautifulSoup(str(r.content, "utf-8").replace("\n", " "), 'html.parser')
    for div in soup.find_all(["div", 'a'], {'class':['footnotes', 'footnote']}): 
        div.decompose()
    for div in soup.find_all(["span"], {'class':['TibetanInlineEnglish']}): 
        div.decompose()
    en_text = h.handle(str(soup.select("#maintext")[0]))
    return en_text.strip(), bo_text.strip()

def save_bilingual_tokenized(url, dir="articles/"):
    en_text, bo_text = get_bitext_from_url(url)
    get_sents_en(en_text)
    lines = get_lines_en(en_text)
    fname = get_name_from_url(url)
    if en_text:
        with open(dir + fname+".en.stem", 'w') as f:
            for s in get_sents_en(en_text):
                f.write(en_tokenize(s)+"\n")
    if bo_text:
        with open(dir + fname+".bo.stem", 'w') as f:
            for s in get_sents_bo(bo_text):
                f.write(tokenize(s)+"\n")

def save_bilingual_plain(url, dir="articles_plain/"):
    en_text, bo_text = get_bitext_from_url(url)
    get_sents_en(en_text)
    lines = get_lines_en(en_text)
    fname = get_name_from_url(url)
    if en_text:
        with open(dir + fname+".en.stem", 'w') as f:
            for s in get_sents_en(en_text):
                f.write(s+"\n")
    if bo_text:
        with open(dir + fname+".bo.stem", 'w') as f:
            for s in get_sents_bo(bo_text):
                f.write(s+"\n")
    
# import markdown
# html = markdown.markdown(en_text)
# en_text = "".join(BeautifulSoup(html).findAll(text=True))