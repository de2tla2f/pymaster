from time import time
from struct import pack

import ipaddress

class ServerEntry:

  def __init__(self, addr, challenge):

    # Address
    self.addr = addr
    # Shortcuts for generating query
    self.queryAddr = b''

    if ':' in addr[0]:
      self.queryAddr += ipaddress.ip_address(addr[0]).packed
    else:
      for i in addr[0].split('.'):
        self.queryAddr += pack('!B', int(i))

    self.queryAddr += pack('!H', int(addr[1]))

    # Random number that server must return
    self.challenge = challenge
    self.sentChallengeAt = time()

    # Remove server after this time.
    # This maybe not instant
    self.die = self.sentChallengeAt + 600