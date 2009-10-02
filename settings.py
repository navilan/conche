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
 
                                           
SUVerifier =  os.path.join(XBUILD_PATH, 'SUVerify/build/Release/SUVerify')                                                          
SPARKLE_PUB_KEY = os.path.join(PROJECT_ROOT, 'dsa_pub.pem')
SPARKLE_PRI_KEY = os.path.join(XBUILD_PATH, 'dsa_priv.pem')    

AWS_ACCESS_ID = 'AKIAI7CKLZUTB36XFNCQ'
AWS_ACCESS_KEY = 'ovXRvMMBUMyhuUP3p723zuh2Gs018mqVMyh6/72b'
AWS_BUCKET = 'slammer'
AWS_PATH =  'releases'

APPCAST_TEMPLATE =\
'<item>\
    <title>$app Version $vstring</title>\
    <sparkle:releaseNotesLink>http://mysite.com/rnotes/$app-$vstring.html</sparkle:releaseNotesLink>\
    <pubDate>$pub_date</pubDate>\
    <enclosure\
        url="http://mysite.com/$app/$zip"\
        sparkle:version="$version"\
        sparkle:shortVersionString="$vstring"\
        type="application/octet-stream"\
        length="$bytes"\
        sparkle:dsaSignature="$sign"\
    />\
 </item>\
'