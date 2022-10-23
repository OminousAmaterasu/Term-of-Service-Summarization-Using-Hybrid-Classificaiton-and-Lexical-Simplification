import string
import joblib


def process_text(text):
    text = str(text)
    nopunc = [char for char in text if char not in string.punctuation]
    nopunc = ''.join(nopunc)
    clean_words = [word for word in nopunc.split()]

    return clean_words

# Load the model from the file
#if __name__ == '__main__':
#  def process_text(text):
#    text = str(text)
#    nopunc = [char for char in text if char not in string.punctuation]
#    nopunc = ''.join(nopunc)
#    clean_words = [word for word in nopunc.split()]

#    return clean_words
svm_from_joblib = joblib.load("D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy\\clf.pkl")
  

# Input: "Others" Category from the output of the Rule-Based Classification
# Output: Further categorizing the sentences using SVM 
def classifySVM(category):
  svm = svm_from_joblib.predict(category)
  print(svm)
  return svm
