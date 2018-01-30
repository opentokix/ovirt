#!/usr/bin/env python
"""List all running VMs."""

from optparse import OptionParser


from ovirt_lib import create_api_connection, get_vm_id, get_cluster_id, get_dc_id, add_vm


def main(opts):
    """Magic main."""
    (api, options) = create_api_connection(opts)

    print "VM ID: %s" % get_vm_id(api, 0, "ntp1")
    print "Cluster id: %s" % get_cluster_id(api, "")
    print "DC ID: %s" % get_dc_id(api, "")

    options['vm_name'] = 'peter-script-test-01'
    options['vmem'] = 2 * 2**30
    options['vcpus'] = 2
    options['os_type'] = 'rhel_7x64'
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
