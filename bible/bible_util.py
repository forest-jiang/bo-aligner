import pandas as pd
import re
from common_util import *
from sklearn.model_selection import train_test_split

def is_verse(ind):
    return bool(re.match("^\d+:\d+$", ind.split(" ")[1]))

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def read_bible_sentences(file, only_verses = True):
    sents = pd.read_csv(file, index_col="index")
    if only_verses:
        sents = sents[sents.index.map(is_verse)]
    return sents


def get_chap(ind):
    return ind.split(":")[0]
def get_all_chaps(inds):
    return f7([ind.split(":")[0] for ind in inds if is_verse(ind)])

def sents_filter_chaps(sents, chaps_kept):
    return sents[sents.index.map(lambda x: x.split(":")[0] in chaps_kept)]

# ("\u0f0d");  // ། TIBETAN, DZONGKHA: SHAD
# ("\u0f0e");  // ༎ TIBETAN, DZONGKHA: NYIS SHAD
# ("\u0f11");  // ༑ TIBETAN, DZ.: RIN CHEN SPUNGS SHAD
# ("\u0f0f");  // ༏ DZONGKHA: TSCHEG SHAD
# ("\u0f10");  // ༐ DZONGKHA: NYIS TSCHEG SHAD
# ("\u0f12");  // ༒ DZONGKHA: RGYA GRAM SHAD
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

# sent_punc = "།༎༑༏༐༒ "
# pattern = re.compile("[^" + sent_punc + "]+" + "[" + sent_punc + " ]+")

# Write .stem file and .line files, return index for each line
def prepare_align_bo(sents, file_prefix, no_break_verse=False):
    stem_file = file_prefix + ".stem"
    line_file = file_prefix + ".line"
    sent_pieces, sent_pieces_ind, sent_pieces_tokenized = [], [], []
    chap = ""
    i_row = 0
    for i, row in sents.iterrows():
        chap, prev_chap = get_chap(i), chap
        if prev_chap and prev_chap != chap:
            sent_pieces.append("<p>")
            sent_pieces_ind.append("<p>")
            sent_pieces_tokenized.append("<p>")
    #     print(row.bo_text)
        if no_break_verse:
            sent_pieces.append(row.bo_text)
            sent_pieces_tokenized.append(tokenize(row.bo_text))
            sent_pieces_ind.append(i)
        else:
            for piece in split_to_pieces_bo(row.bo_text):
                piece_stripped = piece.strip()
                sent_pieces.append(piece_stripped)
                sent_pieces_tokenized.append(tokenize(piece_stripped))
                sent_pieces_ind.append(i)
        i_row += 1
        if (i_row % 1000) == 0: print("Rows processed...", i_row)

    with open(line_file, 'w') as f:
        for piece in sent_pieces:
            f.write(piece)
            f.write("\n")
    with open(stem_file, 'w') as f:
        for piece in sent_pieces_tokenized:
            f.write(piece)
            f.write("\n")

    return sent_pieces_ind

def prepare_align_en(sents, file_prefix, no_break_verse=False):
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
    nlp.add_pipe(nlp.create_pipe('sentencizer'))

    stem_file = file_prefix + ".stem"
    line_file = file_prefix + ".line"
    sent_pieces, sent_pieces_ind, sent_pieces_tokenized = [], [], []
    chap = ""
    i_row = 0
    for i, row in sents.iterrows():
        chap, prev_chap = get_chap(i), chap
        if prev_chap and prev_chap != chap:
            sent_pieces.append("<p>")
            sent_pieces_ind.append("<p>")
            sent_pieces_tokenized.append("<p>")
    #     print(row.bo_text)
        doc = nlp(row.en_text, disable=["tagger", "parser", "ner"])
        if no_break_verse:
            sent_pieces.append(doc.text)
            sent_pieces_tokenized.append(" ".join([t.text for t in doc]))
            sent_pieces_ind.append(i)
        else:
            for sent in doc.sents:
                sent_pieces.append(sent.text)
                sent_pieces_tokenized.append(" ".join([t.text for t in sent]))
                sent_pieces_ind.append(i)
        i_row += 1
        if (i_row % 1000) == 0: print("Rows processed...", i_row)

    with open(line_file, 'w') as f:
        for piece in sent_pieces:
            f.write(piece)
            f.write("\n")
    with open(stem_file, 'w') as f:
        for piece in sent_pieces_tokenized:
            f.write(piece)
            f.write("\n")
    return sent_pieces_ind



def write_ladder_file(ladder_file, index_bo, index_en, verse_index):
    verse_index_dict = {ind:i for i, ind in enumerate(verse_index)}
    i_bo, i_en = 0, 0  # Sentence piece index
    iv_bo, iv_en = -1, -1
    ladders = []
    ladders.append((i_bo, i_en))
    for iv, verse_name in enumerate(verse_index):
        # forward to the last i where the next row is greater than p_index
        while i_bo < len(index_bo) and verse_index_dict[index_bo[i_bo]] <= iv:
            i_bo += 1
        while i_en < len(index_en) and verse_index_dict[index_en[i_en]] <= iv:
            i_en += 1
        ladders.append((i_bo, i_en))
    with open(ladder_file, 'w') as f:
        for a,b in ladders:
            f.write("%d %d\n" % (b, a))