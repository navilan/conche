# Conche                                   

A primitive build system built for cocoa developers that use git, sparkle and S3. Designed but never tested with extensibility in mind.

Version 0.1 Alpha - In other words: Works for me. I have no idea if it would work for you. There is minimal if any, error handling in place. Has not been tested to work for more than one application.


## Features

Conche can perform the following sequence of actions after proper configuration.

1. Clean source directory
2. Git clone from the given repository
3. Build the specified project, target and configuration
4. Get the version number from info plist
5. Zip the resulting app
6. Sign the archive
7. Verify the signature using Sparkle verifier
8. Generate Appcast
9. Generate Release Notes
10. Tag git with the current version 
11. Upload to Amazon S3 
                       
Tasks are configured using YAML.        

1. providers.yaml - List of providers and default settings for them.
2. apps.yaml - List of your applications, settings and overrides for providers.
3. tasklist.yaml - Tasks and sequences

## Caveats                     

Some things that really should've been done already:

1. No declared dependencies between tasks. If you run a task that depends on something else, its behavior is unpredictable.
2. There are some conventions followed, primarily because its now used by one person for one app. I'll try to list some that I know(remember):
    1. The $build_root specified in apps.yaml is used as $SYMROOT for xcodebuild.
    2. The application project file must be in $source_root
3. No support for rolling back.

## Install

    sudo easy_install pyyaml 

If you need Amazon S3 support:

    sudo easy_install boto 


Get the source by cloning this repository.

## Configure                

### 1. Init
    
       cd <Conche Directory> 
       python conche_init.py  -a <Your App> -p <Dir*>
   
   Dir* = A build directory somewhere far far away from your working source directory
   

The above command copies the yaml files in the template directory to the directory you specified. Overwriting only if its new.   

### 2. Configure

#### Providers

    providers.yaml

Stuff to check and change:

1. Name templates
2. Paths for xcode, git, keys etc    
    
#### Apps

    apps.yaml

Stuff to check and change: Pretty much everything.
    
#### Tasks

    tasklist.yaml

Define sequences of tasks here. Please do remember that there are implicit dependencies that have not been taken care of yet. For example, running get_version without running build will fail. 

###. Run

    cd <Conche Directory> 
    python conche.py  -a <Your App> [-p <root>] [-t tasklist]

root = Where you did the init. Default = Current Working Directory.
tasklist = Any of the task lists defined in tasklist.yaml or individual tasks defined by the providers. Can be comma separated to run more than one.

## Contribution

Please do fork. Topic branches will keep me from postponing a merge, put a smile on my face and help the planet be a better place for everyone. 

## License 

MIT License. See `LICENSE`.