#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       tools.py
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

from multiprocessing import Process, Manager, Queue
from pika.adapters import SelectConnection
from string import find
import logging
import os
import sys
import pika
import time

class Worker(Process):
    
    def __init__(self,config,plugin,block):
        Process.__init__(self)
        self.logging = logging.getLogger(__name__)
        self.c=config
        self.plugin=plugin
        self.block=block
        self.daemon=True
    
    def run(self):
        period=0
        while self.block() == True:
            try:
                time.sleep(period)
                period+=1
                self.logging.debug('Started.')
                credentials = pika.PlainCredentials(self.c['_user'],self.c['_password'])
                self.parameters = pika.ConnectionParameters(self.c['_broker'],credentials=credentials)
                self.connection = SelectConnection(self.parameters,self.__on_connected) 
                self.connection.ioloop.start()
            except KeyboardInterrupt:
                try:
                    self.connection.close()
                    self.connection.ioloop.start()
                except:
                    pass
                break
            except:
                self.logging.debug('Lost connection to Broker, sleeping %s seconds and restarting.' % (period))
        
    def __on_connected(self,connection):
        self.logging.info('Connecting to broker.')
        connection.channel(self.__on_channel_open)
    
    def __on_channel_open(self,new_channel):
        self.channel = new_channel
        self.__initialize()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.plugin.consume, queue = self.c['_queue'])
    
    def __initialize(self):
        self.logging.debug('Creating queues and bindings on broker.')                
        self.channel.queue_declare(queue=self.c['_queue'],durable=True)
        self.plugin.acknowledge=self.acknowledge
    
    def acknowledge(self,tag):
        self.channel.basic_ack(delivery_tag=tag)


class ModManager():
  
    def __init__(self, cfg, block):
        self.logging = logging.getLogger(__name__)
        self.cfg=cfg
        self.block=block
        self.register={}
        self.__load()        
  
    def __load(self):
        for module in self.cfg:
            if self.cfg[module]['_enabled'] == 'True':
                try:
                    self.logging.info('Module %s enabled importing.' % module)
                    import plugins
                    self.register[module]={}
                    for counter in range(int(self.cfg[module]['_workers'])):
                        self.register[module][counter] = Worker(config=self.cfg[module],
                                                                plugin=getattr(plugins,module)(config=self.__cleanConfig(self.cfg[module])),
                                                                block=self.block)
                        #self.register[module][counter]['mod'].acknowledge = self.register[module][counter]['proc'].acknowledge
                        self.register[module][counter].start()
                except Exception as err:
                    self.logging.warning('Failed to load module %s. Reason: %s' % (module, err))
            else:
                self.logging.info('Module %s disabled.' % module)
  
    def __cleanConfig(self, config):
        cleaned={}
        for item in config:
            if find(item,'_') !=0:
                cleaned[item]=config[item]
        return cleaned
