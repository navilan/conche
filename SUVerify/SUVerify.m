#import <Foundation/Foundation.h>
#import "SUDSAVerifier.h"

int main (int argc, const char * argv[]) {
    NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
	NSString * archive_path = [NSString stringWithCString:argv[1] encoding:NSASCIIStringEncoding];
	NSString * signature = [NSString stringWithCString:argv[2] encoding:NSASCIIStringEncoding];
	NSString * keyfile = [NSString stringWithCString:argv[3] encoding:NSASCIIStringEncoding];	
	
	NSString * key = [NSString stringWithContentsOfFile:keyfile  encoding:NSASCIIStringEncoding error:nil];
	
	BOOL result = [SUDSAVerifier validatePath:archive_path withEncodedDSASignature:signature withPublicDSAKey:key];
	if(result){
		printf("Signature Verified\n");
	} else {
		printf("ERROR**************: Singature Verification Failed.\n");
	}
    [pool drain];
    return result ? 0 : -1;
}



