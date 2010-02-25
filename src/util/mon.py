
import sys
import time
import datetime
from proc import Process, SystemProcess

def now():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def now_time():
	return datetime.datetime.now().strftime('%H:%M:%S')

def now_date():
	return datetime.datetime.now().strftime('%Y-%m-%d')

##################################################
###################  Monitor  ####################
##################################################

class Monitor:
    def __init__(self, log_path, interval, system, pids):
        self.log_path = log_path
        self.log = open(log_path, 'w')
        self.console = sys.stdout
        self.interval = interval
        self.system = system and SystemProcess() or None
        self.pids = pids
        self.processes = map(Process, pids)

    def start(self):
        try:
            self.console.write('Recording... [Press Ctrl+C to terminate]\n')
            self.loop()
        except KeyboardInterrupt:
            see_log_message = ' Log is saved in %s' % self.log_path
            self.console.write('Finished.%s\n' % see_log_message)

    def loop(self):
        self.print_heading()
        for process in self.processes:
            if self.system:
                self.system.get_cpu()
            for process in self.processes:
                process.get_cpu()
        if self.interval < 10:
            time.sleep(self.interval)
        else:
            time.sleep(10)
        while True:
            self.record()
            time.sleep(self.interval)

    def print_heading(self):
        columns = []
        columns.append( 'Date' )
        columns.append( 'Time' )
        if self.system:
            columns.append( 'CPU' )
        for process in self.processes:
            pid = process.pid
            columns.append( '%d cpu' % pid )
            columns.append( '%d vm' % pid )
            columns.append( '%d mem' % pid )

        self.print_line(columns)

    def record(self):
        columns = []
        columns.append(now_date())
        columns.append(now_time())
        if self.system:
            cpu = self.system.get_cpu()
            columns.append( cpu )
        for process in self.processes:
            cpu = process.get_cpu()
            vm, pm = process.get_memories()
            columns.append( cpu )
            columns.append( vm )
            columns.append( pm )

        self.print_line(columns)

    def print_line(self, values):
        self.log.write( ','.join(map(self.format_column, values)) )
        self.log.write( '\n' )
        self.log.flush()

    def format_column(self, value):
        if type(value) == float:
            return '%10.2f' % value
        elif type(value) == int:
            return '%10d' % value
        else:
            value = str(value)
            if ' ' not in value:
                return '%10s' % value
            else:
                return '%10s' % ('"%s"'%value)

##################################################
############  Command Line Interface  ############
##################################################

def usage():
    print '''Usage: python mon.py [option] pid...

When no pid specified, start to record system CPU usage. (Press Ctrl+C to stop.)
Default log file path is pymon.log.

Options:
  -h, --help        Show this help
  -s, --system      Monitor system CPU (default)
  -S, --non-system  Don't monitor system CPU
  -l, --log         Specify log path
  -i, --interval    Delay interval (by seconds). Default to 3 seconds

Examples:
  python mon.py
  python mon.py -l your-pymon-path.csv
  python mon.py 1123 2234
  python mon.py -S 7762
  python mon.py -S java
  python mon.py -h
'''

def main():
    import sys
    run_command(sys.argv[1:])

def run_command(argv):
    import getopt
    optlist, args = getopt.getopt(argv, 'hsSi:l:', [
            'help',
            'system',
            'no-system',
            'log',
            'interval',
        ])

    pid = None

    log_path = 'pymon.log'

    default_interval = 3
    interval = default_interval

    monitor_system = True
    pids = []

    for o, a in optlist:
        if o in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif o in ('-s', 'system'):
            monitor_system = True
        elif o in ('-S', 'no-system'):
            monitor_system = False
        elif o in ('-i', 'interval'):
            interval = float(a)
        elif o in ('-l', 'log'):
            log_path = a
        else:
            sys.exit('Unknown option %s' % o)

    if args:
        for p in args:
            try:
                p = int(p)
            except:
                pass
            pids.append(p)
    if not pids:
        monitor_system = True


    log = open(log_path, 'w')
    mon = Monitor(log_path = log_path, interval = interval, system=monitor_system, pids = pids)
    mon.start()


if __name__ == '__main__':
    main()



# vim: expandtab:shiftwidth=4
