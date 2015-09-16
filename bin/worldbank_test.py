import sys
from splunklib.modularinput import *
import traceback
import xml.etree.ElementTree as ET


from os.path import join, dirname
import urllib2
import datetime
import time

p = join(dirname(__file__), 'indicators.txt')
with open(p) as fin:
    content = fin.readlines()

pp = '%s.log'
with open(pp,'w') as ff:

    for entry in content:
        indicator_id = entry.replace("\n", "")
        url = "http://api.worldbank.org/countries/all/indicators/%s?date=2000:2015&per_page=4000&format=xml" % indicator_id
        print url
        f = urllib2.urlopen(url)
        data = ET.parse(f)
        timestamp = time.mktime(datetime.datetime.strptime('1902', "%Y").timetuple())
        for wpdata in data.getroot():
            try:
                timestamp = time.mktime(datetime.datetime.strptime(wpdata.find('{http://www.worldbank.org}date').text, "%Y").timetuple())
            except Exception, e:
                continue

            s = 'time=%s ' % timestamp
            for t in wpdata:
                s += '%s=\"%s\" ' % (t.tag,t.text)
            ff.write('%s\n'%s)
