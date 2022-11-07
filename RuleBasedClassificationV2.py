import spacy
import re

nlp = spacy.load('en_core_web_trf')
from spacy.matcher import Matcher
matcher = Matcher(nlp.vocab)


permission_pattern = [
    # [9GAG, we, ...] may VERB and VERB  
    [ {"POS": {"IN": ["PROPN", "PRON"]}},
      {"LOWER": "may"},
      {"POS": "VERB"},
      {"LOWER": "and"},
      {"POS": "VERB"}
    ],
    # [PRON] is given the opportunity to
    [ {"POS": {"IN": ["PROPN", "PRON", "NOUN"]}},
      {"LOWER": {"IN": ["is", "offers"] }},
      {"LOWER": {"IN": ["given", "you"] }},
      {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["opportunity", "right"] }},
      {"LOWER": "to", "OP": "?"}
    ],
    # [NOUN, PRONOUN] may, [from time to time], VERB
    [ {"POS": {"IN": ["PROPN", "PRON", "NOUN"]}},
      {"LOWER": "may"},
      {"IS_PUNCT": True},
      {"LOWER": "from"},
      {"LOWER": "time"},
      {"LOWER": "to"},
      {"LOWER": "time"},
      {"POS": "VERB"}
    ],
    # [NOUN, PRON] has the authority to
    [ {"POS": {"IN": ["PROPN", "PRON", "NOUN"]}},
      {"LOWER": "also", "OP": "?"},
      {"LOWER": "has"},
      {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["authority", "right"]}},
      {"LOWER": "to", "OP": "?"}
    ],
    # [NOUN, PRONOUN] may provide
    [ {"POS": {"IN": ["PROPN", "PRON"]}},
      {"LOWER": "may"},
      {"LOWER": "also", "OP": "?"},
      {"LOWER": "provide"}
    ],
    # [NOUN, PRONOUN] can freely VERB
    [ {"POS": {"IN": ["NOUN"]}},
      {"LOWER": "can"},
      {"LOWER": "freely"}
    ],
    # NOUN can send a 
    [ {"POS": {"IN": ["NOUN"]}},
      {"LOWER": "can"},
      {"LOWER": "send"},
      {"LOWER": "a"}
    ],
    # You may start the
    [ {"LOWER": "you"},
      {"LOWER": "may"},
      {"LOWER": "start"},
      {"LOWER": "the"}
    ],
    # PROPN may collect information
    [ {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}},
      {"LOWER": "may"},
      {"LOWER": "collect"},
      {"LOWER": "information"}
    ],
    # PROPN may collect information
    [ {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}},
      {"LOWER": "may", "OP": "?"},
      {"LOWER": "allow"},
      {"LOWER": "you"},
      {"LOWER": "to"}
    ],
    # may be monitored by us
    [ {"LOWER": "may"},
      {"LOWER": "be"},
      {"LOWER": "monitored"},
      {"LOWER": "by"},
      {"LOWER": "us"}
    ],
    # in case... [SERVICES] may take actions
    [ {"LOWER": "in"},
      {"LOWER": "case"},
      {"LOWER": {"NOT_IN": ["may"]}, "OP": "*"},
      {"LOWER": "may"},
      {"LOWER": "take"},
      {"LOWER": {"NOT_IN": ["actions"]}, "OP": "*"},
      {"LOWER": "actions"}
    ],
    # you grant [PRON] the rights
    [ {"LOWER": "you"},
      {"LOWER": "grant"},
      {"POS": {"IN": ["PRON", "PROPN", "NOUN"]}},
      {"LOWER": "the"},
      {"LOWER": "rights"}
    ],
    # [PRON] may run marketing and promotional
    [ {"POS": {"IN": ["PRON"]}},
      {"LOWER": "may"},
      {"LOWER": "run"},
      {"LOWER": {"IN": ["marketing", "promotional"]}},
      {"LOWER": "and"},
      {"LOWER": {"IN": ["marketing", "promotional"]}, "OP": "?"}
    ],
    # PRON may share information
    [ {"POS": {"IN": ["PRON"]}},
      {"LOWER": "may"},
      {"LOWER": "share"},
      {"LOWER": {"NOT_IN": ["information"]}},
      {"LOWER": "information"}
    ],
    # account can be cancelled
    [ {"LOWER": "account"},
      {"LOWER": "can"},
      {"LOWER": "be"},
      {"LOWER": "cancelled"}
    ],
    # PROPN can be accessed
    [ {"POS": {"IN": ["PRON", "PROPN", "NOUN"]}},
      {"LOWER": "can"},
      {"LOWER": "be"},
      {"LOWER": "accessed"}
    ],
    # PROPN... may allow users to VERB
    [ {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}},
      {"LOWER": "may", "OP": "?"},
      {"LOWER": {"IN": ["allow", "allows"]}},
      {"LOWER": "users"},
      {"LOWER": "to"},
      {"POS": "VERB"}
    ],
    # you will .. be able to
    [ {"LOWER": "you"},
      {"LOWER": "will"},
      {"LOWER": {"NOT_IN": ["be"]}},
      {"LOWER": "be"},
      {"LOWER": "able"},
      {"LOWER": "to"}
    ],
    # you give us permission to
    [ {"LOWER": "you"},
      {"LOWER": "give"},
      {"LOWER": "us"},
      {"LOWER": "permission"},
      {"LOWER": "to"}
    ],
    # [9GAG, we, ...] may VERB you
    [ {"POS": {"IN": ["PROPN", "PRON", "NOUN"]}},
      {"LOWER": "may"},
      {"POS": "VERB"},
      {"LOWER": "you"}
    ],
    # you grant [PRON] the rights
    [ {"POS": {"IN": ["PROPN", "PRON", "NOUN"]}},
      {"LOWER": "will"},
      {"LOWER": "have"},
      {"LOWER": "the"},
      {"LOWER": "right"}
    ],
    # you grant [PRON] the rights
    [ {"LOWER": "we"},
      {"LOWER": "retain"},
      {"LOWER": "the"},
      {"LOWER": "right"},
      {"LOWER": "to"},
      {"POS": "VERB"}
    ],
    # you are allowing us to VERB
    [ {"LOWER": "you"},
      {"LOWER": "are"},
      {"LOWER": "allowing"},
      {"LOWER": "us"},
      {"LOWER": "to"},
      {"POS": "VERB"}
    ],
    # you may VERB your
    [ {"LOWER": "you"},
      {"LOWER": "may"},
      {"POS": "VERB"},
      {"LOWER": "your"}
    ],
    # [9GAG, we, ...] may VERB you
    [ {"POS": {"IN": ["PROPN", "PRON"]}},
      {"LOWER": "may"},
      {"POS": "VERB"},
      {"LOWER": "you"}
    ],
    # [9GAG, we, ...] that allows users to
    [ {"POS": {"IN": ["PROPN", "PRON", "NOUN"]}},
      {"LOWER": {"NOT_IN": ["that"]}, "OP": "*"},
      {"LOWER": "that"},
      {"LOWER": "allows"},
      {"LOWER": "users"}
    ],
    # allows drivers and users to
    [ {"LOWER": "allows"},
      {"LOWER": "drivers"},
      {"LOWER": "and"},
      {"LOWER": "users"},
      {"LOWER": "to"},
    ],

]

