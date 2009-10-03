#!/usr/bin/env python
import os
import sys             
from optparse import OptionParser
PROG_ROOT = os.path.dirname(os.path.abspath( __file__ ))

from conf import Conf      
from file_system import File, Folder

def main(argv):
    
    parser = OptionParser(usage="%prog [-f] [-q]", version="%prog 0.1a")
    parser.add_option("-a", "--app", 
                        dest = "app", 
                        help = "The application to build. Required.")
    parser.add_option("-t", "--task", 
                        dest = "task", 
                        default = 'default',
                        help = "The task that needs to be run. Optional. Default: `default`.")
    parser.add_option("-p", "--path", 
                        dest = "path", default = '.', 
                        help = "Conche root path. Default: Current Working Directory")
                        
    (options, args) = parser.parse_args()
    if len(args):
        parser.error("Unexpected arguments encountered.")
    
    if not options.app:
        parser.error("You must specify an application.")
        
    path = options.path
    
    cnf = Conf(path)
    cnf.run_task(options.app, options.task)
    
if __name__ == "__main__":
    main(sys.argv[1:])