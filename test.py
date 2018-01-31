#!/usr/bin/env python
"""List all running VMs."""

from optparse import OptionParser
from ovirt_lib import create_api_connection, get_vm_id, get_cluster_id, get_dc_id, add_vm, get_random_storagedomain, add_disk_to_instance, get_vnic_id, add_nic_to_instance, start_vm_with_cdrom, get_random_cluster


def main(opts):
    """Magic main."""
    (api, options) = create_api_connection(opts)

    cluster = 'Hypercube1'
    dc = 'Hypercube1'
    cluster_id = get_cluster_id(api, cluster)
    dc_id = get_dc_id(api, dc)
    vlan_name = 'ovirtmngt'

    options['vm_name'] = 'script-test-01'
    options['vmem'] = 2 * 2**30
    options['vcpus'] = 2
    options['os_type'] = 'rhel_7x64'

    get_vnic_id(api, dc_id, 'ovirtdefault')

    # add_vm(api, cluster_id, options)
    # vm_id = get_vm_id(api, cluster_id, options['vm_name'])
    # vnic_id = get_vnic_id(api, dc_id, vlan_name)
    # storage_domain = get_random_storagedomain(api, dc_id)
    # add_disk_to_instance(api, vm_id, storage_domain, 30, 'os_disk', True)
    # add_nic_to_instance(api, vm_id, vnic_id)
    # start_vm_with_cdrom(api, vm_id, 'ks.iso')

    print get_random_cluster(api, dc)


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
