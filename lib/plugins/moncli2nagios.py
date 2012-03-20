#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       nagios.py
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
from xml.utils.iso8601 import parse #pip install pyxml

class Moncli2Nagios():
    '''Class which converts MonCli reports into Nagios check results and writes them into Spool/Queue.
    
    This class receives 2 methods
    
    self.acknowledge    Krolyk method which acknowledges the data coming from the queue.
    self.block          Krolyk method to check whether the main loop is going to exit.
    
    '''    
    def __init__(self,config):
        self.logging = logging.getLogger(__name__)
        self.config = config
        self.logging.info('Initialized.')
        self.service = { 'OK':0, 'Warning':1, 'Critical':2, 'Unknown':3 }
        self.host = { 'Up':0, 'Down':1, 'Unreachable':2 }
        
    def consume(self,ch, method, properties, body):
        '''The callback function which is called by Krolyk and which delivers the actual content from RabbitMQ.'''
        try:
            document = json.loads(body)
            if "nagios:process" in document['tags']:
                (type,status) = self.calculateStatus(document['evaluators'],self.getType(tags=document['tags']))
                file_content = self.createData(type,status,document)
                self.writeFile(file_content)            
            self.acknowledge(method.delivery_tag)
        except Exception as err:
            self.logging.warning('An error occurred: %s' % err)
            
    def createData(self, type, status, document):
        '''Convenience function which calls the right function based upon type'''
        if type == 'service':
            return self.createService(status,document)
        elif type == 'host':
            return self.createHost(status,document)
            
    def createService(self, status, document):
        '''Converts a document into a Nagios service_check_result format.'''
        return ( '[%s] PROCESS_SERVICE_CHECK_RESULT;%s;%s;%s;%s - %s\\n<pre>%s</pre>\\n|%s' % 
                        (parse(document['report']['time']),
                        document['destination']['name'],
                        document['destination']['subject'],
                        self.service[status],
                        status,
                        document['report']['message'],
                        '\\n'.join(document['plugin']['verbose'][0:15]),
                        self.createPerfdata(document)) )
                           
    def createHost(self, status, document):
        '''Converts a document into a Nagios host_check_result format.'''
        pass
 
    def createPerfdata(self, document):
        '''Creates Nagios style performance data out of a document.'''
        if document.has_key('nagios:performance'):
            perfdata=[]
            for evaluator in sorted(document['evaluators']):
                if document['evaluators'][evaluator]['metric'] in [ '%', 's', 'us', 'ms', 'B', 'KB', 'MB', 'TB', 'c' ]:
                    perfdata.append("'%s'=%s%s;;;;" % (evaluator, document['evaluators'][evaluator]['value'], document['evaluators'][evaluator]['metric']))
                else:
                    perfdata.append("'%s'=%s;;;;" % (evaluator, document['evaluators'][evaluator]['value']))
            perfdata.append("[%s]" % document['destination']['subject'])
            return " ".join(perfdata)
        else:
            return ''
        
    def writeFile(self, data):
        '''Writes into the Nagios named pipe. Should rewrite this into writing directly to the spool directory.
        Open closes on each incoming check result is not efficient.'''
        if data != None and data != '':
            cmd=open(self.config['pipe'],'w')
            cmd.write(data+'\n')
            cmd.close()            
        else:
            pass
  
    def calculateStatus(self, evaluators,type):
        '''Calculates the worst status out of each evaluator status'''
        status_list=[]
        for evaluator in evaluators:
            status_list.append(evaluators[evaluator]["status"])
        status = self.chooseStatus(status_list,type)
        return (type, status)
        
    def chooseStatus(self, status_list, type):
        '''Does the actual work figuring out which is the worst status.'''
        global_status=None
        if type == 'service':
            global_status = 'OK'
            for status in status_list:
                if status == 'Critical' or status == 'Unknown':
                    global_status = status
                    break
                if status == 'Warning' and status == 'OK':
                    global_status = status
        if type == 'host':
            global_status = 'Down'
            for status in status_list:
                if status == 'Down' or status == 'Unknown':
                    global_status = status
                    break
        return global_status
        
    def getType(self, tags=[]):
        '''Based upon the Status of the evaluators, this function determines whether we're dealing with a host or service.'''
        if "nagios:service" in tags:
                return 'service'
        elif "nagios:host" in tags:
                return 'host'
