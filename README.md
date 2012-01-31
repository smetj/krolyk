<pre>

  |  /              |         |    
  ' /    __|  _ \   |  |   |  |  / 
  . \   |    (   |  |  |   |    <  
 _|\_\ _|   \___/  _| \__, | _|\_\ 
                      ____/    

</pre>

Krolyk 0.1 Copyright 2011 by Jelle Smet <development@smetj.net>

		
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

The config file contains a section called "modules"
Each class has its own section under modules.  The name of the module section should match the name of your class.
Your module (which contains the class) should be stored in the mods/ directory.

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

    self.config         The dictionary containing the parameters coming from this class's section in the Krolyk config file.
    self.acknowledge    Krolyk method which acknowledges the data coming from the queue.
    self.block          Krolyk method to check whether the main loop is going to exit.


For bugs please submit a bugreport to: 
    https://github.com/smetj/krolyk/issues


Krolyk is distributed under the Terms of the GNU General Public License Version 3. (http://www.gnu.org/licenses/gpl-3.0.html)

For more information please visit http://www.smetj.net/krolyk/
