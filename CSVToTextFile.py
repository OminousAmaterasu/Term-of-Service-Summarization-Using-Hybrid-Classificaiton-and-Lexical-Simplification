import pandas as pd

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


df = pd.read_csv('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy - Copy\\Test-Dataset.csv')
actual_value = list(df.VALUE)
sentences = list(df.SENTENCES)




with open('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy - Copy\\test-dataset.txt', 'w', encoding='utf-8') as f:
    for x in range(len(actual_value)):
        f.write(sentences[x])
    # f.write(classification_report(actual_value, predicted_value))
        f.write('\n')