prohibition_pattern = [
    # [We, Apple, etc.] reserve all rights
    [ {"POS": {"IN": ["PROPN", "PRON"]}},
      {"LOWER": "reserve"},
      {"LOWER": "all"},
      {"LOWER": "rights"},
      {"LOWER": "not"}
    ],
    # You promise that you will not
    [ {"LOWER": "you", "OP": "?"},
      {"LOWER": "promise", "OP": "?"},
      {"LOWER": "that", "OP": "?"},
      {"LOWER": "you"},
      {"LOWER": "will"},
      {"LOWER": "not"}
    ],
    # No person ... shall have 
    [ {"LOWER": "no"},
      {"LOWER": "person"},
      {"LOWER": {"NOT_IN": ["shall"]}, "OP": "*"},
      {"LOWER": "shall"}
    ],
    # We don't control, verify...
    [ {"LOWER": "we"},
      {"LOWER": "do"},
      {"LEMMA": "not"},
      {"POS": "VERB"},
      {"IS_PUNCT": True},
      {"POS": "VERB"}
    ],
    # We must not have
    [ {"LOWER": "we"},
      {"LOWER": "must"},
      {"LOWER": "not"},
      {"LOWER": "have"}
    ],
    [ {"LOWER": "no"},
      {"LOWER": {"IN": ["right", "title", "interest"]}},
      {"LOWER": {"NOT_IN": ["shall"]}, "OP": "*"},
      {"LOWER": "shall"},
      {"LOWER": "be"}
    ],
    # You hereby acknowledge... but it shall not
    [ {"LOWER": "you"},
      {"LOWER": "hereby", "OP": "?"},
      {"LOWER": "acknowledge"},
      {"LOWER": {"NOT_IN": ["but"]}, "OP": "*"},
      {"LOWER": "but"},
      {"LOWER": "it"},
      {"LOWER": "shall"},
      {"LOWER": "not"}
    ],
    # Don't use the [NOUN] to do harm
    [ {"LOWER": "do"},
      {"LEMMA": "not"},
      {"LOWER": "use"},
      {"LOWER": "the"},
      {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}},
      {"LOWER": "to"},
      {"LOWER": "do"},
      {"LOWER": "harm"},
    ],
    # You represent and warrant that (a) you are not located
    [ {"LOWER": "you"},
      {"LOWER": {"IN": ["represent"]}},
      {"LOWER": "and"},
      {"LOWER": {"IN": ["warrant"]}},
      {"LOWER": "that"},
      {"LOWER": {"NOT_IN": ["you"]}, "OP": "*"},
      {"LOWER": "you"},
      {"LOWER": {"NOT_IN": ["are"]}, "OP": "*"},
      {"LOWER": "are"},
      {"LOWER": "not"},
    ],
    # you (further?) agree not to VERB
    [ {"LOWER": "you"},
      {"LOWER": "further", "OP": "?"},
      {"LEMMA": "agree"},
      {"LOWER": "not"},
      {"LOWER": "to"},
      {"POS": "VERB"}
    ],
    # you can't violate... terms
    [ {"LOWER": "you"},
      {"LOWER": "ca"},
      {"LEMMA": "not"},
      {"LOWER": "violate"},
      {"LOWER": {"NOT_IN": ["terms"]}, "OP": "*"},
      {"LOWER": "terms"}
    ],
    # you may not VERB
    [ {"LOWER": "you"},
      {"LOWER": "may"},
      {"LOWER": "not"},
      {"POS": "VERB"},
      {"LOWER": "or", "OP": "?"},
      {"POS": "VERB", "OP": "?"}
    ],
    # you will not VERB and VERB
    [ {"LOWER": "you"},
      {"LOWER": "will"},
      {"LOWER": "not"},
      {"POS": "VERB"},
      {"LOWER": "and", "OP": "?"},
      {"POS": "VERB", "OP": "?"}
    ],
    # you shall not include ... illegal ... inappropriate
    [ {"LOWER": "you"},
      {"LOWER": "shall"},
      {"LOWER": "not"},
      {"LOWER": "include"},
      {"LOWER": {"NOT_IN": ["illegal"]}, "OP": "*"},
      {"LOWER": "illegal"},
      {"LOWER": {"NOT_IN": ["inappropriate"]}, "OP": "*"},
      {"LOWER": "inappropriate", "OP": "?"}
    ],
    # we will not be able to
    [ {"LOWER": "we"},
      {"LOWER": "will"},
      {"LOWER": "not"},
      {"LOWER": "be"},
      {"LOWER": "able"},
      {"LOWER": "to"}
    ],
    # you are not permitted to
    [ {"LOWER": "you"},
      {"LOWER": "are"},
      {"LOWER": "not"},
      {"LOWER": "permitted"},
      {"LOWER": "to"}
    ],
    # PRON cannot be VERB
    [ {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}},
      {"LOWER": {"NOT_IN": ["can", "shall"]}, "OP": "*"},
      {"LOWER": {"IN": ["can", "shall"]}},
      {"LOWER": "not"},
      {"LOWER": "be"},
      {"POS": "VERB"},
    ],
    # prohibits [discriminatory, obscene, harrasing, sceptive, violent, illegal]
    [ {"LOWER": {"IN": ["prohibits", "prohibit"]}},
      {"LOWER": {"NOT_IN": ["discriminatory", "obscene", "harassing", "deceptive", "violent", "illegal"]}, "OP": "*"},
      {"LOWER": {"IN": ["discriminatory", "obscene", "harassing", "deceptive", "violent", "illegal"]}}
    ],
    # we do not warrant that
    [ {"LOWER": "we"},
      {"LOWER": "do"},
      {"LOWER": "not"},
      {"LOWER": "warrant"},
      {"LOWER": "that"}
    ],
    # prohibited from VERB
    [ {"LOWER": "prohibited"},
      {"LOWER": "from"},
      {"POS": "VERB"}
    ],
    # have no right to VERB
    [ {"LOWER": "have"},
      {"LOWER": "no"},
      {"LOWER": "right"},
      {"LOWER": "to"},
      {"POS": "VERB"}
    ],
    # illegal... do not VERB
    [ {"LOWER": "illegal"},
      {"LOWER": {"NOT_IN": ["do"]}, "OP": "*"},
      {"LOWER": "do"},
      {"LOWER": "not"},
      {"POS": "VERB"},
    ],
    # [NOUN, PRON] do not grant
    [ {"POS": {"IN": ["PROPN", "PRON", "NOUN"]}},
      {"LOWER": "do"},
      {"LOWER": "not"},    
      {"LOWER": "grant"}
    ],
    # [NOUN] may not be VERB
    [ {"POS": {"IN": ["PROPN", "PRON", "NOUN"]}},
      {"LOWER": {"NOT_IN": ["may"]}, "OP": "*"},
      {"LOWER": "may"},
      {"LOWER": "not"},
      {"LOWER": "be"},
      {"POS": "VERB"},
      {"LOWER": "or", "OP": "?"},
      {"POS": "VERB", "OP": "?"}
    ],
    # You must not VERB 
    [ {"LOWER": "you"},
      {"LOWER": "must"},
      {"LOWER": "not"},
      {"POS": "VERB"}
    ],
    # [NOUN] may not process
    [ {"POS": {"IN": ["PROPN", "PRON", "NOUN"]}},
      {"LOWER": "may"},
      {"LOWER": "not"},
      {"LOWER": "process"}
    ],

]

