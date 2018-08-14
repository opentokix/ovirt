#!/usr/bin/env python2 

from __future__ import print_function
from optparse import OptionParser
from ovirt_lib import create_api_connection, get_vm_id, get_cluster_id, get_dc_id, add_vm, get_random_storagedomain, add_disk_to_instance, get_vnic_id, add_nic_to_instance, start_vm_with_cdrom, start_vm_with_pxe
import csv
import sys

def get_sds(api, dc_id):
  sd_list = []
  dcs_service = api.system_service().data_centers_service()
  dc_service = dcs_service.data_center_service(dc_id)
  attached_sds_service = dc_service.storage_domains_service()
  return attached_sds_service.list()




def main():
  (api, options) = create_api_connection(opts)
  dc_id = get_dc_id(api, opts.dc)
  sds = get_sds(api, dc_id)
  for s in range(len(sds)):
    total = sds[s].available + sds[s].used
    percent = float(float(sds[s].used) / float(total) * 100.0)
    print(int(percent))
    print(sds[s].committed)
    t_gb = total / 1024 / 1024 / 1024 


if __name__ == '__main__':
  p = OptionParser()
  p.add_option("-u", "--user", dest="username", help="Username for ovirtmanager")
  p.add_option("-U", "--url", dest="url", help="Url of the ovirt api: https://ovirtmanager.example.com/ovirt-engine/api")
  p.add_option("-p", "--password", dest="password", help="Password for ovirtmanager")
  p.add_option("-z", "--credentials", dest="credentials", help="Credentials location")
  p.add_option("-w", "--warning", dest="warn", help="Warning treshold")
  p.add_option("-c", "--critical", dest="crit", help="Critical treshold")
  p.add_option("-D", "--datacenter", dest="dc", help="Datacenter to check")
  (opts, args) = p.parse_args()
  main() 