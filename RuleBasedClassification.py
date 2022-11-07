import nltk
import spacy
import re
import subprocess
import sys


#def install(package):
#    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

#install("spacy-transformers")

#spacy.cli.download('en_core_web_trf')  #uncomment if en_core_web_trf is not downloaded
nlp = spacy.load('en_core_web_trf')
from spacy.matcher import Matcher
matcher = Matcher(nlp.vocab)


permission_pattern = [
    # 1. (give/s | grant/s | allow/s | permit/s) (to)? (everyone | user | you | contributor | recipient / licensee)
    [  {"LEMMA":  {"IN": ["give", "grant", "allow", "permit"]} }, 
       {"LOWER": "to", "OP": "?"}, 
       {"LOWER": {"IN": ["everyone", "user", "you", "contributor", "recepient", "licencee"]}} 
    ],
    # 2. (everyone | user | you | contributor | recipient | licensee) be (given | granted | allowed | permitted)
    [ {"LOWER": {"IN": ["everyone", "user", "you", "contributor", "recipient", "licensee"]}},
      {"LEMMA": "be"},
      {"ORTH": {"IN": ["given", "granted", "allowed", "permitted"]}}
    ],
    # 3.  (everyone | user | you | contributor | recipient | licensee) (((be)? free) | (have the freedom))
    [ {"LOWER": {"IN": ["everyone", "user", "you", "contributor", "recipient", "licensee"]}},
      {"LEMMA": "be"},
      {"ORTH": "free",}
    ],
    [ {"LOWER": {"IN": ["everyone", "user", "you", "contributor", "recipient", "licensee"]}},
      {"LEMMA": "have"},
      {"LOWER": "the"},
      {"LOWER": "freedom"}
    ],
    # 4.((you are) | you’re) free
    [ {"LEMMA": "you"},
      {"LOWER": "are", "OP": "?"},
      {"LOWER": "free"}
    ],
    # 5. (everyone | user | you | contributor | recipient | licensee) (can | may)
    [ {"LOWER": {"IN": ["everyone", "user", "you", "contributor", "recipient", "licensee"]}},
      {"LOWER": {"IN": ["can", "may"]}}
    ],
    # 6. We may (verb), (verb)?
    [ {"LOWER": "We"},
      {"LOWER": "may"},
      {"POS": "VERB"},
      {'IS_PUNCT': True},
      {"POS": "VERB", "OP": "?"}
    ],
    # 6. We may 
    [ {"LOWER": "We"},
      {"LOWER": "may"}
    ],
    # 6. We may 
    [ {"LOWER": "you"},
      {"LOWER": "may"},
      {"POS": "VERB"},
      {"LOWER": "your"}
    ],
]

prohibition_pattern = [
    # 1., 2., & 3. please {do not} | don’t (grant | give)
    [ {"LEMMA": "please", "OP": "?"},
      {"LOWER": "do"}, {"ORTH": "not"},
      {"LEMMA": {"IN": ["grant", "give"]}, "OP": "?"}
    ],
    [ {"LOWER": "please", "OP": "?"},
      {"LOWER": "do"}, {"LOWER": "n't"},
      {"LEMMA": {"IN": ["grant", "give"]}, "OP": "?"}
    ],
    # (the)? (user/s | you | contributor/s | recipient | licensee) {also}? (may | will | agree | can | should | must) not|(n’t)?
    [ {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["user", "you", "contributor", "recepient", "licensee"]}},
      {"LOWER": "also", "OP": "?"},
      {"LOWER": {"IN": ["may", "will", "agree", "can", "should", "must"]}},
      {"LEMMA": {"IN": ["not"]}}
    ],
    [ {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["user", "you", "contributor", "recepient", "licensee"]}},
      {"LOWER": "also", "OP": "?"},
      {"lemma": {"IN": ["will", "can", "should", "must"]}},
      {"LOWER": {"IN": ["n't"]}}
    ],
    #  the user is not [VERB] to
    [ {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["user", "you", "contributor", "recepient", "licensee"]}},
      {"LEMMA": "be"},
      {"LOWER": "not"},
      {"POS": "VERB"},
      {"LOWER": "to"}
    ],
    # You may never
    [ {"LOWER": "You"},
      {"LOWER": "may"},
      {"LOWER": "never"}
    ],
    # Don't use the service
    [ {"LOWER": "You"},
      {"LOWER": "may"},
      {"LOWER": "never"}
    ]
]

