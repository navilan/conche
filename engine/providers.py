import sys
import string
from subprocess import Popen, PIPE
from file_system import Folder, File


class Provider(object):

     def __init__(self, ptype, app, conf):
        self.type = ptype
        self.app = app
        self.settings = conf.get('settings', {})


     def perform_task(self, task_name):
         task = getattr(self, task_name)
         if not task:
             self.fail('No Task with name:' + task_name)
         task()

     def execute(self, cmdstring, logresult=True):
         cmd = Popen(cmdstring, stdout=PIPE, shell=True)
         cmdresult = cmd.communicate()[0]
         if cmd.returncode:
             self.fail(cmdresult)
         self.app.logger.info(cmdresult)
         return cmdresult

     def eval(self, setting_name):
         return self.app.substitute(self.settings[setting_name])

     def fail(self, reason, error=None):
         self.app.logger.error(
             string.Template(
             '$provider failed bacause of this:$reason').substitute(provider=self.type, reason=reason))
         if error:
             raise error
         else:
             raise Exception(reason)

class Git(Provider):
    def clean(self):
        self.app.source_root.delete()

    def clone(self):
        self.clean()
        if not self.app.source_root.parent.exists:
            self.app.source_root.parent.make()
        self.app.source_root.parent.cd()
        self.execute(self.eval('git') + " clone " + self.eval('repository'))
        self.app.source_root.cd()
        self.execute(self.eval('git') + " submodule init")
        self.execute(self.eval('git') + " submodule update")
        
    def tag(self):
        self.app.source_root.cd()
        tag = self.execute(self.eval('git') + ' tag -l ' +  self.app.build_version)
        if not tag == '':
            self.fail('Did you forget to change the version number?')
        self.execute(self.eval('git') + ' tag -m "' +
                        self.app.marketing_version + '" ' + self.app.build_version)
        self.execute(self.eval('git') + ' push --tags')

class Xcode(Provider):

    @property
    def project(self):
        return self.eval('project')

    def clean(self):
        self.app.source_root.cd()
        cmd = self.eval('xcode')
        cmd = cmd + " -project " + self.project           
        cmd = cmd + " SYMROOT=" + str(self.app.build_root)        
        cmd += " clean"
        self.execute(cmd)
        self.app.path = None

    def build(self, dry=False):
        self.clean()
        cmd = self.eval('xcode')
        cmd = cmd + " -target " + self.eval('target')
        cmd = cmd + " -configuration " + self.eval('configuration')
        cmd = cmd + " -project " + self.project
        cmd = cmd + " SYMROOT=" + str(self.app.build_root)
        self.execute(cmd)
        self.app.path = self.app.build_root.child_folder(
                                self.eval('configuration')).child(self.app.name + ".app")


class InfoPlist(Provider):
    def clean(self):
        self.app.build_version = None
        self.app.marketing_version = None

    def get_version(self, dry=False):
        info = Folder(self.app.path).child('Contents/Info.plist')
        if not File(info).exists:
            self.fail("InfoPlist not found at :" + info)
        from Foundation import NSMutableDictionary
        plist = NSMutableDictionary.dictionaryWithContentsOfFile_(info)
        self.app.build_version = plist['CFBundleVersion']
        self.app.marketing_version = plist.get('CFBundleShortVersionString', self.app.build_version)


class Zip(Provider):
    def clean(self):
        self.app.archive.delete()

    def package(self):
        if not self.app.release_root.exists:
            self.app.release_root.make()
        app = Folder(self.app.path)
        zip_path = app.zzip()
        vzip_name = self.eval('name')
        vzip_path = self.app.release_root.child(vzip_name)
        self.app.archive = File(vzip_path)
        self.app.archive.delete()
        File(zip_path).move_to(vzip_path)

class TemplateReleaseNotesGenerator(Provider):
    def clean(self):
        self.app.release_notes.delete()
        self.app.release_notes = None

    def generate_release_notes(self):
        if not self.app.release_root.exists:
            self.app.release_root.make()
        release_notes_name = self.eval('name')
        self.app.release_notes = File(self.app.release_root.child(release_notes_name))
        notes = File(self.eval('notes_file')).read_all()
        expanded_notes = self.app.substitute(notes)
        self.app.release_notes.write(expanded_notes)


class Sparkle(Provider):
   def clean(self):
       self.app.appcast.delete()
       self.app.appcast = None
       self.app.signature = None

   def sign(self):
       sign_cmd = 'openssl dgst -sha1 -binary < "' + self.app.archive.path + '"'
       sign_cmd = sign_cmd + ' | openssl dgst -dss1 -sign "' + self.eval('private_key') + '"'
       sign_cmd = sign_cmd + ' | openssl enc -base64'
       self.app.signature = self.execute(sign_cmd)

   def verify(self):
       verify_cmd = '"' + self.eval('verifier') + '"'
       verify_cmd = verify_cmd + ' "' + self.app.archive.path + '"'
       verify_cmd = verify_cmd + ' "' + self.app.signature + '"'
       verify_cmd = verify_cmd + ' "' + self.eval('public_key') + '"'
       self.execute(verify_cmd)

   def generate_appcast(self):
       self.app.appcast = File(self.eval('appcast_file'))
       appcast_item = self.eval('appcast_template')
       feed = self.app.appcast.read_all()
       index = feed.find(self.app.substitute('sparkle:version="$build_version"'))
       if not index == -1:
           return
       index = feed.find('</channel>')    
       if index == -1:
           self.fail('Invalid Appcast file')  
       index = feed.rfind('>', 0, index)    
       if index == -1:
           self.fail('Invalid Appcast file')
       feed = feed[:index] + appcast_item + feed[index:]
       self.app.appcast.write(feed)
       self.app.appcast.copy_to(self.app.release_root)   


class S3(Provider):
    def clean(self):pass

    def publish(self):
        try:
            from boto.s3 import Connection, Key, Bucket
        except ImportError, e:
            self.fail("Boto required for S3 publish. Please run `sudo easy_install boto`", e)

        vzip = self.app.archive
        connection = Connection(self.eval('id'), self.eval('key'))
        bucket = connection.get_bucket(self.eval('bucket'))

        def dep_cb(done, rem):
            self.app.logger.info(str(done) + "/" + str(rem) + " bytes transferred")

        # Publish Archive    
        key = bucket.new_key(Folder(self.eval('path')).child(vzip.name))
        key.set_contents_from_filename(str(vzip), cb=dep_cb, num_cb=20)

        # Publish Appcast     
        key = bucket.new_key(Folder(self.eval('path')).child(self.app.appcast.name))
        key.set_contents_from_filename(str(self.app.appcast), cb=dep_cb, num_cb=20)        
        
        # Publish Release Notes                                        
        key = bucket.new_key(Folder(self.eval('path')).child(self.app.release_notes.name))
        key.set_contents_from_filename(str(self.app.release_notes), cb=dep_cb, num_cb=20)