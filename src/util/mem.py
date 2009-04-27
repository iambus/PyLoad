#!/usr/bin/python

import time
import datetime
import sys

def now():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

from meminfo import read_memory

##################################################
###################  Recording  ##################
##################################################

class NullStream:
    name = ''
    def write(self, ignore):
        pass
    def flush(self):
        pass

null_stream = NullStream()

console = sys.stdout
log = null_stream

def record_loop(interval, pid):
    while True:
        current_time, current_memory = now(), read_memory(pid)
        log.write( '%s:%8d\n' % (current_time, current_memory) )
        log.flush()
        console.write('%s   %d\n' % (current_time, current_memory))

        time.sleep(interval)

def record(interval, pid = None):
    try:
        console.write('Recording... [Press Ctrl+C to terminate]\n')
        record_loop(interval, pid)
    except KeyboardInterrupt:
        see_log_message = ' Log is saved in %s' % log.name if log.name else ''
        console.write('Finished.%s\n' % see_log_message)

##################################################
############  Command Line Interface  ############
##################################################

def usage():
    print '''Usage: python mem.py [option] [logpath]

When no option specified, start to record Memory usage. (Press Ctrl+C to stop.)
Default log file path is mem-usage.log.

Options:
  -h, --help      Show this help.
  -l, --log       Log path
  -n, --no-log    When recording Memory information, don't write date to log file (simply print to stdout).
  -i, --interval  Delay interval. Default to 3 seconds.
  -q, --quiet     No console output (log to file).

Examples:
  python mem.py 5688
  python mem.py -l logpath 5688
  python mem.py -n 5688
  python mem.py -i 1 5688
  python mem.py -h 5688
'''

def main():
    import sys
    run_command(sys.argv[1:])

def run_command(argv):
    import getopt
    optlist, args = getopt.getopt(argv, 'hp:l:ni:q', [
            'help',
            'pid',
            'log',
            'no-log',
            'interval',
            'quiet',
        ])

    if not args:
        sys.exit("Must specify pid")
    pid = args.pop(0)
    if args:
        sys.exit('Too many args given: %s' % args)

    default_log_path = 'mem-usage.log'
    logpath = None

    default_interval = 3
    interval = default_interval

    nolog = None
    quiet = None

    for o, a in optlist:
        if o in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif o in ('-l', 'log'):
            logpath = a
        elif o in ('-n', 'no-log'):
            nolog = True
        elif o in ('-i', 'interval'):
            interval = float(a)
        elif o in ('-q', 'quiet'):
            quiet = True
        else:
            sys.exit('Unknown option %s' % o)

    if not nolog and not logpath:
        logpath = default_log_path

    if nolog and logpath:
        sys.exit("Bad args: don't give log path if nolog specified")

    if quiet and nolog:
        sys.exit("Can't set 'quiet' option if 'nolog' specified")

    assert nolog or logpath

    if quiet:
        global console
        console = null_stream


    if logpath:
        global log
        log = open(logpath, 'w')
    record(interval, pid)


if __name__ == '__main__':
    main()


# vim: expandtab:shiftwidth=4
