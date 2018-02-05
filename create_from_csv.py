#!/usr/bin/env python
"""Create and start machines from csv."""

from optparse import OptionParser
from ovirt_lib import create_api_connection, get_vm_id, get_cluster_id, get_dc_id, add_vm, get_random_storagedomain, add_disk_to_instance, get_vnic_id, add_nic_to_instance, start_vm_with_cdrom
import csv
import sys


def create_from_csv(api, opts):
    """Create instances from csv."""
    source = csv.DictReader(open(opts.csv_file), delimiter=',')
    for s in source:
        options = {}
        print dir(options)
        for k in s:
            if len(s[k]) == 0:
                print "ERROR: %s is required and can not be empty." % k
                sys.exit(1)
        options['vm_name'] = s.vm_name
        options['vcpus'] = s.num_cpus
        options['vmem'] = int(s['ram_amount']) * 2 ** 30
        cluster_id = get_cluster_id(api, s.vm_dc)
        print get_dc_id(api, s.vm_dc)

        for d in ['Disk1', 'Disk2', 'Disk3', 'Disk4']:
            if s[d] != 'None':
                print s[d].split(':')
    return 0


def main():
    """Incredible main."""
    (api, options) = create_api_connection(opts)
    create_from_csv(api, opts)
    api.close()


if __name__ == '__main__':
    p = OptionParser()
    p.add_option("-u", "--user", dest="username", help="Username for ovirtmanager")
    p.add_option("-U", "--url", dest="url", help="Url of the ovirt api: https://ovirtmanager.example.com/ovirt-engine/api")
    p.add_option("-p", "--password", dest="password", help="Password for ovirtmanager")
    p.add_option("-z", "--credentials", dest="credentials", help="Credentials location")
    p.add_option("--csv", dest="csv_file")
    (opts, args) = p.parse_args()
    main()


vm_name,num_cpus,ram_amount,vm_dc,storagedomain,os_disk,os_type,BootDevice,network_name,Disk1,Disk2,Disk3,Disk4