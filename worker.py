#!/usr/bin/python
from Printer.Adafruit_Thermal import *

printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

def printissue(issue):
    printer.wake()
    printer.flush()
    printer.setDefault()

    printer.setLineHeight(20)
    printer.justify('C')
    printer.setSize('L')
    printer.inverseOn()

    printer.println('  @%s  ' % (issue['assignee']))

    printer.inverseOff()
    printer.setLineHeight()
    printer.setSize('M')

    printer.println('%s #%s' % (issue['repo'], str(issue['number'])))

    printer.setSize('S')

    printer.println('%s' % (issue['timestamp']))

    printer.feed(1)
    printer.justify('L')
    printer.setLineHeight(40)

    printer.println(issue['title'])

    for label in issue['labels'].split(','):
        printer.println('*** %s' % (label.upper()))

    printer.setLineHeight()
    printer.feed(3)

    printer.setDefault()
    printer.flush()
    printer.sleep()

printissue({
    'assignee': 'nearengine',
    'repo': 'shiplet.co',
    'number': 420,
    'timestamp': 'Apr 20 2015 4:20:00',
    'title': 'Stuff is broke',
    'labels': 'P-High,C-Low'
})
