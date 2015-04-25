#!/usr/bin/python
from Printer.Adafruit_Thermal import *

def print_issue(issue):
    printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

    printer.wake()
    printer.flush()
    printer.setDefault()

    printer.setLineHeight(20)
    printer.justify('C')
    printer.setSize('L')
    printer.inverseOn()

    printer.println('  @%s  ' % (issue['assignee']))

    printer.inverseOff()
    printer.setSize('M')

    printer.println('%s #%s' % (issue['repo'], str(issue['number'])))

    printer.setSize('S')

    printer.println('%s' % (issue['timestamp']))

    printer.feed(1)
    printer.setLineHeight(40)
    printer.justify('L')

    printer.println(issue['title'])

    for label in issue['labels'].split(','):
        printer.println('*** %s' % (label.upper()))

    printer.feed(3)

    printer.setDefault()
    printer.flush()
    printer.sleep()
