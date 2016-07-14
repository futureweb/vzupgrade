#!/usr/bin/python

import subprocess
import argparse
import sys
import tempfile
import os
import time
import shutil

'''
Check upgrade prerequisites - run preupgrade-assistant
or only its parts if '--blocker' option is specified
'''
def check():
    if cmdline.blocker:
        check_blockers()
    else:
        subprocess.call(['preupg'])

'''
Explicitely launch VZ-specific preupgrade-assistant checkers
that check for upgrade blockers
'''
def check_blockers():
    FNULL = open(os.devnull, 'w')
    ret = subprocess.call(['yum', 'check-update'], stdout=FNULL, stderr=FNULL)# >/dev/null
    if ret > 0:
        print "You have updates available! Please install all updates first"

    ret += subprocess.call(['/usr/share/preupgrade/Virtuozzo6_7/system/vzfs/check.sh'])
    ret += subprocess.call(['/usr/share/preupgrade/Virtuozzo6_7/system/prlctl/check.sh'])

    if ret == 0:
        print "Noupgrade blockers found!"

'''
Actually run upgrade by means of redhat-upgrade-tool
Preliminary launch preupgrade-assistant if it has not been launched yet
'''
def install():
    if not os.path.isdir("/root/preupgrade"):
        print "It looks like preupgrade check was not performed, launching..."
        check()
    subprocess.call(['redhat-upgrade-tool'])

def list_prereq():
    print "=== Virtuozzo-specifi upgrade prerequisites: ==="
    print "* No VMs exist on the host"
    print "* There are no containers that use VZFS"
    print "* All updates are installed"


def parse_command_line():
    global cmdline
    parser = argparse.ArgumentParser(description="Virtuozzo Upgrade Tool")
    subparsers = parser.add_subparsers(title='command')

    sp = subparsers.add_parser('check', help='check upgrade prerequisites and generate upgrade scripts')
    sp.add_argument('--blocker', action='store_true', help='check only upgrade blockers')
    sp.set_defaults(func=check)

    sp = subparsers.add_parser('list', help='list prerequisites for in-place upgrade')
    sp.set_defaults(func=list_prereq)

    sp = subparsers.add_parser('install', help='Perform upgrade')
    sp.add_argument('--source', action='store', nargs='?', help='source to be used')
    sp.set_defaults(func=install)

    cmdline = parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    parse_command_line()
    cmdline.func()
