#!/usr/bin/env python
"""Create and start machines from csv."""

from optparse import OptionParser
from ovirt_lib import create_api_connection, get_vm_id, get_cluster_id, get_dc_id, add_vm, get_random_storagedomain, add_disk_to_instance, get_vnic_id, add_nic_to_instance, start_vm_with_cdrom, start_vm_with_pxe
import csv
import sys


def create_from_csv(api, opts):
    """Create instances from csv."""
    source = csv.DictReader(open(opts.csv_file), delimiter=',')
    for s in source:

        options = {'vm_name': None, 'vmem': None, 'vcpus': None, 'os_type': None}
        for k in s:
            if len(s[k]) == 0:
                print "ERROR: %s is required and can not be empty." % k
                sys.exit(1)
        cluster_id = get_cluster_id(api, s.get('cluster'))
        dc_id = get_dc_id(api, s.get('dc'))
        options['vm_name'] = s.get('vm_name')
        options['vcpus'] = s.get('num_cpus')
        options['vmem'] = int(s.get('ram_amount')) * 2 ** 30
        options['os_type'] = s.get('os_type')
        add_vm(api, cluster_id, options)
        vm_id = get_vm_id(api, cluster_id, options['vm_name'])
        vnic_id = get_vnic_id(api, dc_id, s.get('network_name'))
        add_nic_to_instance(api, vm_id, vnic_id)
        add_disk_to_instance(api, vm_id, get_random_storagedomain(api, dc_id), int(s.get('os_disk')), 'os_disk')

        for d in ['Disk1', 'Disk2', 'Disk3', 'Disk4']:
            if s[d] != 'None':
                if ':' not in s[d]:
                    print "Error: extra disks is on the form size:name, 10:app for a 10G app disk"
                disk = s[d].split(':')
                add_disk_to_instance(api, vm_id, get_random_storagedomain(api, dc_id), int(disk[0]), disk[1], boot=False)
        if s.get('BootDevice') == 'pxe':
            start_vm_with_pxe(api, vm_id)
        else:
            start_vm_with_cdrom(api, vm_id, s.get('BootDevice'))
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
