#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       skeleton.py
#       
#       Copyright 2012 Jelle Smet development@smetj.net
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
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

# Disclaimer:   This plugin should be able to write directly in the Nagios spool 
#               file instead of opening/closing Nagios named pipe for each message.

import logging
import time
import json
from socket import socket
import string
import xml.utils.iso8601

class Moncli2Graphite():
    '''Class which loads Moncli metrics into graphite.
    
    This class receives 2 methods
    
    self.acknowledge    Krolyk method which acknowledges the data coming from the queue.
    self.block          Krolyk method to check whether the main loop is going to exit.
    
    '''    
    def __init__(self,config):
        self.logging = logging.getLogger(__name__)
        self.config = config
        
        #Receives acknowledgement function from Krolyk.
        self.acknowledge = None
        
        #Receives Krolyk framework lock.
        self.block = block
        
        self.createSocketConnection()
        
        self.logging.info('Initialized.')
        
    def consume(self,ch, method, properties, body):
        '''The callback function which is called by Krolyk and which delivers the actual content from RabbitMQ.'''
        try:
            document = json.loads(body)
            data =[]
            if "graphite:process" in document['tags']:
                for metric in document['plugin']['metrics']:
                    #This pre_ filtering can be skipped in the latest moncli release
                    if not string.find(metric,'pre_') == 0:
                    	#moncli.hostname.hadoop.dn.dfs.blockChecksumOp_avg_time
                        data.append ("%s.%s.%s.%s %s %s" % ( self.config['carbon_prefix'],
                                                             document['report']['source'].split('.')[0],
                                                             document['plugin']['name'],
                                                             metric,
                                                             document['plugin']['metrics'][metric],
                                                             xml.utils.iso8601.parse(document['report']['time'])))
                self.writeSocket(data)
                self.logging.info('Data for host %s send to Graphite. Tags: %s' % (document['report']['source'],document['tags']) )
                
            self.acknowledge(method.delivery_tag)
                
        except Exception as err:
            self.logging.warning('An error occurred: %s' % err)
    def createSocketConnection(self):
        self.socket = socket()
        while self.block() == True:
            try:
                self.socket.connect( (self.config['carbon_server'],int(self.config['carbon_port'])) )
                break
            except Exception as err:
                self.logging.warning ('Can not connect to to Carbon. Reason: %s' % err)        
                time.sleep(1)
    def writeSocket(self,data):
	#print '\n'.join(data) + '\n'
        while self.block() == True:
            try:
                self.socket.sendall('\n'.join(data) + '\n')
                break
            except:
                self.createSocketConnection()
        
        
