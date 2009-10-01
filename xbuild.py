import sys
from buildflow import Builder

def main(argv):
    # if not Builder().get():
    #       print "Get failed. Terminating xbuild." 
    #       return      
    # if not Builder().build():
    #    print "Build failed. Terminating xbuild." 
    #    return         
    if not Builder().package():
      print "Packaging failed. Terminating xbuild." 
      return   
     
    print "Build Succeeded."
        
    

if __name__ == "__main__":
    main(sys.argv[1:])