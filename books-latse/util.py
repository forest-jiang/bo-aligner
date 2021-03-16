
tib =  "[\u0f00-\u0fda]"
shay = "[\u0f0d-\u0f0f]"
tsek = "[\u0f0b-\u0f0c]"
base = "[\u0f40-\u0f6c]"
addon = "[\u0f71-\u0fbc]"
no_shay_cons = "[ཀགཤ]"

from botok.text.tokenize import sentence_tok, word_tok
def tokenize_new(s):
    return " ".join( t.lemma if t.lemma else t.text for t in word_tok(s))

import re

from pybo import Text
def tokenize(s):
    return Text(s).tokenize_words_raw_text

# def get_nlp():
#     import spacy
#     nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
#     nlp.add_pipe('sentencizer')
#     return nlp

# nlp = get_nlp()

def remove_prefix(text, pattern):
    return re.sub(r'^{0}'.format(pattern), '', text)

# def en_tokenize(s):
#     return " ".join([t.text for t in nlp(s)])

from nltk.tokenize import word_tokenize, sent_tokenize

def en_tokenize(s):
    return " ".join(word_tokenize(s))

def en_get_sents(s):
    return sent_tokenize(s)


def post_process_sents(sents):
    new_sents = []
    one_sent = []
    for sent in sents:
        one_sent += sent[1]
        if sent[1][-1].chunk_type == "PUNCT":
            new_sents.append((len(one_sent), one_sent))
            one_sent = []
    if one_sent:
        new_sents.append((len(one_sent), one_sent))
    return new_sents

def bo_get_sents(s):
    sents = post_process_sents(sentence_tok(s))
    full_sents = []
    tokenized = []
    for i in range(len(sents)):
        toks = sents[i][1]
        if toks:
            tokenized.append( " ".join( t.lemma if t.lemma else t.text for t in toks).strip() )
            full_sents.append( s[toks[0].start:toks[-1].start+toks[-1].len].strip() )
    return tokenized, full_sents
    
    

def remove_p(lines):
    return list(filter(lambda x: x!="<p>", lines))

def rebuild_text(source, target, align, out, score_thres=0.0):
    with open(source,'r') as f:
        lines_s = f.read().split("\n") 
    with open(target,'r') as f:
        lines_t = f.read().split("\n")
    with open(align,'r') as f:
        lines_a = f.read().split("\n")

    prev_s, prev_t = -1, -1
    with open(out, 'w') as f:
        for line in lines_a:
            tmp = line.split("\t")
            if len(tmp) == 3:
                i_s, i_t, score = int(tmp[0]), int(tmp[1]), float(tmp[2])
                if score < score_thres: continue
                f.write("\n".join(remove_p(lines_s[prev_s+1:i_s+1]))+'\n')
                f.write("\n".join(remove_p(lines_t[prev_t+1:i_t+1]))+'\n')
                f.write("%f" % score+'\n')
                prev_s, prev_t = i_s, i_t
        f.write("\n".join(remove_p(lines_s[prev_s+1:]))+'\n')
        f.write("\n".join(remove_p(lines_t[prev_t+1:]))+'\n')
        f.write("%f" % score+'\n')

def rebuild_text_df(source, target, align, score_thres=0.0):
    with open(source,'r') as f:
        lines_s = f.read().split("\n") 
    with open(target,'r') as f:
        lines_t = f.read().split("\n")
    with open(align,'r') as f:
        lines_a = f.read().split("\n")

    prev_s, prev_t = -1, -1
    data = []
    for line in lines_a:
        tmp = line.split("\t")
        if len(tmp) == 3:
            i_s, i_t, score = int(tmp[0]), int(tmp[1]), float(tmp[2])
            if score < score_thres: continue
            s, t = " ".join(remove_p(lines_s[prev_s+1:i_s+1])), " ".join(remove_p(lines_t[prev_t+1:i_t+1]))
            if s and t:
                data.append((s,t, score))
            prev_s, prev_t = i_s, i_t
    s, t = " ".join(remove_p(lines_s[prev_s+1:])), " ".join(remove_p(lines_t[prev_t+1:]))
    if s and t:
        data.append((s, t, score))
    return data

def bo_to_sents(s):
    tokens = word_tok(s)   
    left = 0
    sents = []
    sents_stem = []
    for i in range(len(tokens)-1):
        if tokens[i].chunk_type == "PUNCT" and tokens[i+1].chunk_type != "PUNCT":
            sents_stem.append(" ".join( t.lemma if t.lemma else t.text for t in tokens[left:i+1]))
            sents.append("".join(t.text for t in tokens[left:i+1]))
            left = i+1
    sents_stem.append(" ".join( t.lemma if t.lemma else t.text for t in tokens[left:]))
    sents.append("".join(t.text for t in tokens[left:]))
    return sents_stem, sents


def prepare_intraparagraph(df, source, target):
    source_tok = source.replace(".txt", ".stem")
    target_tok = target.replace(".txt", ".stem")
    with open(source,'w') as f_s, open(source_tok, 'w') as f_st,open(target,'w') as f_t, open(target_tok, 'w') as f_tt:
        for i, row in df.iterrows():
            en_sents = en_get_sents(row['source'])
            bo_sents_tok, bo_sents = bo_get_sents(row["target"])
            if len(bo_sents_tok) == 1 or len(en_sents) == 1:
                continue
            f_s.write("\n".join(en_sents) + "\n<p>\n")
            f_st.write("\n".join(en_tokenize(s) for s in en_sents) + "\n<p>\n")
            f_t.write("\n".join(bo_sents) + "\n<p>\n")
            f_tt.write("\n".join(bo_sents_tok) + "\n<p>\n")


def prepare_intraparagraph_basic(df, source, target):
    source_tok = source.replace(".txt", ".stem")
    target_tok = target.replace(".txt", ".stem")
    with open(source,'w') as f_s, open(source_tok, 'w') as f_st,open(target,'w') as f_t, open(target_tok, 'w') as f_tt:
        for i, row in df.iterrows():
            en_sents = en_get_sents(row['source'])
            bo_sents_tok, bo_sents = bo_to_sents(row["target"])
            if len(bo_sents_tok) == 1 or len(en_sents) == 1:
                continue
            f_s.write("\n".join(en_sents) + "\n<p>\n")
            f_st.write("\n".join(en_tokenize(s) for s in en_sents) + "\n<p>\n")
            f_t.write("\n".join(bo_sents) + "\n<p>\n")
            f_tt.write("\n".join(bo_sents_tok) + "\n<p>\n")