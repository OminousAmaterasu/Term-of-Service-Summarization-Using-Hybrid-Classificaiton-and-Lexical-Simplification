import pandas as pd
df = pd.read_csv("D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy\\tos-4.csv")
sentence = list(df.SENTENCES)


with open("D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy\\Tester.txt", "w+", encoding="utf-8") as f:
    for x in range(len(sentence)):
        f.write(sentence[x])
        f.write("\n")

f.close