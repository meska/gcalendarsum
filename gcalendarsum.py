#!/usr/bin/env python
#coding:utf-8
# Author:  Marco Mescalchin -- <meskatech@gmail.com>
# Purpose: Sum hours from google calendar
# Created: 02/06/2010
import re,urllib,locale,datetime,calendar
import dateutil.parser
import gdata.calendar.service
from optparse import OptionParser

locale.setlocale(locale.LC_ALL,'')

def_start = datetime.datetime.now().strftime('%Y-%m-01')
def_end = datetime.datetime.now().strftime('%Y-%m-' + str(calendar.monthrange(int(datetime.datetime.now().strftime("%Y")),int(datetime.datetime.now().strftime("%m")))[1]))

parser = OptionParser()
parser.add_option("-u", "--username", dest="username")
parser.add_option("-p", "--password",dest="password")
parser.add_option("-c", "--calendar",dest="calendar")
parser.add_option("-q", "--query",dest="query")
parser.add_option("-s", "--start",dest="start",default=def_start)
parser.add_option("-e", "--end",dest="end",default=def_end)

(options, args) = parser.parse_args()

if not options.username or not options.password or not options.calendar or not options.query:
    parser.error("incorrect number of arguments")

def elapsed_time(seconds, suffixes=['y','w','d','h','m','s'], add_s=False, separator=' '):
    """
    Takes an amount of seconds and turns it into a human-readable amount of time.
    From: http://snipplr.com/view/5713/python-elapsedtime-human-readable-time-span-given-total-seconds/
    """
    # the formatted time string to be returned
    time = []

    # the pieces of time to iterate over (days, hours, minutes, etc)
    # - the first piece in each tuple is the suffix (d, h, w)
    # - the second piece is the length in seconds (a day is 60s * 60m * 24h)
    parts = [(suffixes[0], 60 * 60 * 24 * 7 * 52),
             (suffixes[1], 60 * 60 * 24 * 7),
             (suffixes[2], 60 * 60 * 24),
             (suffixes[3], 60 * 60),
             (suffixes[4], 60),
             (suffixes[5], 1)]

    # for each time piece, grab the value and remaining seconds, and add it to
    # the time string
    for suffix, length in parts:
        value = seconds / length
        if value > 0:
            seconds = seconds % length
            time.append('%s%s' % (str(value),
                                  (suffix, (suffix, suffix + 's')[value > 1])[add_s]))
        if seconds < 1:
            break

    return separator.join(time)

def FullTextQuery(calendar_service, text_query='Tennis'):
    print 'Full text query for events on Primary Calendar: \'%s\'' % ( text_query,)
    query = gdata.calendar.service.CalendarEventQuery('default', 'private', 'full', text_query)
    feed = calendar_service.CalendarQuery(query)
    for i, an_event in enumerate(feed.entry):
        print '\t%s. %s' % (i, an_event.title.text,)
        print '\t\t%s. %s' % (i, an_event.content.text,)
        for a_when in an_event.when:
            print '\t\tStart time: %s' % (a_when.start_time,)
            print '\t\tEnd time:   %s' % (a_when.end_time,)

def SumHours(calendar_service,cal,text_query='',start_date='2010-01-01', end_date='2010-12-31'):
    query = gdata.calendar.service.CalendarEventQuery(cal.gcalcli_username,cal.gcalcli_visibility,cal.gcalcli_projection,text_query)
    query.start_min = start_date
    query.start_max = end_date
    query.max_results = 200

    sum_seconds = 0

    feed = calendar_service.CalendarQuery(query)
    for i, an_event in enumerate(feed.entry):
        print '%s. %s' % (i, an_event.title.text,)
        for a_when in an_event.when:
            print '\tStart time: %s' % (dateutil.parser.parse(a_when.start_time).strftime("%c"),)
            print '\tEnd time:   %s' % (dateutil.parser.parse(a_when.end_time).strftime("%c"),)
            delta = dateutil.parser.parse(a_when.end_time) - dateutil.parser.parse(a_when.start_time)
            sum_seconds+=delta.seconds
    return elapsed_time(sum_seconds)

def getCal(calendar_service,calendar_name,prefix = 'https://www.google.com/calendar/feeds/'):
    """
    get calendar by name,
    thanks to: http://code.google.com/p/gcalcli/
    """
    feed = calendar_service.GetAllCalendarsFeed()
    for cal in feed.entry:
        if cal.title.text == calendar_name:
            cal.gcalcli_altLink = cal.GetAlternateLink().href
            match = re.match('^'+ prefix + '(.*?)/(.*?)/(.*)$',cal.gcalcli_altLink)
            cal.gcalcli_username    = urllib.unquote(match.group(1))
            cal.gcalcli_visibility  = urllib.unquote(match.group(2))
            cal.gcalcli_projection  = urllib.unquote(match.group(3))
            return cal

def PrintUserCalendars(calendar_service):
    feed = calendar_service.GetAllCalendarsFeed()
    print feed.title.text
    for i, a_calendar in enumerate(feed.entry):
        print '%s. %s' % (i, a_calendar.title.text,)

if __name__=='__main__':
    calendar_service = gdata.calendar.service.CalendarService()
    calendar_service.email = options.username
    calendar_service.password = options.password
    calendar_service.source = 'Meska-CalendarSum-0.1'
    calendar_service.ProgrammaticLogin()
    cal = getCal(calendar_service,options.calendar)
    print "Total: %s" % SumHours(calendar_service,cal,options.query,options.start,options.end)


