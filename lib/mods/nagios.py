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
import logging
import time
class Nagios():
    '''Class which converts MonCli reports into Nagios check results and writes them into Spool/Queue.
    
    This class receives 2 methods and a dictionary object from Krolyk:
    
    self.config         The dictionary containing the parameters coming from this class's section in the Krolyk config file.
    self.acknowledge    Krolyk method which acknowledges the data coming from the queue.
    self.block          Krolyk method to check whether the main loop is going to exit.
    
    '''    
    def __init__(self):
        self.logging = logging.getLogger(__name__)
        self.logging.info('Initialized.')
    def consume(self,ch, method, properties, body):
        #Convert body into a nagios check results
        
        #Write Nagios check result into spool/queue
        
        #Acknowledge message with broker
        self.acknowledge(method.delivery_tag)
