import sys
from buildflow import Builder

def main(argv):   
    builder = Builder()
    # if not builder.get():
    #   print "Get failed. Terminating xbuild." 
    #   return      
    # if not builder.build():
    #   print "Build failed. Terminating xbuild." 
    #   return         
    if not builder.get_version():
      print "Build failed. Terminating xbuild." 
      return      
    # if not builder.package():
    #   print "Packaging failed. Terminating xbuild." 
    #   return   
    if not builder.update_git():
      print "Updating version control failed. Terminating xbuild." 
      return         
    # if not builder.deploy():
    #       print "Deployment failed. Terminating xbuild." 
    #       return      
     
    print "Build Succeeded."
        
    

if __name__ == "__main__":
    main(sys.argv[1:])