from subprocess import Popen, PIPE

import settings
from file_system import File, Folder
 
class Builder(object):
    
    def get(self):
        root = Folder(settings.PROJECT_ROOT) 
        root.delete()
        root.make()
        root.parent.cd()      
        git = settings.GIT_PATH + " clone " + settings.GIT_REPOSITORY
        cmd = Popen(git, shell=True)
        cmd.communicate()    
        return cmd.returncode == 0 
        
    def build(self):                         
        root = Folder(settings.PROJECT_ROOT) 
        root.cd()                            
        xcode = settings.XCODE_PATH                 
        xcode += self.makeargs(MMMtarget='XCODE_TARGET', MMMconfiguration='XCODE_CONFIGURATION', SYMROOT='BUILD_ROOT')        
        cmd = Popen(xcode, shell=True)
        cmd.communicate()    
        if cmd.returncode:
            return False                                                                                                    
        app_name = settings.APP_NAME + ".app"    
        app = File(Folder(settings.BUILD_ROOT).child_folder(settings.XCODE_CONFIGURATION).child(app_name))
        release_root = Folder(settings.RELEASE_ROOT)
        if not release_root.exists:
            release_root.make()      
        target = release_root.child_folder(app_name)
        if target.exists:
            target.delete()   
        app.move_to(release_root) 
        return True
        
        
    def makearg(self, actual_key, settings_key):
        if not hasattr(settings, settings_key):
            return None 
        if actual_key.startswith('MMM'):                
            return actual_key.replace("MMM", "-", 1) + " " + getattr(settings, settings_key)
        return actual_key + "=" + getattr(settings, settings_key)            
        
    def makeargs(self, **kwargs):
        args = " "
        for (actual_key, settings_key) in kwargs.iteritems():
            arg = self.makearg(actual_key, settings_key)
            if arg:
                args += arg
                args += " "
        return args        

# Clean

    # 1. Clean up local   


# Build
    
    # 2. Get from git             

    
    # 3. Call xcodebuild                        
    
                        
# Package
    
    # 4. Zip the archive
    # 5. Sign with sparkle
    # 6. Check git tag with current. if different update the tag
    # 7. Update release notes in hyde folder    
    # 8. Run Hyde             
# Test

# Deploy    

# 9. Upload the file to S3
# 10. Upload to Google


