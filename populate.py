import jwt
import random
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from app.mod_search.models import Document
import ast

from mongoengine import connect
connect(name='quality',
        username='davide',
        password='qupid',
        host='mongodb://davide:qupid@ds011943.mlab.com:11943/heroku_pv8g6c32')

'''json_key = json.load(open(os.path.join(MYDIR,'first-c75c55e52243.json')))
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
gc = gspread.authorize(credentials)
wks = gc.open("vaccinations_meta").sheet1

urls2 = wks.col_values(2)
urls2 = [x for x in urls2 if x.startswith("http")]
urls9 = wks.col_values(9)
urls9 = [x for x in urls9 if x.startswith("http")]
titles = wks.col_values(3)[x]

for i in range(0,len(urls2)):
    doc = Document()
    try:
        snip = ""#urllib.urlopen(wks.col_values(2)[res[i]]).read()[0:3000]
        alc = call_alchemy_combined.call(arch[i])
        sent = alc['docSentiment']['score'] if 'score' in alc['docSentiment'] else "0"
        emotion = alc['docEmotions'] if 'docEmotions' in alc else {}
        doc = Document("/annotate?url="+urls9[i],titles[i],snip,sent,emotion)
        doc.save()
        docs.append(doc)
    except:
        try:
            snip = ""#urllib.request.urlopen(wks.col_values(9)[res[i]]).read()[0:3000]
            alc = call_alchemy_combined.call(sh[i])
            sent = alc['docSentiment']['score'] if 'score' in alc['docSentiment'] else "0"
            emotion = alc['docEmotions'] if 'docEmotions' in alc else {}
            doc = Document("/annotate?url="urls9[i],titles[i],snip,sent,emotion)
            doc.save()
            docs.append(doc)
        except:
            pass'''

import csv
with open('vaccines_data.csv') as csvfile:
    vreader = csv.reader(csvfile, delimiter=',',quotechar='"')
    vreader.next()
    for row in vreader:
        doc = Document()
        doc.url = row[1]
        doc.title = row[2]
        doc.source = row[3]
        doc.trustworthiness = round(float(row[12])/100,1)
        doc.sentiment = round(float(row[5]),1)
        doc.entities = ast.literal_eval(row[6])
        doc.emotion['anger'] = round(float(row[7]),1)
        doc.emotion['joy'] = round(float(row[8]),1)
        doc.emotion['fear'] = round(float(row[9]),1)
        doc.emotion['sadness'] = round(float(row[10]),1)
        doc.emotion['disgust'] = round(float(row[11]),1)
        doc.save()