duty_pattern = [
   # [NOUN] shall be based
    [ {"POS": "NOUN"},
      {"LOWER": "shall"},
      {"LOWER": "be"},
      {"LOWER": "based"}
    ],
    # [PRON] may be required to
    [ {"POS": {"IN": ["PROPN", "PRON"]}},
      {"LOWER": "may"},
      {"LOWER": "be"},
      {"LOWER": "required"},
      {"LOWER": "to", "OP": "?"}
    ],
    # Read and follow our Term
    [ {"POS": "VERB", "OP": "?"},
      {"LOWER": "and", "OP": "?"},
      {"POS": "VERB"},
      {"LOWER": "our"},
      {"LOWER": "terms"}
    ],
    # treat others with respect
    [ {"LOWER": "treat"},
      {"LOWER": "others"},
      {"LOWER": "with"},
      {"LOWER": "respect"}
    ],
    ## if all CAPS LOCK, then DUTY
    [ {"IS_UPPER": True, "OP": "{10,}"}
    ],
    # You dont have to... but you must
    [ {"LOWER": "you"},
      {"LOWER": "do"},
      {"LEMMA": "not"},
      {"LOWER": "have"},
      {"LOWER": "to"},
      {"LOWER": {"NOT_IN": ["but"]}, "OP": "*"},
      {"LOWER": "but"},
      {"LOWER": "you"},
      {"LOWER": "must"}
    ],
    # You must provide
    [ {"LOWER": "you"},
      {"LOWER": "must"},
      {"LOWER": "provide"}
    ],
    # You are [solely?] responsible for
    [ {"LOWER": "you"},
      {"LOWER": "are"},
      {"LOWER": "solely", "OP": "?"},
      {"LOWER": "responsible"},
      {"LOWER": "for"}
    ],
    # [SERVICES] may be updated.. you should check it regularly
    [ {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}},
      {"LOWER": "may"},
      {"LOWER": "be"},
      {"LOWER": "updated"},
      {"LOWER": {"NOT_IN": ["you"]}, "OP": "*"},
      {"LOWER": "you"},
      {"LOWER": "should"},
      {"LOWER": "check"}
    ],
    # at the sole risk by you
    [ {"LOWER": "sole"},
      {"LOWER": "risk"},
      {"LOWER": "by"},
      {"LOWER": "you"}
    ],
    # if you fail to meet requirements, you should stop using service
    [ {"LOWER": "if"},
      {"LOWER": {"NOT_IN": ["fail"]}, "OP": "*"},
      {"LOWER": "fail"},
      {"LOWER": {"NOT_IN": ["requirements"]}, "OP": "*"},
      {"LOWER": "requirements"},
      {"LOWER": {"NOT_IN": ["you"]}, "OP": "*"},
      {"LOWER": "you"},
      {"LOWER": "should"},
      {"LOWER": "stop"},
    ],
    # if you do not accept..., you must stop
    [ {"LOWER": "if"},
      {"LOWER": "you"},
      {"LOWER": "do"},
      {"LEMMA": "not"},
      {"LOWER": {"IN": ["agree", "accept"]}},
      {"LOWER": {"NOT_IN": ["you"]}, "OP": "*"},
      {"LOWER": "you"},
      {"LOWER": "must"},
      {"LOWER": "stop"}
    ],
    # we both agree that, both parties agree that
    [ {"LOWER": "we", "OP": "?"},
      {"LOWER": "both"},
      {"LOWER": "parties", "OP": "?"},
      {"LOWER": {"IN": ["agree", "agreed"]}},
      {"LOWER": "that"}
    ],
    # you will be subjected ... responsible for
    [ {"LOWER": "you"},
      {"LOWER": "will"},
      {"LOWER": "be"},
      {"LOWER": {"IN": ["subject", "responsible"]}},
      {"LOWER": {"NOT_IN": ["subject", "responsible"]}, "OP": "*"},
      {"LOWER": {"IN": ["subject", "responsible"]}},
      {"LOWER": "for"}
    ],
    # you understand that the
    [ {"LOWER": "you"},
      {"LOWER": "understand"},
      {"LOWER": "that"},
      {"LOWER": "the"}
    ],
    # copyright infringement should be sent
    [ {"LOWER": "infringement"},
      {"LOWER": {"NOT_IN": ["should"]}, "OP": "*"},
      {"LOWER": "should"},
      {"LOWER": "be"},
      {"LOWER": "sent"}
    ],
    # advertisers must provide
    [ {"LOWER": "advertisers"},
      {"LOWER": "must"},
      {"LOWER": "provide"},
    ],
    # NOUN must cancel the? service
    [ {"POS": "NOUN"},
      {"LOWER": "must"},
      {"LOWER": "cancel"},
      {"LOWER": "the", "OP": "?"},
      {"LOWER": "service"},
    ],
    # creating an account, you will provide information
    [ {"LOWER": "account"},
      {"LOWER": {"NOT_IN": ["you"]}, "OP": "*"},
      {"LOWER": "you"},
      {"LOWER": "will"},
      {"LOWER": "provide"},
      {"LOWER": {"NOT_IN": ["information"]}, "OP": "*"},
      {"LOWER": "information"}
    ],
    # you are accountable
    [ {"LOWER": "you"},
      {"LOWER": "are"},
      {"LOWER": "accountable"},
    ],
    # arbitrator must issue
    [ {"LOWER": "arbitrator"},
      {"LOWER": "must"},
      {"LOWER": "issue"}
    ],
    # you,user acknowledge,agree that
    [ {"LOWER": {"IN": ["you", "user"]}},
      {"LOWER": {"IN": ["acknowledge", "agree", "acknowledges", "agrees"]}},
      {"LOWER": "that"}
    ],
    # it is your responsibility to
    [ {"LOWER": "it"},
      {"LOWER": "is"},
      {"LOWER": "your"},
      {"LOWER": "responsibility"},
      {"LOWER": "to"}
    ],
    # [NOUN] shall ensure that
    [ {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}},
      {"LOWER": "shall"},
      {"LOWER": {"IN": ["ensure", "refund"]}},
      {"LOWER": "that", "OP": "?"}
    ],
    # you/r terminate if you fail to comply
    [ {"LOWER": {"IN": ["you", "your"]}},
      {"LOWER": {"NOT_IN": ["terminate"]}, "OP": "*"},
      {"LOWER": "terminate"},
      {"LOWER": {"NOT_IN": ["if"]}, "OP": "*"},
      {"LOWER": "if"},
      {"LOWER": "you"},
      {"LOWER": "fail"},
      {"LOWER": "to"},
      {"LOWER": "comply"},
    ],
    # you cannot use [NOUN]
    [ {"LOWER": "you"},
      {"LOWER": "can"},
      {"LOWER": "not"},
      {"LOWER": "use"},
      {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}},
    ],
    # you further agree that
    [ {"LOWER": "you"},
      {"LOWER": "further"},
      {"LOWER": "agree"},
      {"LOWER": "that"}
    ],
    #please read...terms and conditions (policy)
    [ {"LOWER": "please"},
      {"LOWER": "read"},
      {"LOWER": {"NOT_IN": ["terms", "conditions", "policy"]}, "OP": "*"},
      {"LOWER": {"IN": ["terms", "conditions", "policy"]}, "OP": "*"},
    ],
    # you represent and warrant that
    [ {"LOWER": "you"},
      {"LOWER": {"IN": ["represent"]}},
      {"LOWER": "and"},
      {"LOWER": {"IN": ["warrant"]}},
      {"LOWER": "that"},
      {"LOWER": {"NOT_IN": ["you"]}, "OP": "*"},
      {"LOWER": "you"},
    ],
    # please VERB your
    [ {"LOWER": "please"},
      {"POS": "VERB"},
      {"LOWER": "your"}
    ],
    # you hereby? acknowledge and consent
    [ {"LOWER": {"IN": ["you", "user"]}},
      {"LOWER": "hereby", "OP": "?"},
      {"LOWER": {"IN": ["acknowledge", "acknowledges", "agree", "agrees", "consent"]}},
      {"LOWER": "and", "OP": "?"},
      {"LOWER": {"IN": ["acknowledge", "acknowledges", "agree", "agrees", "consent"]}, "OP": "?"}
    ],
    # you further agree and consent 
    [ {"LOWER": "you"},
      {"LOWER": "further"},
      {"LOWER": "agree"},
      {"LOWER": "and"},
      {"LOWER": "consent"}
    ],
    # may require you to submit
    [ {"LOWER": "may"},
      {"LOWER": "require"},
      {"LOWER": "you"},
      {"LOWER": "to"},
      {"LOWER": {"IN": ["pay", "submit"]}}
    ],
    # read and follow our terms
    [ {"LOWER": "read"},
      {"LOWER": "and", "OP": "?"},
      {"LOWER": "follow", "OP": "?"},
      {"LOWER": "our"},
      {"LOWER": "terms"}
    ],
    # you cannot use [NOUN]
    [ {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}},
      {"LOWER": "retains"},
      {"LOWER": "sole"},
      {"LOWER": "discretion"}
    ],
    # please use customer support
    [ {"LOWER": "please"},
      {"LOWER": "use"},
      {"LOWER": "customer"},
      {"LOWER": "support"}
    ],
    # we may need to provide you
    [ {"LOWER": "we"},
      {"LOWER": "may"},
      {"LOWER": "need"},
      {"LOWER": "to"},
      {"LOWER": "provide"},
      {"LOWER": "you"}
    ],
    # if, then you may not
    [ {"LOWER": "if"},
      {"LOWER": "you"},
      {"LOWER": "do"},
      {"LEMMA": "not"},
      {"LOWER": "agree"},
      {"LOWER": {"NOT_IN": ["then"]}, "OP": "*"},
      {"LOWER": "then"},
      {"LOWER": "you"},
      {"LOWER": "may"},
      {"LEMMA": "not"}
    ],
    # you irrevocably release the NOUN
    [ {"LOWER": "you"},
      {"LOWER": "irrevocably"},
      {"LEMMA": "release"},
      {"LOWER": "the"},
      {"POS": {"IN": ["PROPN", "PROP", "NOUN"]}}
    ],
]

