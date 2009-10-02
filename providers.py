import sys
from subprocess import Popen, PIPE


class Provider(object):
    
     def __init__(self, ptype, app, settings):
        self.type = ptype
        self.app = app
        self.settings = settings


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

     def fail(self, reason, error=None):
         self.app.logger.error(
             string.Template(
             '$provider failed bacause of this:$reason').substitute(name=self.type, reason=reason))
         if error:
             raise error
         else:         
             raise ProviderException(reason)

class Git(Provider): 
    
   
    def clean(self):
        self.app.source_root.delete()

    def clone(self):
        self.app.root.cd()
        self.execute(self.settings.git + " clone " + self.settings.repository)

    def tag(self):
        self.app.source_root.cd()
        tag = self.execute(self.settings.git + ' tag -l ' +  self.app.version)
        if not tag == '':
            self.fail('Did you forget to change the version number?')
        self.execute(self.settings.git + ' tag -m "' +
                        self.app.short_version_string + '" ' + self.app.version)
        self.execute(self.settings.git + ' push --tags')

class Xcode(Provider):

    @property
    def project(self):
        return self.app.source_root.child(self.settings.project)

    def clean(self):
        cmd = self.settings.xcode
        cmd = cmd + " -project=" + self.project
        cmd += " clean"
        self.execute(cmd)
        self.app.path = None

    def build(self):
        self.clean()
        cmd = settings.xcode
        cmd = cmd + " -target = " + self.settings.target
        cmd = cmd + " -configuration = " + self.settings.configuration
        cmd = cmd + " -project=" + self.project
        cmd = cmd + " SYMROOT=" + self.app.build_root
        self.execute(cmd)   
        self.app.path = self.app.build_root.child_folder(
                                self.settings.configuration).child(self.app.name + ".app")


class InfoPlist(Provider):
    def clean(self):
        self.app.build_version = None
        self.app.marketing_version = None

    def get_version(self):
        info = Folder(self.app.path).child('Contents/Info.plist')
        plist = NSMutableDictionary.dictionaryWithContentsOfFile_(info)
        self.app.build_version = plist['CFBundleVersion']
        self.app.marketing_version = plist.get('CFBundleShortVersionString', self.app.build_version)


class Zip(Provider):
    def clean(self):
        self.app.archive.delete()

    def package(self):
        app = Folder(self.app.path)
        zip_path = app.zzip()
        vzip_name = string.Template(self.settings.name).substitute(
                            build_version=self.app.build_version,
                            marketing_version=self.app.marketing_version,
                            app_name=self.app.name)
        vzip_path = self.app.release_root.child(vzip_name)
        self.app.archive = File(vzip_path)
        self.app.archive.delete()        
        File(zip_path).move_to(vzip_path)

class TemplateReleaseNotesGenerator(Provider):
    def clean(self):
        self.app.release_notes.delete()
        self.app.release_notes = None

    def generate_release_notes(self):
        release_notes_name = string.Template(self.settings.name).substitute(
                                build_version=self.app.build_version,
                                marketing_version=self.app.marketing_version,
                                app_name=self.app.name)
        self.app.release_notes = File(self.app.release_root.child(release_notes_name))
        notes = File(self.settings.notes_file).read_all()
        template = string.Template(notes)
        expanded_notes = template.substitute(
                             build_version=self.app.build_version,
                             marketing_version=self.app.marketing_version,
                             app_name = self.app.name,
                             release_notes_name = self.app.release_notes.name,
                             date = self.app.datestring)
        self.app.release_notes.write(expanded_notes)       


class Sparkle(Provider):
   def clean(self):
       self.app.appcast.delete()
       self.app.appcast = None
       self.app.signature = None

   def sign(self):
       sign_cmd = 'openssl dgst -sha1 -binary < "' + self.app.archive_path + '"'
       sign_cmd = sign_cmd + ' | openssl dgst -dss1 -sign "' + self.settings.private_key + '"'
       sign_cmd = sign_cmd + ' | openssl enc -base64'
       self.app.signature = self.execute(sign_cmd)

   def verify(self):
       verify_cmd = '"' + self.settings.Verifier + '"'
       verify_cmd = verify_cmd + ' "' + self.app.archive.path + '"'
       verify_cmd = verify_cmd + ' "' + self.app.signature + '"'
       verify_cmd = verify_cmd + ' "' + self.settings.public_key + '"'
       self.execute(verify_cmd)

   def generate_app_cast(self):
       appcast_name = string.Template(self.settings.appcast_name).substitute(
                           build_version=self.app.build_version,
                           marketing_version=self.app.marketing_version,
                           app_name=self.app.name)
       self.app.appcast = File(self.app.release_root.child(appcast_name))
       template = string.Template(self.settings.appcast_template)
       appcast_item = template.substitute(
                            build_version=self.app.build_version,
                            marketing_version=self.app.marketing_version,
                            app_name = self.app.name,
                            archive_name = self.app.archive.name,
                            appcast_name = self.app.appcast.name,
                            release_notes_name = self.app.release_notes.name,
                            bytes = self.app.archive.length,
                            signature = self.app.signature,
                            date = self.app.datestring)
       self.app.appcast.write(appcast_item)


class S3(Provider):
    def clean(self):pass

    def publish(self):             
        try:
            from boto.s3 import Connection, Key, Bucket
        except ImportError, e:
            self.fail("Boto required for S3 publish. Please run `sudo easy_install boto`", e)    
                 
        vzip = self.app.archive
        connection = Connection(self.settings.id, self.settings.key)
        bucket = connection.get_bucket(self.settings.bucket)
        key = bucket.new_key(Folder(self.settings.path).child(vzip.name))
        def dep_cb(done, rem):            
            self.app.logger.info(str(done) + "/" + str(rem) + " bytes transferred")
        key.set_contents_from_filename(str(vzip), cb=dep_cb, num_cb=20)