duty_pattern = [
    # provided that (user | your | contributor | recipient | licensee)
    [ {"LOWER": "provided"}, {"LOWER": "that", "OP": "?"}, {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["user", "your", "contributor", "recipient", "licensee"]}}
    ],
    # • ( (in (that|such) case)) (user | you | contributor | recipient | licensee)
    [ {"LOWER": "in"},
      {"LOWER": {"IN": ["such", "that"]}},
      {"LOWER": "case"},
      {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["user", "your", "contributor", "recipient", "licensee"]}}
    ],
    # (only if) ) (user | you | contributor | recipient | licensee)
    [ {"LOWER": "only"},
      {"LOWER": "if"},
      {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["user", "you", "contributor", "recipient", "licensee"]}}
    ],
    # (the)? (user | you | contributor | recipient | licensee) be responsible for
    [ {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["user", "you", "contributor", "recipient", "licensee"]}},
      {"LEMMA": "be"},
      {"LOWER": "responsible"},
      {"LOWER": "for", "OP": "?"}
    ],
    # it is (the)? (user | your | contributor | recipient | licensee) responsibility to
    [ {"LOWER": "the", "OP": "?"},
      {"LOWER": {"IN": ["user", "you", "contributor", "recipient", "licensee"]}},
      {"ORTH": "'s"},
      {"LOWER": "responsibility"},
      {"LOWER": "to", "OP": "?"}
    ],
    # (notice | work |user/s | you | contributor | recipient | licensee) (must | will | should)
    [ {"LOWER": {"IN": ["notice", "work", "user", "users", "you", "contributor", "recipient", "licensee"]}},
      {"LOWER": {"IN": ["must", "will", "should"]}}
    ],
    # You (also)? (acknowledge | understand | agree) and (acknowledge | understand | agree)
    [ {"LOWER": "you"},
      {"LOWER": "also", "OP": "?"},
      {"LOWER": {"IN": ["acknowledge", "understand", "agree"]}},
      {"LOWER": "and", "OP": "?"},
      {"LOWER": {"IN": ["acknowledge", "understand", "agree"]}, "OP": "?"}
    ],
    # You agree to defend
    [ {"LOWER": "you"},
      {"LOWER": "agree"},
      {"LOWER": "to"},
      {"LOWER": "defend"}
    ],
    # If ... you may only (verb)
    [ {"LOWER": "if"},
      {"OP": "+"},
      {"LOWER": "you"},
      {"LOWER": "may"},
      {"LOWER": "only"},
      {"POS": "VERB"}
    ],
    # expect(s) (users of the (company))? to do the same
    [ {"LEMMA": "expect"},
      {"LOWER": "users"},
      {"OP": "+"},
      {"LOWER": "to", "OP": "?"},
      {"LOWER": "do"},
      {"LOWER": "the"},
      {"LOWER": "same"}
    ],
    # You may need
    [ {"LOWER": "you"},
      {"LOWER": "may", "OP": "?"},
      {"LOWER": "need"},
      {"LOWER": "to", "OP": "?"}
    ],

]

matcher.add("Permission", permission_pattern)
matcher.add("Prohibition", prohibition_pattern)
matcher.add("Duty", duty_pattern)



# Reminder: Una dapat muna icatch yung permission, then yung prohibiton, 
# then yung duty (para macatch ng maayos yung mga sentences)




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
            rule_based_prediction.append(2)
            if (cleanTos[number_in_list]) != "PROHIBITION":
                #print(x, "PROHIBITION", i)
                print(x, "Detected as PROHIBITION, must be " + cleanTos[number_in_list], i)

        elif (permission_count > 0):
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

#For debugging
#incorrect = 0
#for i in range(len(rule_based_prediction)):
#  if rule_based_prediction[i] != value_list[i]:
#    incorrect += 1

#print("Number of incorrect classification: " + incorrect)