matcher.add("Permission", permission_pattern)
matcher.add("Prohibition", prohibition_pattern)
matcher.add("Duty", duty_pattern)



# Read text file if input is text file
def readTxtFile(txtFile):
    TOS = open(txtFile, encoding="utf-8")
    with TOS as file:
        data = file.read().rstrip('')
    return data

# Preprocessing
def removePuncAndTokenizeSent(origToS):
    #new_string = re.sub(r'[^\w\s.]', '', origToS)
    #new_string = re.sub(r'[^\w\s.]', '', origToS)
    #sent_tokenized = nltk.sent_tokenize(new_string)
    sent_tokenized = [p for p in origToS.split('\n') if p]
    return sent_tokenized

# Input: Unclassified array of Sentences
# Output: Array of predictions, ex. [1, 0, 2, 3 ...] wherein  0 is others, 1 is permission, 2 is prohibition, 3 is duty
def ruleBasedClassification(cleanTos): 
    rule_based_prediction = []     
    x = 1
    number_in_list = 0
    for i in cleanTos:         # change sentences to value_list
        doc = nlp(i)              #Read a sentence
        matches = matcher(doc)    # 
        x = x+1
        #print(x)
        duty_count = 0
        prohibition_count = 0
        permission_count = 0
        #print(matches)
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]  # Get string representation
            span = doc[start:end]  # The matched span
            #print(match_id, string_id, start, end, span.text)
            if (string_id == "Duty"):
                duty_count += 1
            elif (string_id == "Prohibition"):
                prohibition_count += 1
            elif (string_id == "Permission"):
                permission_count += 1

        #print(duty_count, prohibition_count, permission_count)      
        
        if (duty_count > 0):
            if (prohibition_count > 0):         # if detected duty but also detected prohibition, then it is prohibition
                if re.search("if you don't agree", i, re.IGNORECASE):  # if the if statement is not found, prohibition
                    rule_based_prediction.append(3) 
                else:
                    rule_based_prediction.append(2)
                    if (cleanTos[number_in_list]) != "PROHIBITION":
                        #print(x, "PROHIBITION", i)
                        print(x, "Detected as PROHIBITION, must be " + cleanTos[number_in_list], i)
            else:                                #if no prohibition, then it is duty
                rule_based_prediction.append(3) 
                if (cleanTos[number_in_list]) != "DUTY":
                    #print(x, "DUTY", i)
                    print(x, "Detected as DUTY, must be " + cleanTos[number_in_list], i)

        elif (prohibition_count > 0):
            if re.search("in such event", i, re.IGNORECASE) or \
               re.search("nothing in this", i, re.IGNORECASE) :
                rule_based_prediction.append(0)
            else:    
                rule_based_prediction.append(2)
                if (cleanTos[number_in_list]) != "PROHIBITION":
                    #print(x, "PROHIBITION", i)
                    print(x, "Detected as PROHIBITION, must be " + cleanTos[number_in_list], i)

        elif (permission_count > 0):
            if re.search("may contain links", i, re.IGNORECASE) or \
               re.search("may also include links", i, re.IGNORECASE) or \
               re.search("nothing in these terms", i, re.IGNORECASE) or \
               re.search("agreement may only be", i, re.IGNORECASE) or \
               re.search("this section applies", i, re.IGNORECASE) or \
               re.search("it may communicate", i, re.IGNORECASE) or \
               re.search("must be meeting a target", i, re.IGNORECASE) or \
               re.search("you may make", i, re.IGNORECASE):
                rule_based_prediction.append(0)
            else:    
                rule_based_prediction.append(1)
                if (cleanTos[number_in_list]) != "PERMISSION":
                    #print(x, "PERMISSION", i)
                    print(x, "Detected as PERMISSION, must be " + cleanTos[number_in_list], i)

        else:
            rule_based_prediction.append(0)
            if (cleanTos[number_in_list]) != "OTHERS":
                #print(x, "OTHERS", i)
                print(x, "Detected as OTHERS, must be " + cleanTos[number_in_list], i)

       
            
    
    

    return rule_based_prediction


lists = [
    "You acknowledge and agree that such system requirements, which may be changed from time to time, are Your responsibility."
]

print(ruleBasedClassification(lists))

#For debugging
#incorrect = 0
#for i in range(len(rule_based_prediction)):
#  if rule_based_prediction[i] != value_list[i]:
#    incorrect += 1

#print("Number of incorrect classification: " + incorrect)