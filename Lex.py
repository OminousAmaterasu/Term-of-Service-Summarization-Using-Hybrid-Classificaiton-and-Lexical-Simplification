#<-- START Install Packages using pip -->
#import subprocess
#import sys

#def install(package):
#    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

#install("wordfreq")
#install("wordfreq")
#install("torch")
#<-- END Install Packages using pip -->

import torch
from transformers import BertTokenizer, BertModel, BertForMaskedLM

import wordfreq
from wordfreq import zipf_frequency

bert_model = 'bert-large-uncased'
print(bert_model)
tokenizer = BertTokenizer.from_pretrained(bert_model)
print(tokenizer)
model = BertForMaskedLM.from_pretrained(bert_model)
print(model)

def get_bert_candidates(input_text, numb_predictions_displayed = 10):
  list_candidates_bert = []
  for word in input_text.split():
    if zipf_frequency(word, 'en') < 5:
      replace_word_mask = input_text.replace(word, '[MASK]')
      text = f'[CLS]{replace_word_mask} [SEP] {input_text} [SEP] '
      tokenized_text = tokenizer.tokenize(text)
      masked_index = [i for i, x in enumerate(tokenized_text) if x == '[MASK]'][0]
      indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
      segments_ids = [0]*len(tokenized_text)
      tokens_tensor = torch.tensor([indexed_tokens])
      segments_tensors = torch.tensor([segments_ids])
      # Predict all tokens
      with torch.no_grad():
          outputs = model(tokens_tensor, token_type_ids=segments_tensors)
          predictions = outputs[0][0][masked_index]
      predicted_ids = torch.argsort(predictions, descending=True)[:numb_predictions_displayed]
      predicted_tokens = tokenizer.convert_ids_to_tokens(list(predicted_ids))
      list_candidates_bert.append((word, predicted_tokens))
  return list_candidates_bert

def post_process(original, simplified):
  ls = original.split()
  ls2 = simplified.split()
  for word in ls:
    if "," in word:
      ls2[ls.index(word)] = ls2[ls.index(word)]+','
  return ' '.join(ls2)


list_texts = [ 
 'The Risk That Students Could Arrive at School With the Coronavirus as schools grapple with how to reopen, new estimates show that large parts of the country would probably see infected students if classrooms opened now.'
] 

import re
for input_text in list_texts:
  new_text = input_text
  bert_candidates =  get_bert_candidates(input_text)
  for word_to_replace, l_candidates in bert_candidates:
    tuples_word_zipf = []
    for w in l_candidates:
      if w.isalpha():
        tuples_word_zipf.append((w, zipf_frequency(w, 'en')))
    tuples_word_zipf = sorted(tuples_word_zipf, key = lambda x: x[1], reverse=True)
    new_text = re.sub(word_to_replace, tuples_word_zipf[0][0], new_text) 
  print("Original text: ", input_text )
  print("Simplified text:", post_process(input_text, new_text), "\n")
