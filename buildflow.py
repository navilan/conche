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

    def package(self):            
         app_name = settings.APP_NAME + ".app"                              
         release_root = Folder(settings.RELEASE_ROOT)
         app = release_root.child_folder(app_name)
         zip_path = app.zzip()                                                                       
         sign_cmd = 'openssl dgst -sha1 -binary < "' + zip_path + '" | openssl dgst -dss1 -sign "' + settings.SPARKLE_PRI_KEY + '" | openssl enc -base64'                                     
         cmd = Popen(sign_cmd, stdout=PIPE, shell=True)
         key = cmd.communicate()[0]    
         
         if not cmd.returncode == 0:
             return False           
             
         cmd = Popen(settings.SUVerifier + ' "'  + zip_path + '" "' + key + '" "' + settings.SPARKLE_PUB_KEY + '"', shell=True)
         cmd.communicate()    
         return cmd.returncode == 0
        
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
        
        
                   

                        
# Package
    
    # 4. Zip the archive
    # 5. Sign with sparkle   
    # 6. Generate appcast
    # 7. Check git tag with current. if different update the tag
    # 8. Update release notes in hyde folder    
    # 9. Run Hyde             
# Test

# Deploy    

# 9. Upload the file to S3
# 10. Upload to Google


