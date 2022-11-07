import spacy

# Load English tokenizer, tagger,
# parser, NER and word vectors
nlp = spacy.load("en_core_web_trf")

# Process whole documents
text = ("If Website or any of the resources it makes available are illegal in your locality, DO NOT USE WEBSITE.")

doc = nlp(text)

# Token and Tag
for token in doc:
    print(token, token.pos_)

# You want list of Verb tokens
#print("Verbs:", [token.text for token in doc if token.pos_ == "VERB"])
