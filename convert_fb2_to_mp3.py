# -*- coding: utf-8 -*-
import re
import codecs


from bs4 import BeautifulSoup
import gevent
from gevent.queue import Queue
from gtts import gTTS

filename = "some.fb2"
with codecs.open(filename,'r',encoding='utf8') as f:
    content = f.read()

soup = BeautifulSoup(content,"lxml")
text = soup.find_all("p")

p_text = []
for x in text:
    seq = re.split('(?<=[.!?])\s',x.text)
    p_text.append(seq)

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

if False:
    for x in q:
        tasks.put_nowait(x)
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