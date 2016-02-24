# -*- coding: utf-8 -*-
import re
import codecs
import zipfile
import os
import sys
import logging
import traceback

from bs4 import BeautifulSoup
import gevent
from gevent.queue import Queue
from gtts import gTTS

logging.basicConfig(filename="log.log", level=logging.ERROR,
                            format="%(levelname)s  [%(asctime)-16s [%(filename)18s:%(lineno)-4s - %(funcName)20s() ]:\
                             [%(name)s:%(lineno)s] %(message)s")

filename = "some.fb2.zip"
path_out = "Y:/test_1"
number_of_threads = 3
max_count_mp3 = 0

try:
    if not os.path.exists(path_out):
        os.makedirs(path_out)


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

    print "zip read done"

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

    print "parse fb2 done"

    counter = 0
    q = []
    for x in p_text:
        counter += 1
        counter_seq = 0
        for p in x:
            counter_seq+=1
            file_name = "{}/t1_{:04d}_{:03d}.mp3".format(path_out,counter,counter_seq)
            q.append({'name':file_name,'text':u'{}'.format(p),'counter_p':counter,'sequnse':counter_seq})

    """
    for x in q:
        tts = gTTS(text=x['text'], lang='ru')
        tts.save(x['name'])
    """ 

    print "creating list of text done"


    tasks = Queue()

    def worker(n):
        error_counter = 0
        max_error_counter = 5
        while error_counter < max_error_counter and not tasks.empty():
            try:
                task = tasks.get()
                while error_counter < max_error_counter:
                    try:
                        tts = gTTS(text=task['text'], lang='ru')
                        tts.save(task['name'])
                        error_counter = 0
                    except Exception as e:
                        logging.exception("Error in gtts: {}".format(e))
                        logging.exception(traceback.format_exc())            
                        error_counter += 1
                if  error_counter >= max_error_counter:
                    logging.error("File not created : [{}] with text [{}]".format(task['name'],task['text'],))    
                gevent.sleep(0)
            except Exception as e:
                logging.exception("Error in gtts: {}".format(e))
                logging.exception(traceback.format_exc())
                
        print('Quitting time!')

    counter = 0
    for x in q:
        tasks.put_nowait(x)
        if max_count_mp3 > 0:
            counter += 1
            if True:    
                if counter>20:
                    break

    print "creating queueu of tasks done"

    print "generation mp3"

    threads = []
    for x in xrange(number_of_threads):
        threads.append(gevent.spawn(worker, "worker_{}".format(x)))

    gevent.joinall(threads)
except Exception as e:
    logging.exception("Error in convert_fb2_to_mp3.py: {}".format(e))
    logging.exception(traceback.format_exc())
    raise