class MasterProtocol:

	# Client To Master
	clientQuery = '1'

	# Server To Master
	challengeRequest = 'q'

	# Master To Client
	queryPacketHeader = b'\xff\xff\xff\xff\x66\x0a'

	# Master To Server
	challengePacketHeader = b'\xff\xff\xff\xff\x73\x0a'
