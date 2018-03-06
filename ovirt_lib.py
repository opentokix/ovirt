#!/usr/bin/env python
"""Ovirt modules."""

import ovirtsdk4 as sdk
import ovirtsdk4.types as types
import time
import ConfigParser
import os
import sys
import getpass
import random


def get_vm_id(api, cluster_id, name):
    """Get id of vm in specific cluster."""
    search_name = "name=%s" % name
    vms_service = api.system_service().vms_service()
    try:
        vm = vms_service.list(search=search_name)[0]
    except:
        return None
    return vm.id


def get_dc_id(api, name):
    """Get id of dc from name."""
    search_name = "name=%s" % name
    dcs_service = api.system_service().data_centers_service()
    try:
        dc = dcs_service.list(search=search_name)[0]
    except:
        return None
    return dc.id


def get_cluster_id(api, name):
    """Get id of cluster from name."""
    search_name = "name=%s" % name
    clusters_service = api.system_service().clusters_service()
    try:
        cluster = clusters_service.list(search=search_name)[0]
    except:
        return None
    return cluster.id


def get_vnic_id(api, dc_id, name):
    """Get vNic id for network name in a DC."""
    dcs_service = api.system_service().data_centers_service()
    dc_service = dcs_service.data_center_service(dc_id)
    attached_vnic_service = dc_service.networks_service()
    for service in attached_vnic_service.list():
        if service.name == name:
            network_id = service.id
    profiles_service = api.system_service().vnic_profiles_service()
    for profile in profiles_service.list():
        if profile.name == name and profile.network.id == network_id:
            return profile.id


def add_vm(api, cluster_id, options):
    """Adding a VM."""
    vms_service = api.system_service().vms_service()
    try:
        vms_service.add(
            types.Vm(
                name=options['vm_name'],
                memory=options['vmem'],
                cpu=types.Cpu(topology=types.CpuTopology(cores=int(options['vcpus']), sockets=1)),
                type=types.VmType('server'),
                os=types.OperatingSystem(type=options['os_type']),
                cluster=types.Cluster(
                    id=cluster_id,
                ),
                template=types.Template(name='Blank',),
            ),
        )
    except Exception as e:
        print "Can't add VM: %s" % str(e)
        api.close()
        sys.exit(1)


def get_random_storagedomain(api, dc_id):
    """Return a random storage domain above 1TB free space."""
    sd_list = []
    dcs_service = api.system_service().data_centers_service()
    dc_service = dcs_service.data_center_service(dc_id)
    attached_sds_service = dc_service.storage_domains_service()
    sds = attached_sds_service.list()
    for s in range(len(sds)):
        if sds[s].name.find('ssd') != -1:
            avail = int(sds[s].available / 1073741824)
            if avail > 999:
                sd_list.append(sds[s].id)
            else:
                print "WARNING: %s is under 1TB free space" % (sds[s].name)
    if len(sd_list) == 0:
        print "ERROR: No storage domain available"
        sys.exit(1)
    return random.choice(sd_list)


def add_disk_to_instance(api, vm_id, storage_domain, size, name, boot=True):
    """Add disk to VM by id."""
    vms_service = api.system_service().vms_service()
    disk_attachments_service = vms_service.vm_service(vm_id).disk_attachments_service()
    try:
        disk_attachment = disk_attachments_service.add(
            types.DiskAttachment(
                disk=types.Disk(
                    name=name,
                    description=name,
                    format=types.DiskFormat.COW,
                    provisioned_size=size * 2**30,
                    sparse=True,
                    storage_domains=[
                        types.StorageDomain(
                            id=storage_domain,
                        ),
                    ],
                ),
                interface=types.DiskInterface.VIRTIO,
                bootable=boot,
                active=True,
            ),
        )
    except Exception as e:
        print "Can't add Disk: %s" % str(e)
        api.close()
        sys.exit(1)
    disks_service = api.system_service().disks_service()
    disk_service = disks_service.disk_service(disk_attachment.disk.id)
    while True:
        time.sleep(5)
        disk = disk_service.get()
        if disk.status == types.DiskStatus.OK:
            break


def add_nic_to_instance(api, vm_id, vnic_id, nic_name='nic1'):
    """Add nic to vm."""
    vms_service = api.system_service().vms_service()
    """Get id of network."""
    nics_service = vms_service.vm_service(vm_id).nics_service()
    try:
        nics_service.add(
            types.Nic(
                name=nic_name,
                description='My network interface card',
                vnic_profile=types.VnicProfile(
                    id=vnic_id,
                ),
            ),
        )
    except Exception as e:
        print "Can't add NIC: %s" % str(e)
        api.close()
        sys.exit(1)


def start_vm_with_pxe(api, vm_id):
    """Add PXE Boot option to vm."""
    vms_service = api.system_service().vms_service()
    vm_service = vms_service.vm_service(vm_id)
    vm_service.start(
        vm=types.Vm(
            os=types.OperatingSystem(
                boot=types.Boot(
                    devices=[
                        types.BootDevice.HD,
                        types.BootDevice.NETWORK]
                )
            )
        )
    )


def start_vm_with_cdrom(api, vm_id, isoname='ks.iso'):
    """Add CDROM and boot vm."""
    vms_service = api.system_service().vms_service()
    vm_service = vms_service.vm_service(vm_id)
    cdroms_service = vm_service.cdroms_service()
    cdrom = cdroms_service.list()[0]
    cdrom_service = cdroms_service.cdrom_service(cdrom.id)
    cdrom_service.update(
        cdrom=types.Cdrom(
            file=types.File(
                id=isoname
            ),
        ),
        current=False,
    )
    vm_service.start(
        vm=types.Vm(
            os=types.OperatingSystem(
                boot=types.Boot(
                    devices=[
                        types.BootDevice.HD,
                        types.BootDevice.CDROM]
                )
            )
        )
    )


def construct_credentials(opts):
    """Construct credentials. First read environment, then command line, lastly ini."""
    raw_credentials = {'username': None, 'password': None, 'url': None}
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
        if raw_credentials[key] is None:
            if key == "username":
                # this will never trigger, here for future use maybe
                raw_credentials['username'] = raw_input("Username: ")
            if key == "password":
                raw_credentials['password'] = getpass.getpass()
            if key == "url":
                hostname = raw_input("Hostname of ovirt manager: ")
                raw_credentials['url'] = "https://%s/ovirt-engine/api" % hostname
    return raw_credentials, opts


def create_api_connection(opts):
    """Create API Connection."""
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
