#!/usr/bin/env python
"""List all running VMs."""

from optparse import OptionParser
from ovirt_lib import create_api_connection, lists_vms


def main(opts):
    """Magic main."""
    print opts
    (api, options) = create_api_connection(opts)
    print options
    lists_vms(api, options)
    api.close()


if __name__ == '__main__':
    p = OptionParser()
    p.add_option("-u", "--user", dest="username", help="Username for ovirtmanager")
    p.add_option("-U", "--url", dest="url", help="Url of the ovirt api: https://ovirtmanager.example.com/ovirt-engine/api")
    p.add_option("-p", "--password", dest="password", help="Password for ovirtmanager")
    p.add_option("-z", "--credentials", dest="credentials", help="Credentials location")
    p.add_option("-f", dest="foo")
    (opts, args) = p.parse_args()
    main(opts)
