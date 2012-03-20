#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       help.py
#       
#       Copyright 2012 Jelle smet development@smetj.net
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

__version__= '0.3'

class Help():
    def __init__(self):
        print ('Krolyk v%s by Jelle Smet development@smetj.net' %(__version__))
        print ('''
        
Description:

    Krolyk is a framework which allows you to easily register a Python class as a process 
    to consume and process data coming from a RabbitMQ message broker.
    
Usage:
        
    krolyk command --config name
    
    Valid commands:

        start       Starts Krolyk and forks into the background.        (not implemented yet)
        stop        Stops Krolyk.                                       (not implemented yet)
        debug       Starts Krolyk into the foreground.
        help        Shows this help message.
    

    Parameters:

        --config    Defines the location of the config file.


Config file:

The config file contains a section called "plugins"
Each class has its own section under plugins.  The name of the module section should match the name of your class.
Your module (which contains the class) should be stored in the plugins/ directory.

Each section should contain at least following parameters:
    
        "_enabled"       = True
        "_workers"       = 5
        "_broker"        = "sandbox"
        "_queue"         = "molog_output"
        "_user"          = "guest"
        "_password"      = "guest"

These are used to connect your class to the right queue.
You can define as much extra parameters as you want (without leading underscore)

Your class will receive 2 methods and 1 dictionary object from the Krolyk framework:

    self.acknowledge    Krolyk method which acknowledges the data coming from the queue.
    self.block          Krolyk method to check whether the main loop is going to exit.


For bugs please submit a bugreport to: 
    https://github.com/smetj/krolyk/issues



Krolyk is distributed under the Terms of the GNU General Public License Version 3. (http://www.gnu.org/licenses/gpl-3.0.html)

For more information please visit http://www.smetj.net/krolyk/
        ''')
