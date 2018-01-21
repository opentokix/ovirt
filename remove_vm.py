#!/usr/bin/env python
"""List all running VMs."""


import ovirtsdk4 as sdk
import ovirtsdk4.types as types
import ConfigParser
from optparse import OptionParser
import os
import sys
import getpass
import time


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


def remove_vm(api, options):
    """Remove a single VM."""
    vms_service = api.system_service().vms_service()
    search_name = "name=" + options['vm_name']
    vm = vms_service.list(search=search_name)[0]
    vm_service = vms_service.vm_service(vm.id)
    vm_service.stop()
    while True:
        time.sleep(5)
        vm = vm_service.get()
        if vm.status == types.VmStatus.DOWN:
            break
    vm_service.remove()


def construct_credentials(opts):
    """Construct credentials. First read environment, then command line, lastly ini."""
    raw_credentials = {'username': '',
                       'password': '',
                       'url': ''}
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
                raw_credentials['username'] = raw_input("Username: ")
            if key == "password":
                raw_credentials['password'] = getpass.getpass()
            if key == "url":
                hostname = raw_input("Hostname of ovirt manager: ")
                raw_credentials['url'] = "https://%s/ovirt-engine/api" % hostname
    return raw_credentials


def main(opts):
    """Magic main."""
    options = construct_credentials(opts)
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

    options['vm_name'] = opts.vm_name

    remove_vm(api, options)
    api.close()


if __name__ == '__main__':
    p = OptionParser()
    p.add_option("-u", "--user", dest="username", help="Username for ovirtmanager")
    p.add_option("-U", "--url", dest="url", help="Url of the ovirt api: https://ovirtmanager.example.com/ovirt-engine/api")
    p.add_option("-p", "--password", dest="password", help="Password for ovirtmanager")
    p.add_option("-z", "--credentials", dest="credentials", help="Credentials location")
    p.add_option("-n", "--name", dest="vm_name", help="Name of vm to be removed")
    (opts, args) = p.parse_args()
    main(opts)
