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
class nagios():
    '''Class which converts MonCli reports into Nagios check results and writes them into Spool/Queue.
    This class receives 2 methods and a dictionary object from Krolyk.
    
    self.config     The dictionary 
    
    '''    
    def __init__(self):
        #self.config=None
        #self.acknowledge=None
        #self.block=None
        self.logging = logging.getLogger(__name__)
        self.logging.info('Initialized.')
    def consume(self,ch, method, properties, body):
        print self.config
        print body
        time.sleep(5)
        self.acknowledge(method.delivery_tag)
