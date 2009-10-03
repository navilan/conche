import sys
from file_system import File, Folder
import logging                      
from logging import handlers
import string         
from datetime import datetime        

logger = logging.getLogger('default')      
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

try:
    import yaml
except ImportError:
    logger.error('PyYaml is required for conche. Please run `sudo easy_install pyyaml`')                                                                                            
    raise

class App(object): 
    def __init__(self, name, settings, root):
        self.name = name       
        self.settings = settings
        root = root.rstrip('/')
        self.root = Folder(root)
        self.build_root = Folder(string.Template(settings['build_root']).substitute(root=root, app_name=self.name))
        self.source_root = Folder(string.Template(settings['source_root']).substitute(root=root, app_name=self.name))
        self.release_root = Folder(string.Template(settings['release_root']).substitute(root=root, app_name=self.name))                
        self.path = None          
        self.build_version = None
        self.marketing_version = None 
        self.signature = None
        self.datestring = datetime.today().strftime("%A, %d. %B %Y %I:%M:%S")       
        self.archive = None
        self.appcast = None        
        self.release_notes = None        
                    
    @property     
    def logger(self):
        return logger         
        
    def substitute(self, value):   
        template = string.Template(value)
        d = dict(  
                root = self.root.path,
                build_root = self.build_root.path,
                source_root = self.source_root.path,                
                release_root = self.release_root.path, 
                build_version=self.build_version,
                marketing_version=self.marketing_version,
                app_name = self.name,
                signature = self.signature,
                date = self.datestring)

        if self.archive:       
            d['archive_name'] = self.archive.name                         
            d['bytes'] = self.archive.size
        
        if self.appcast:
            d['appcast_name'] = self.appcast.name    
            
        if self.release_notes:
            d['release_notes_name'] = self.release_notes.name 
                      
        return template.substitute(d)    
        
class Conf(object):
    
    def __init__(self, path):
        self.path = Folder(path).humblepath
        if not Folder(path).exists:
            raise ConfException(self)     
        self.app = None    

    def dump(self):   
        import pickle
        print pickle.dumps(self.apps)    
        print pickle.dumps(self.providers)        
        print pickle.dumps(self.tasklist)        
        
    def __parse__(self): 
        app_settings = self.__load_settings__(self.path, 'apps.yaml')
        self.apps = {}
        for app_name, app_conf in app_settings.iteritems():
            self.apps[app_name] = App(app_name, app_conf, self.path)
            
        self.app = self.apps[self.app_name]
        provider_settings = self.__load_settings__(self.path, 'providers.yaml')
        self.providers = {}
        self.task_providers = {}
        for provider_type, provider_config in provider_settings.iteritems():            
            app_config = self.app.settings.get(provider_type, {})
            settings = provider_config.get('settings', {})
            settings.update(app_config)
            provider_config['settings'] = settings
            provider = self.make(provider_type, provider_config)
            self.providers[provider_type] = provider
            for task in provider_config['tasks']:
                self.task_providers[task] = provider
                
        task_lists = self.__load_settings__(self.path, 'tasklist.yaml')
        self.tasks = {}         
        for task_list_name, task_list in task_lists.iteritems():
            self.tasks[task_list_name] = task_list


    def run_task(self, app, task_name):
        if not self.app:                
            self.app_name = app
            self.__parse__()  
        split_tasks = task_name.split(',')  
        for t in split_tasks:       
            task_list = self.tasks.get(t, None)
            if task_list:
                for subtask in task_list:
                    self.run_task(app, subtask)
            else:        
                provider = self.task_providers.get(t, None)
                if not provider:
                    raise Exception('No Task Found for:' + t)
                provider.perform_task(t)     
                        
            
    def __load_settings__(self, path, file_name):
        f = open(Folder(path).child(file_name), 'r')    
        settings = yaml.load(f)
        f.close()                  
        return settings
        

    def make(self, ptype, provider_config):
       class_string = provider_config['provider']
       (module_name, _ , provider_name) = class_string.rpartition(".")
       __import__(module_name)
       module = sys.modules[module_name]
       classobj = getattr(module, provider_name)
       return classobj(ptype, self.app, provider_config)            
        
         
class ConfException(Exception):
    
    def __str__(self, conf):
        return string.Template("A configuration error occured. Check the configuration file[$path] for errors.").substitute(path=conf.path)