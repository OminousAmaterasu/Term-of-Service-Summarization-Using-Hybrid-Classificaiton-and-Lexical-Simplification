#import joblib
#svm_from_joblib = joblib.load("D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy\\clf.pkl")
from flask import Flask, render_template, request
import RuleBasedClassificationV2 as RuleBased
#import SVM as svm
#svm.reload('process_text')
#import LexicalSimplification as lexSimple
import re
import string
import WebScraping
import pandas as pd
import csv

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score



app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("ToS.html")

@app.route("/result", methods = ["POST"])
def result():
    sent_tokenized=[]
    import SVM as svm


    text_file = request.files['fileToS']
    file = text_file.read()
    file = file.decode("utf-8")

    #output = request.form.to_dict() 
        #file = request.files['file']
    #output = file.stream.read()
        #    return render_template("ToS.html", summToS = "The file is here!")
    #else:
        #output = request.form['origToS']
       #    return render_template("ToS.html", summToS = "Me")

    toBeTokenized = ""
    textArea = request.form.get('copyPasteTOS')

    websiteLink = request.form.get('websiteLink')
    if len(file) > len(textArea):
        toBeTokenized = file
    elif len(file) < len(textArea):
        toBeTokenized = textArea
    elif len(file) == 0 or len(textArea) == 0:
        toBeTokenized = WebScraping.extractTextFromLink(websiteLink)


    sent_tokenized = RuleBased.removePuncAndTokenizeSent(toBeTokenized)

    # Rule-Based Only
    array_classified_rule_based = RuleBased.ruleBasedClassification(sent_tokenized)  # categorize using rulebased

    #SVM Only
    array_classified_SVM = svm.classifySVM(sent_tokenized) #categorize using svm

    # Hybrid-Series
    # INPUT => RULE-BASED => SVM => OUTPUT
    # if rulebased and svm are not the same, svm's output will be picked
    series_classification = []
    for x in range(len(sent_tokenized)):
        # if rule-based is not same, svm is picked
        if array_classified_rule_based[x] != array_classified_SVM[x]:
            series_classification.append(array_classified_rule_based[x])
        # else, rule-based as is
        else:
            series_classification.append(array_classified_SVM[x])
        #if array_classified_rule_based[x] == 0:  #if rule-based prediction is "Others"...
        #    if array_classified_SVM[x] != 0: # if svm prediciton is not "Others"...
        #        array_classified_rule_based[x] = array_classified_SVM[x]  # Overwrite the prediciton of rule-based with prediciton of svm

    # Hybrid-Parallel
    # INPUT => SVM  =======> OUTPUT
    #    ↓===> RULE-BASED == ↑     
    # category depends on hierarchy
    # 1. Prohibition 2. Duty  3. Permission 4. Others
    parallel_classification = []
    for x in range(len(sent_tokenized)):
        # if rule-based and svm are not same...
        if array_classified_rule_based[x] != array_classified_SVM[x]:
            match array_classified_rule_based[x]:
                case 0: #if rule-based is others but svm is Perm Proh or Dut, pick SVM
                    parallel_classification.append(array_classified_SVM[x])
                case 1: 
                    # if rule-based is permission but svm is proh or dut, pick SVM
                    if array_classified_SVM[x] == 2 or array_classified_SVM[x] == 3:
                        parallel_classification.append(array_classified_SVM[x])
                    # if rule-based is permission but svm is others, pick rule-based as is
                    else:
                        parallel_classification.append(array_classified_rule_based[x])
                case 2: 
                    # if rule-based is prohibition, highest in hierarchy, so pick rule-based
                    parallel_classification.append(array_classified_rule_based[x])
                case 3:
                    # if rule-based is duty but svm proh, pick SVM
                    if array_classified_SVM[x] == 2:
                        parallel_classification.append(array_classified_SVM[x])
                    # if rule-based is duty but svm is others, pick rule-based as is
                    else:
                        parallel_classification.append(array_classified_rule_based[x])

        # if output is same, as is
        else:
            parallel_classification.append(array_classified_rule_based[x])

            

     # <--! EXPERIMENT RESULT start  -->       

    df = pd.read_csv('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy - Copy\\Test-Dataset - Copy.csv')
    actual_value = list(df.VALUE)

    header = ['NUMBER', 'SENTENCE', 'ACTUAL_VALUE', 'PREDICTED_VALUE']

    # Rule-based
    with open('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy - Copy\\tos-rule-based-only-result.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for x in range(len(sent_tokenized)):
            writer.writerow([x, sent_tokenized[x], actual_value[x], array_classified_rule_based[x]])
    
    #SVM
    with open('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy - Copy\\tos-svm-only-result.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for x in range(len(sent_tokenized)):
            writer.writerow([x, sent_tokenized[x], actual_value[x], array_classified_SVM[x]])

    #Series
    with open('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy - Copy\\tos-series-result.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for x in range(len(sent_tokenized)):
            writer.writerow([x, sent_tokenized[x], actual_value[x], series_classification[x]])

    #Parallel
    with open('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy - Copy\\tos-parallel-result.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for x in range(len(sent_tokenized)):
            writer.writerow([x, sent_tokenized[x], actual_value[x], parallel_classification[x]])

    # Precision, Recall, F-measure
    with open('D:\\BSCS 3-3\\Second Semester\\6 CS Thesis Writing 1\\Project (Software)\\ToSUM V1 - Copy - Copy\\new-result.txt', 'w', encoding='utf-8') as f:
        f.write('Rule-Based Only')
        f.write(classification_report(actual_value, array_classified_rule_based))
        f.write('\n')
        f.write('SVM Only')
        f.write(classification_report(actual_value, array_classified_SVM))
        f.write('\n')
        f.write('Hybrid-Parallel')
        f.write(classification_report(actual_value, parallel_classification))
        f.write('\n')
        f.write('Hybrid-Series')
        f.write(classification_report(actual_value, series_classification))
        f.write('\n')

    # <--! EXPERIMENT RESULT end  -->   

    #rule_based_only_duty = []
    #rule_based_only_prohibition = []
    #rule_based_only_permission = []
    #rule_based_only_others = []
    #sent_count = 0
    #for x in sent_tokenized:
    #     if array_classified_rule_based[sent_count] == 1 :
    #        rule_based_only_permission.append(x)
    #     elif array_classified_rule_based[sent_count] == 2:
    #         rule_based_only_prohibition.append(x)
    #     elif array_classified_rule_based[sent_count] == 3:
    #          rule_based_only_duty.append(x)
    #     else: 
    #        rule_based_only_others.append(x)
            #sent_count += 1
            #if sent_count >= 299:
            #    break

  

        
    #simplified_perm  = lexSimple.simplify(permission)
    #simplified_proh = lexSimple.simplify(prohibition)
    #simplified_dut = lexSimple.simplify(duty)

    return render_template("ToS.html", 
                             # Original Sentences
                            sent_tokenized=sent_tokenized, 
                            # Rule-Based Only (category of sentence only (0, 1, 2, 3), not sentences ) 
                            array_classified_rule_based=array_classified_rule_based,
                            # SVM only output (category of sentence only (0, 1, 2, 3), not sentences ) 
                            array_classified_SVM=array_classified_SVM,
                            # Hybrid-Series Classification
                            series_classification=series_classification,
                            # Hybrid-Parallel Classification
                            parallel_classification=parallel_classification
                            # Simplified Sentences
                            #simplified_perm=simplified_perm, simplified_proh=simplified_proh, simplified_dut=simplified_dut,
                            )

if __name__ == '__main__':
    def process_text(text):
        text = str(text)
        nopunc = [char for char in text if char not in string.punctuation]
        nopunc = ''.join(nopunc)
        clean_words = [word for word in nopunc.split()]

        return clean_words
    app.run(debug = True, port= 5000)

