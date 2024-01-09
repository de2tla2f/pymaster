#!/usr/bin/env python3
import socket
import random
import sys
import traceback
import logging
import os
from optparse import OptionParser
from struct import pack
from time import time

from server_entry import ServerEntry
from protocol import MasterProtocol

LOG_FILENAME = "pymaster.log"
MAX_SERVERS_FOR_IP = 14


class PyMaster:
    def __init__(self, ip, port):
        self.serverList = []
        if ':' in ip:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))

        logging.debug("Welcome to PyMaster!")
        logging.debug("I ask you again, are you my master? @-@")
        logging.debug("Running on %s:%d" % (ip, port))


    def server_loop(self):
        data, addr = self.sock.recvfrom(1024)
        data = data.decode("latin_1")

        match data[0]:
            case MasterProtocol.clientQuery:
                self.client_query(data, addr)
            case MasterProtocol.challengeRequest:
                self.send_challenge_to_server(data, addr)
            case other:
                logging.debug("Unknown message: {0} from {1}:{2}".format(data, addr[0], addr[1]))


    def client_query(self, data, addr):
        region = data[1]  # UNUSED
        data = data.strip("1" + region)
        try:
            query = data.split("\0")
        except ValueError:
            logging.debug(traceback.format_exc())
            return

        queryAddr = query[0]  # UNUSED
        rawFilter = query[1]

        # Remove first \ character
        rawFilter = rawFilter.strip("\\")
        split = rawFilter.split("\\")

        # Use NoneType as undefined
        gamedir = "valve"  # halflife, by default
        clver = None
        nat = 0
        key = None

        for i in range(0, len(split), 2):
            try:
                value = split[i + 1]
                if split[i] == "gamedir":
                    gamedir = value.lower()  # keep gamedir in lowercase
                elif split[i] == "nat":
                    nat = int(value)
                elif split[i] == "clver":
                    clver = value
                elif split[i] == 'key':
                    key = int(value, 16)
                else:
                    logging.debug(
                        "Unhandled info string entry: {0}/{1}. Infostring was: {2}".format(
                            split[i], value, split
                        )
                    )
            except IndexError:
                pass

        packet = MasterProtocol.queryPacketHeader

        if key != None: # Required in latest Xash3D version
            packet += b'\x7F' + pack('<I', key) + b'\x00'

        for i in self.serverList:

            # Use pregenerated address string
            packet += i.queryAddr

        packet += b"\0\0\0\0\0\0"  # Fill last IP:Port with \0

        self.sock.sendto(packet, addr)

    def send_challenge_to_server(self, data, addr):

        logging.debug("Challenge Request: {0}:{1}".format(addr[0], addr[1]))

        # At first, remove old server- data from list
        count = 0
        for i in self.serverList:
            if i.addr[0] == addr[0]:
                if i.addr[1] == addr[1]:
                    self.serverList.remove(i)
                else:
                    count += 1
                if count > MAX_SERVERS_FOR_IP:
                    logging.debug("Reached MAX_SERVERS_FOR_IP: {0}".format(MAX_SERVERS_FOR_IP))
                    return

        # Add server
        logging.debug("Add Server: {0}:{1}".format(addr[0], addr[1]))

        challenge = random.randint(0, 2**32 - 1)

        # Add server to list
        self.serverList.append(ServerEntry(addr, challenge))

        # And send him a challenge
        packet = MasterProtocol.challengePacketHeader
        packet += pack("I", challenge)
        self.sock.sendto(packet, addr)

def spawn_pymaster(verbose, ip, port):
    if verbose:
        logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger().addHandler(logging.FileHandler(LOG_FILENAME))
    logging.getLogger().setLevel(logging.DEBUG)

    masterMain = PyMaster(ip, port)
    while True:
        try:
            masterMain.server_loop()
        except Exception:
            logging.debug(traceback.format_exc())


if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option(
        "-i",
        "--ip",
        action="store",
        dest="ip",
        default="0.0.0.0",
        help="ip to listen [default: %default]",
    )
    parser.add_option(
        "-p",
        "--port",
        action="store",
        dest="port",
        type="int",
        default=27010,
        help="port to listen [default: %default]",
    )
    parser.add_option(
        "-d",
        "--daemonize",
        action="store_true",
        dest="daemonize",
        default=False,
        help="run in background, argument is uid [default: %default]",
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="don't print to stdout [default: %default]",
    )

    (options, args) = parser.parse_args()

    if options.daemonize != 0:
        from daemon import DaemonContext

        with DaemonContext(
            stdout=sys.stdout, stderr=sys.stderr, working_directory=os.getcwd()
        ) as context:
            spawn_pymaster(options.verbose, options.ip, options.port)
    else:
        sys.exit(spawn_pymaster(options.verbose, options.ip, options.port))
