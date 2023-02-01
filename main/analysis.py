import pytesseract
import glob
import re
import string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

terms = {'Quality/Six Sigma':['black belt','capability analysis','control charts','doe','dmaic','fishbone',
                              'gage r&r', 'green belt','ishikawa','iso','kaizen','kpi','lean','metrics',
                              'pdsa','performance improvement','process improvement','quality',
                              'quality circles','quality tools','root cause','six sigma',
                              'stability analysis','statistical analysis','tqm'],      
        'Operations management':['automation','bottleneck','constraints','cycle time','efficiency','fmea',
                                 'machinery','maintenance','manufacture','line balancing','oee','operations',
                                 'operations research','optimization','overall equipment effectiveness',
                                 'pfmea','process','process mapping','production','resources','safety',
                                 'stoppage','value stream mapping','utilization'],
        'Supply chain':['abc analysis','apics','customer','customs','delivery','distribution','eoq','epq',
                        'fleet','forecast','inventory','logistic','materials','outsourcing','procurement',
                        'reorder point','rout','safety stock','scheduling','shipping','stock','suppliers',
                        'third party logistics','transport','transportation','traffic','supply chain',
                        'vendor','warehouse','wip','work in progress'],
        'Project management':['administration','agile','budget','cost','direction','feasibility analysis',
                              'finance','kanban','leader','leadership','management','milestones','planning',
                              'pmi','pmp','problem','project','risk','schedule','scrum','stakeholders'],
        'Data analytics':['analytics','api','aws','big data','busines intelligence','clustering','code',
                          'coding','data','database','data mining','data science','deep learning','hadoop',
                          'hypothesis test','iot','internet','machine learning','modeling','nosql','nlp',
                          'predictive','programming','python','r','sql','tableau','text mining',
                          'visualuzation'],
        'Healthcare':['adverse events','care','clinic','cphq','ergonomics','healthcare',
                      'health care','health','hospital','human factors','medical','near misses',
                      'patient','reporting system']}

def getEmail(texto):
    try:
        email = re.search(r'[\w\.-]+@[a-z0-9\.-]+', texto).group(0)
    except AttributeError:
        email = re.search(r'[\w\.-]+@[a-z0-9\.-]+', texto)
    return email

def getPhoneNumber2(texto):
    try:
        phone = re.findall(r'+?(?[1-9][0-9 .-()]{8,}[0-9]', texto)
    except AttributeError:
        phone = re.search(r'+?(?[1-9][0-9 .-()]{8,}[0-9]', texto)
    return phone

def getPhoneNumber(text):
    e = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    if not e:
        return e
    return e[0]

def getText(file):
    ruta = "main/static/files/"+file
    images = glob.glob(ruta)
    image_text = ""
    for img in images:
        image_text = pytesseract.image_to_string(img)

    image_text = image_text.replace('\n',' ')
    image_text = image_text.replace('  ',' ')
    text_phone = image_text    
    image_text = re.sub(r'\d+','',image_text) #quito números
    image_text_email = image_text
    image_text = image_text.lower() #####
    image_text = image_text.translate(str.maketrans('','',string.punctuation))
    text = image_text

    return text, image_text_email, text_phone

def getRessumeDF(text):
    # ruta = "main/static/files/"+file
    # images = glob.glob(ruta)
    # image_text = ""
    # for img in images:
    #     image_text = pytesseract.image_to_string(img)
    # image_text = re.sub(r'\d+','',image_text) #quito números
    # image_text = image_text.replace('\n',' ')
    # image_text = image_text.replace('  ',' ')
    # image_text_email = image_text
    # image_text = image_text.lower() #####
    # image_text = image_text.translate(str.maketrans('','',string.punctuation))


    # text = image_text
    quality = 0
    operations = 0
    supplychain = 0
    project = 0
    data = 0
    healthcare = 0

    # Create an empty list where the scores will be stored
    scores = []

    # Obtain the scores for each area
    for area in terms.keys():
            
        if area == 'Quality/Six Sigma':
            for word in terms[area]:
                if word in text:
                    quality +=1
            scores.append(quality)
            
        elif area == 'Operations management':
            for word in terms[area]:
                if word in text:
                    operations +=1
            scores.append(operations)
            
        elif area == 'Supply chain':
            for word in terms[area]:
                if word in text:
                    supplychain +=1
            scores.append(supplychain)
            
        elif area == 'Project management':
            for word in terms[area]:
                if word in text:
                    project +=1
            scores.append(project)
            
        elif area == 'Data analytics':
            for word in terms[area]:
                if word in text:
                    data +=1
            scores.append(data)
            
        else:
            for word in terms[area]:
                if word in text:
                    healthcare +=1
            scores.append(healthcare)
            
    sum = pd.DataFrame({'Área':terms.keys(), 'Puntaje': scores}).sort_values(by='Puntaje', ascending=False)

    pie = plt.figure(figsize=(6,6))
    plt.pie(sum['Puntaje'], labels=sum.index, autopct='%1.0f%%',startangle=90)
    plt.title('Áreas más desarrolladas')
    plt.axis('equal')
    pie.savefig('main/static/files/resume_results.png')

    return sum

def getPhone(string):
    phone = ''
    phoneRegEx = re.compile('\"tel\:[\(\)\-0-9\ ]{1,}\"')
    m = phoneRegEx.search(string)
    if m:
        phone = m.group(0)[5:-1]
    return phone

def obtenerDF_Email(file):
    text, text_email, text_phone = getText(file)
    dataframe = getRessumeDF(text)
    email = getEmail(text_email)
    phone = getPhoneNumber(text_phone)
    #print("\n\n",phone,"\n\n")
    return dataframe, email, phone