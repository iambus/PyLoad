
import time
import sys

from cpuinfo import read_current_point, cpu_percentage_between_points

##################################################
###################  Recording  ##################
##################################################

def read_current_time_and_cpu(pid = None):
    return time.time(), read_current_point(pid)

def record_loop(logname, interval, pid = None):
    fp = open(logname, 'w') if logname else None
    last_time, last_cpu = read_current_time_and_cpu(pid)
    while True:
        time.sleep(interval)
        current_time, current_cpu = read_current_time_and_cpu(pid)
        current_cpu_usage = cpu_percentage_between_points(last_cpu, current_cpu)
        if fp:
            fp.write( '%s:%16s:%8.2f\n' % (last_time, current_time, current_cpu_usage) )
            fp.flush()
        print '%.02f' % current_cpu_usage

        last_time, last_cpu = current_time, current_cpu

def record(logname, interval, pid = None):
    try:
        print 'Recording... [Press Ctrl+C to terminate]'
        record_loop(logname, interval, pid)
    except KeyboardInterrupt:
        see_log_message = ' Log is saved in %s' % logname if logname else ''
        print 'Finished.%s' % see_log_message

##################################################
################  Read Log File  #################
##################################################


def extract_from_text(text):
    import re
    lines = text.split('\n')
    lines = map(lambda x:re.sub('#.*', '', x), lines) # remove comments
    lines = map(lambda x:x.strip(), lines) # remove blanks
    lines = map(lambda x:x.rstrip('%'), lines) # remove tailing %
    lines = filter(lambda x:x, lines) # remove blank lines
    return [map(float, re.split(r'\s*:\s*', line)) for line in lines]

def compute_all_cpu(values):
    if not values:
        return '<no data>'
    total_time = 0.0
    total_cpu = 0.0
    for t1, t2, u in values:
        total_time += t2 - t1
        total_cpu += (t2 - t1) * u

    return total_cpu/total_time

def compute_text(text):
    print '%.02f%%' % compute_all_cpu( extract_from_text(text) )

def file_text(path):
    fp = open(path)
    try:
        return fp.read()
    finally:
        fp.close()

def compute_file(path):
    compute_text(file_text(path))

##################################################
##############  Analysis Log File  ###############
##################################################

def format_seconds(ts):
    #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
    return time.strftime('%H:%M:%S', time.localtime(ts))

def percentage_bits(u):
    n = int(u+0.5)
    f = 100
    m = f - n
    b = 0
    assert type(n) == int
    n, m, b = n/2, m/2, n%2
    assert (n + m + b) == f/2, '%s + %s + %s != %s / 2' % (n, m, b, f)
    return '[' + '=' * n + '>' * b + '.' * m + ']'

def analysis_text(text):
    values = extract_from_text(text)
    for t1, t2, u in values:
        s1 = format_seconds(t1)
        s2 = format_seconds(t2)
        u = int(u+0.5)
        us = percentage_bits(u)
        print '%s ~ %s %3d%% %s' % (s1, s2, u, us)

def analysis_file(path):
    analysis_text(file_text(path))

##################################################
############  Command Line Interface  ############
##################################################

def usage():
    print '''Usage: python cpu.py [option] [logpath]

When no option specified, start to record CPU usage. (Press Ctrl+C to stop.)
Default log file path is cpu-usage.log.

Options:
  -h, --help      Show this help.
  -p, --pid       If pid is specified, it will record CPU usage for single process
  -r, --read      Compute the average CPU usage in log file.
  -a, --analysis  Display CPU information in log file.
  -n, --no-log    When recording CPU information, don't write date to log file (simply print to stdout).
  -i, --interval  Delay interval. Default to 3 seconds.

Examples:
  python cpu.py [logpath]
  python cpu.py -p 5678 [logpath]
  python cpu.py -r [logpath]
  python cpu.py -a [logpath]
  python cpu.py -n
  python cpu.py -i 1
  python cpu.py -h
'''

def main():
    import sys
    run_command(sys.argv[1:])

def run_command(argv):
    import getopt
    optlist, args = getopt.getopt(argv, 'hp:arni:', [
            'help',
            'pid',
            'analysis',
            'read',
            'no-log',
            'interval',
        ])

    pid = None

    default_log_path = 'cpu-usage.log'
    logpath = None

    default_interval = 3
    interval = default_interval

    read_mode = None
    nolog = None

    for o, a in optlist:
        if o in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif o in ('-p', 'pid'):
            pid = int(a)
        elif o in ('-r', 'read'):
            read_mode = 'r'
        elif o in ('-a', 'Analysis'):
            read_mode = 'a'
        elif o in ('-n', 'no-log'):
            nolog = True
        elif o in ('-i', 'interval'):
            interval = float(a)
        else:
            sys.exit('Unknown option %s' % o)

    if not nolog and not logpath:
        logpath = args.pop() if args else default_log_path

    if args:
        sys.exit('Too many args given: %s' % args)

    if nolog and read_mode:
        sys.exit("Bad args: log path must be given in read mode")

    if nolog and logpath:
        sys.exit("Bad args: don't give log path if nolog specified")

    assert nolog or logpath
    assert not read_mode or logpath

    if read_mode and pid:
        sys.exit("-p (--pid) is only for recording.")

    if read_mode == 'r':
        compute_file(logpath)
    elif read_mode == 'a':
        analysis_file(logpath)
    else:
        record(logpath, interval, pid)


if __name__ == '__main__':
    main()


# vim: expandtab:shiftwidth=4
