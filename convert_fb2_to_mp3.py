# -*- coding: utf-8 -*-
import re
import codecs
import zipfile
import sys

from bs4 import BeautifulSoup
import gevent
from gevent.queue import Queue
from gtts import gTTS

filename = "some.fb2.zip"

""" check is zip"""
flag_is_zip = True
flag_is_zip = zipfile.is_zipfile(filename)
if flag_is_zip:
    zf = zipfile.ZipFile(filename, 'r')
    file_list = [x for x in zf.namelist() if x.endswith(".fb2")]

content = []
if flag_is_zip:
    with zf.open(file_list[0],'r') as f:
        content = f.read().decode('utf8')
    zf.close()
else:
    with codecs.open(filename,'r',encoding='utf8') as f:
        content = f.read()

soup = BeautifulSoup(content,"lxml")
text = soup.find_all("p")

p_text = []
for x in text:
    seq = re.split('(?<=[.!?])\s',x.text)
    p_text.append(seq)

""" save for debug text """
filename_2 = "test_utf_out.txt"
with codecs.open(filename_2,'w',encoding='utf8') as f:
    counter = 0
    for x in p_text:
        counter +=1
        counter_seq = 0
        f.write("\n")
        for p in x:
            if counter_seq>0:
                f.write("\n")        
            f.write(u"t1_{:04d}_{:03d}: {}".format(counter,counter_seq,p))
            counter_seq+=1


sys.exit()

counter = 0
q = []
for x in p_text:
    counter += 1
    counter_seq = 0
    for p in x:
        counter_seq+=1
        file_name = "t1_{:04d}_{:03d}.mp3".format(counter,counter_seq)
        q.append({'name':file_name,'text':u'{}'.format(p),'counter_p':counter,'sequnse':counter_seq})

for x in q:
    tts = gTTS(text=x['text'], lang='ru')
    tts.save(x['name'])




tasks = Queue()

def worker(n):
    while not tasks.empty():
        task = tasks.get()
        tts = gTTS(text=task['text'], lang='ru')
        tts.save(task['name'])
        gevent.sleep(0)
    print('Quitting time!')


for x in q:
    tasks.put_nowait(x)
    if False:
        if x['counter_p']>100:
            break

gevent.joinall([
    gevent.spawn(worker, 'steve'),
    gevent.spawn(worker, 'john'),
    gevent.spawn(worker, 'nancy'),
    gevent.spawn(worker, 'perry'),
    gevent.spawn(worker, 'sew'),
    gevent.spawn(worker, 'readly'),
])