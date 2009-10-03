#!/usr/bin/env python
import os
import sys                       
import string
from optparse import OptionParser
PROG_ROOT = os.path.dirname(os.path.abspath( __file__ ))

from file_system import File, Folder

def main(argv):
    
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 0.1a")       
    parser.add_option("-a", "--app", 
                        dest = "app", 
                        help = "The application to build. Required.")
    parser.add_option("-p", "--path", 
                        dest = "path", default = '.', 
                        help = "Conche root path. Default: Current Working Directory. Optional. Default: `%default`")
                        
    (options, args) = parser.parse_args()
    if len(args):
        parser.error("Unexpected arguments encountered.")
    
    if not options.app:
        parser.error("You must specify an application.")

    path = options.path  
    
    if path == ".":
        path = os.getcwdu()
   
    target = Folder(path) 
    if not target.exists:
        target.make()
    source = Folder(PROG_ROOT).child_folder('template')
    target.copy_contents_of(source, incremental=True)
    
    apps = File(target.child('apps.yaml'))
    appsString = apps.read_all()
    appsString = string.Template(appsString).safe_substitute(init_app = options.app)
    apps.write(appsString)
        
if __name__ == "__main__":
    main(sys.argv[1:])