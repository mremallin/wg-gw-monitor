#!/bin/env python3

import sys
import platform
import subprocess
import logging
import time

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

def check_reachability(gateway):
    # from https://stackoverflow.com/questions/2953462/pinging-servers-in-python
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    time.sleep(1)
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', '-w', '1', gateway]

    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def bounce_interface(interface):
    logging.info("Bouncing interface {}".format(interface))
    command = ['wg-quick', 'down', interface]
    logging.debug("Command: {}".format(command))
    subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    command[1] = 'up'
    subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
def main():
    if len(sys.argv) < 3:
        print("Not enough arguments")
        help()
        sys.exit(1)

    # After this number of missed pings, bounce the wg interface
    # As written, each unreachable ping takes about 2s to be noticed
    # This means 30 missed pings will take about 60s to detect
    MISSED_PINGS = 30

    # Number of consecutive pings that have failed
    missed_ping_count = 0

    wg_gateway = sys.argv[1]
    wg_interface = sys.argv[2]

    logging.info("Watching reachability to {} for interface {}".format(wg_gateway, wg_interface))

    try:
        while(True):
            is_reachable = check_reachability(wg_gateway)
            if not is_reachable:
                logging.debug("{} not reachable".format(wg_gateway))
                missed_ping_count += 1
            else:
                logging.debug("{} reachable".format(wg_gateway))
                missed_ping_count = 0

            if (missed_ping_count >= MISSED_PINGS):
                bounce_interface(wg_interface)
                missed_ping_count = 0
    except KeyboardInterrupt:
        print("Exiting...")

def help():
    print("{} [gw address] [wg interface]".format(sys.argv[0]))

if __name__ == "__main__":
    main()

