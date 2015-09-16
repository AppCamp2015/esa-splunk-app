import sys
from splunklib.modularinput import *
import traceback
import xml.etree.ElementTree as ET

class WorldbankScript(Script):

    def get_scheme(self):
        scheme = Scheme("World bank")
        scheme.description = "Collecting information Data Model Summaries."
        scheme.use_external_validation = True
        scheme.use_single_instance = False

        myarg = Argument("myarg")
        myarg.data_type = Argument.data_type_string
        myarg.description = "Location where datamodel acceleration TSIDX data for the index is stored."
        # myarg.required_on_edit = False
        scheme.add_argument(myarg)

        return scheme

    def validate_input(self, validation_definition):
        pass

    def stream_events(self, inputs, ew):
        ew.log(EventWriter.INFO, "BEGIN stream_events")
        # noinspection PyBroadException
        try:
            for input_name, input_item in inputs.inputs.iteritems():

                from os.path import join, dirname
                import urllib2
                import datetime
                import time

                p = join(dirname(__file__), 'indicators.xml')
                tree = ET.parse(p)
                for child in tree.getroot():
                    indicator_id = child.attrib["id"]
                    url = "http://api.worldbank.org/countries/all/indicators/%s" \
                          "?date=2000:2015&per_page=4000&format=xml" % indicator_id
                    ew.log(EventWriter.INFO, url)
                    try:
                        f = urllib2.urlopen(url)
                    except Exception, e:
                        continue
                    data = ET.parse(f)
                    timestamp = time.mktime(datetime.datetime.strptime('1902', "%Y").timetuple())
                    for wpdata in data.getroot():
                        try:
                            ddd = wpdata.find('{http://www.worldbank.org}date')
                            if ddd.text:
                                timestamp = time.mktime(datetime.datetime.strptime(ddd.text, "%Y").timetuple())
                        except Exception, e:
                            continue

                        event = Event(
                            stanza=input_name,
                            source=url,
                            sourcetype=indicator_id
                        )
                        s = ''
                        for t in wpdata:
                            s += '%s=\"%s\" ' % (t.tag,t.text)
                        event.data = s
                        event.time = timestamp
                        ew.write_event(event)

        except:
            ew.log(EventWriter.FATAL, "%s" % traceback.format_exc().replace('\n','      '))
        ew.log(EventWriter.INFO, "END stream_events")

if __name__ == "__main__":
    sys.exit(WorldbankScript().run(sys.argv))
