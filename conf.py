import sys
from file_system import File, Folder
import logging                      
from logging import handlers
import string         
from datetime import datetime        
import providers

logger = logging.getLogger('default')      
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class App(object): 
    def __init__(self, settings, root):
        self.name = settings['name']    
        self.root = Folder(root)
        self.build_root = Folder(string.Template(settings['build_root']).substitute(root=root))
        self.source_root = Folder(string.Template(settings['source_root']).substitute(root=root))
        self.release_root = Folder(string.Template(settings['release_root']).substitute(root=root))                
        self.path = None          
        self.build_version = None
        self.marketing_version = None 
        self.signature = None
        self.datestring = datetime.today().strftime("%A, %d. %B %Y %I:%M:%S")       
                    
    @property     
    def logger(self):
        return logger     

class Conf(object):
    
    def __init__(self, path):
        self.path = path
        if not File(path).exists:
            raise ConfException(self)
        try:
            import yaml
        except ImportError:
            logger.error('PyYaml is required for conche. Please run `sudo easy_install yaml`')                                                                                            
            raise
        
        f = open(self.path, 'r')    
        self.settings = yaml.load(f)
        f.close()                   
        self.__parse__()
    
    def dump(self):   
        import pickle
        print pickle.dumps(self.app)    
        print pickle.dumps(self.providers)        
        
    def __parse__(self):
        app_settings = self.settings['App']
        self.app = App(app_settings, self.path)        
        provider_dict = self.settings['Providers']        
        self.providers = {}
        for provider_type, provider_config in provider_dict.iteritems():
            self.providers[provider_type] = self.make(provider_type, provider_config)

    def make(self, ptype, provider_config):
       class_string = provider_config['provider']
       (module_name, _ , provider_name) = class_string.rpartition(".")
       module = sys.modules[module_name]
       classobj = getattr(module, provider_name)
       print provider_name
       return classobj(ptype, self.app, provider_config)            
        
         
class ConfException(Exception):
    
    def __str__(self, conf):
        return string.Template("A configuration error occured. Check the configuration file[$path] for errors.").substitute(path=conf.path)
        
    
    