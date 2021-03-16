
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
    return spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
    
def en_tokenize(nlp, s):
    return " ".join([t.text for t in nlp(s)])
