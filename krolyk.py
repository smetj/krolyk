#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       krolyk.py
#       
#       Copyright 2011 Jelle <jelle@indigo>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
#       

import logging
import os
import sys
from logging.handlers import SysLogHandler
from optparse import OptionParser
import time
from multiprocessing import Process, Manager, Queue
from ctypes import c_char_p


__version__='0.1'

class Logger():
	'''Creates a logger class.'''
	def __init__(self, loglevel='DEBUG'):
		self.loglevel=loglevel
		self.screen_format=logging.Formatter('%(asctime)s %(levelname)s::%(processName)s:%(message)s')
		self.syslog_format=logging.Formatter('NetCrawl %(processName)s %(message)s')
	def get(self,name=None, scrlog=True, txtlog=True):
		log = logging.getLogger(name)
		log.setLevel(self.loglevel)
		syslog=SysLogHandler(address='/dev/log')
		syslog.setFormatter(self.syslog_format)
		log.addHandler(syslog)	

		if scrlog == True:
			scr_handler = logging.StreamHandler()
			scr_handler.setFormatter(self.screen_format)
			log.addHandler(scr_handler)
		return log
class Worker(Process):
	'''Consumes from RabbitMQ and writes into Nagios named pipe.'''
	def __init__(self,logger,block):
		Process.__init__(self)
		self.logger=logger
		self.block=block
		self.daemon=True
		self.start()
	def run(self):
		self.logger.debug('Started.')
		while self.block() == True:
			try:
				time.sleep(0.1)
			except:
				pass
		
		
class Server():
	'''Server class handling process control, startup & shutdown'''
	def __init__(self,config=None):
		self.cfg = config
		self.procs=[]
		self.block=True
	def lock(self):
		return self.block
	def doPID(self):
		if self.checkPIDRunning() == False:
			self.writePID()
	def checkPIDRunning(self):
		'''Checks whether the pid file exists and if it does, checks whether a process is running with that pid.
		Returns False when no process is running with that pid otherwise True'''
		if os.path.isfile(self.cfg['pid']):
			try:
				pid_file = open(self.cfg['pid'], 'r')
				pid=pid_file.readline()
				pid_file.close()
			except Exception as err:
				sys.stderr.write('I could not open the pid file. Reason: %s\n'%(err))
				sys.exit(1)
		try:
			os.kill(int(pid),0)
		except:
			return False
		else:
			sys.stderr.write('There is already a process running with pid %s\n'%(pid))
			sys.exit(1)				
	def writePID(self):
		try:
			pid = open ( self.cfg['pid'], 'w' )
			pid.write (str(os.getpid()))
			pid.close()
		except Exception as err:
			sys.stderr.write('I could not write the pid file. Reason: %s\n'%(err))
			sys.exit(1)
	def deletePID(self):
		try:
			os.remove ( self.cfg['pid'] )
		except:
			pass				
	def start(self):
		#Creating logging object
		logger = Logger()
		
		self.logger=logger.get(name=self.__class__.__name__)
		self.logger.info('started')

		#Write PID
		self.doPID()
		
		#Start Consumer
		self.procs.append(Worker(logger = self.logger, block=self.lock))
		
					
		while self.lock()==True:
			time.sleep(0.1)
		
		self.logger.info('Exit')
	def stop(self):
		self.block=False
		for process in self.procs:
			process.join()
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option("--pid", dest="pid", default="file.pid", type="string", help="The location of the pid file." )
	parser.add_option("--broker", dest="broker", default="localhost", type="string", help="The hostname of the RabbitMQ broker." )
	parser.add_option("--user", dest="user", default="guest", type="string", help="The user used to connect to the broker." )
	parser.add_option("--password", dest="password", default="password", type="string", help="The password for user." )
	parser.add_option("--exchange", dest="exchange", default="exchange", type="string", help="The exchange to dump check results to." )
	parser.add_option("--pipe", dest="pipe", default="/opt/nagios/var/nagios.cmd", type="string", help="Nagios named pipe." )
	(cli_options,cli_actions)=parser.parse_args()
	
	try:
		server=Server(config = vars(cli_options))
		
		if cli_actions[0] == 'start':
			with daemon.DaemonContext():
				server.start()
		elif cli_actions[0] == 'debug':
			server.start()
	except Exception as err:
		print str(err)
	except KeyboardInterrupt:
		server.stop()
		server.deletePID()
