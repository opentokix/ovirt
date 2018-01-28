#!/usr/bin/env python
"""Ovirt modules."""

import ovirtsdk4 as sdk
import ovirtsdk4.types as types
import time
import ConfigParser
from optparse import OptionParser
import os
import sys
import getpass

# def get_vm_id(api, name):

# def add_disk_to_vm(api, id):


def construct_credentials(opts):
    """Construct credentials. First read environment, then command line, lastly ini."""

    try:
        raw_credentials['username'] = os.environ['ovirt_user']
    except KeyError:
        pass
    try:
        raw_credentials['password'] = os.environ['ovirt_password']
    except KeyError:
        pass
    try:
        raw_credentials['url'] = os.environ['ovirt_url']
    except KeyError:
        pass

    if opts.password:
        raw_credentials['password'] = opts.password
    if opts.username:
        raw_credentials['username'] = opts.username
    if opts.url:
        raw_credentials['url'] = opts.url

    if opts.credentials:
        cred_ini = opts.credentials
        config = ConfigParser.ConfigParser()
        config.read(cred_ini)
        try:
            raw_credentials['username'] = config.get('ovirt', 'user')
        except:
            pass
        try:
            raw_credentials['password'] = config.get('ovirt', 'pass')
        except:
            pass
        try:
            raw_credentials['url'] = config.get('ovirt', 'url')
        except:
            pass
    for key in raw_credentials:
        if len(raw_credentials[key]) == 0:
            if key == "username":
                # this will never trigger, here for future use maybe
                raw_credentials['username'] = raw_input("Username: ")
            if key == "password":
                raw_credentials['password'] = getpass.getpass()
            if key == "url":
                hostname = raw_input("Hostname of ovirt manager: ")
                raw_credentials['url'] = "https://%s/ovirt-engine/api" % hostname
    return raw_credentials


def add_disk_to_vm(api, options):
    print "Future"
    return 0


def create_api_connection(opts):
    (options, opts) = construct_credentials(opts)
    url = options['url']
    user = options['username']
    password = options['password']
    try:
        api = sdk.Connection(url, user, password, insecure=True)
    except Exception as e:
        print str(e)
        sys.exit(1)
    except:
        print "Unknown connection error"
        sys.exit(1)
    return api, options


def lists_vms(api, options):
    """List all vms."""
    vms_service = api.system_service().vms_service()
    try:
        vms = vms_service.list()
    except Exception as e:
        print e
        sys.exit(1)
    for vm in vms:
        print("%s: %s, %s, %s" % (vm.name, vm.id, vm.os.type, vm.memory))


def main():
    """Main is not used."""
    print "Modules"


if __name__ == '__main__':
    main()
