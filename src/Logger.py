
import logging

level = logging.DEBUG

fileHandler = logging.FileHandler('load.log', 'w')
fileFormatter = logging.Formatter('%(asctime)s %(levelname)-8s [%(module)s] %(message)s')
fileHandler.setFormatter(fileFormatter)

console = logging.StreamHandler()
consoleFormatter = logging.Formatter('%(asctime)s,%(msecs)03d %(levelname)-8s [%(module)s] %(message)s', '%H:%M:%S')
console.setFormatter(consoleFormatter)


logger = logging.getLogger()
logger.setLevel(level)

logger.addHandler(fileHandler)
logger.addHandler(console)


def getLogger(m = None):
	if m == None:
		return logger

	fileHandler = logging.FileHandler('load.log', 'w')
	fileFormatter = logging.Formatter('%(asctime)s %(levelname)-8s ['+m+'] %(message)s')
	fileHandler.setFormatter(fileFormatter)

	console = logging.StreamHandler()
	consoleFormatter = logging.Formatter('%(asctime)s,%(msecs)03d %(levelname)-8s ['+m+'] [%(module)s] %(message)s', '%H:%M:%S')
	console.setFormatter(consoleFormatter)


	log = logging.getLogger(m)
	log.setLevel(level)

	log.addHandler(fileHandler)
	log.addHandler(console)
	return log

if __name__ == '__main__':
	log = getLogger()
	log.warn('w')
	log.info('i')
	log.debug('d')
	log.error('e')
	log.fatal('f')

