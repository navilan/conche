import os

XBUILD_PATH = os.path.abspath(os.path.dirname(__file__))

GIT_PATH = '/usr/local/git/bin/git'
XCODE_PATH = '/usr/bin/xcodebuild'

GIT_REPOSITORY = 'git@github.com:lakshmivyas/Fount.git'

XCODE_TARGET = 'Fount'
XCODE_CONFIGURATION = 'Release'

XBUILD_TARGET_PATH = '/Users/lakshmivyas/xbuild'
PROJECT_ROOT =  '/Users/lakshmivyas/xbuild/Fount'
BUILD_ROOT =  os.path.join(XBUILD_TARGET_PATH, 'build')
RELEASE_ROOT = os.path.join(XBUILD_TARGET_PATH, 'out')
APP_NAME = 'Fount'


 
# SPARKLE_PUB_KEY =
# SPARKLE_PRI_KEY =
# 
#               