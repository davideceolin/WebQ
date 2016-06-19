import random
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from app.mod_search.models import Document, Sequence
import ast

a = range(0,50)
res=[]
for i in range(0,12):
    random.shuffle(a)
    res.append(a)

res = [x for y in res for x in y]

combinations = [res[x*6:(x+1)*6] for x in range(0,len(res)/6)]

for comb in combinations:
    print comb
    s = Sequence()
    s.sequence = [Document.objects[i] for i in comb]
    s.user = None
    s.save()

