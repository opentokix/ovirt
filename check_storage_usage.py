#!/usr/bin/env python2 

from __future__ import print_function
from optparse import OptionParser
from ovirt_lib import create_api_connection, get_dc_id
import csv
import sys


def get_sds(api, dc_id):
  sd_list = []
  dcs_service = api.system_service().data_centers_service()
  dc_service = dcs_service.data_center_service(dc_id)
  attached_sds_service = dc_service.storage_domains_service()
  return attached_sds_service.list()


def check_committed(api, sds, info, flags):
  for s in range(len(sds)):
    total = sds[s].available + sds[s].used
    committed_percent = float(float(sds[s].committed) / float(total) * 100.0)
    if committed_percent > float(opts.crit):
      flags['CRITICAL'] = True
      info.append("C:" + sds[s].name)
    elif committed_percent > float(opts.warn):
      flags['WARNING'] = True
      info.append("W:" + sds[s].name)
    else: 
      continue
  exit_logic(api, info, flags)


def check_used(api, sds, info, flags):
  for s in range(len(sds)):
    total = sds[s].available + sds[s].used
    used_percent = float(float(sds[s].used) / float(total) * 100.0)
    if used_percent > float(opts.crit):
      flags['CRITICAL'] = True
      info.append("C:" + sds[s].name)
    elif used_percent > float(opts.warn):
      flags['WARNING'] = True
      info.append("W:" + sds[s].name)
    else: 
      continue
  exit_logic(api, info, flags)


def exit_logic(api, info, flags):
  if flags['CRITICAL'] is True:
    print("CRITICAL: ", ' '.join(info))
    sys.exit(2)
  elif flags['WARNING'] is True:
    print("WARNING: ", ' '.join(info))
    sys.exit(1)
  else:
    print("OK: All storage domains are within defined usage patterns")
  api.close()


def main():
  flags = {'WARNING': False, 'CRITICAL': False}
  info = []
  if (opts.committed and opts.usage):
    print("Please select one check options, used or committed.")
    sys.exit(1)
  if opts.warn > opts.crit:
    print("Warning need to be less than critical")
    sys.exit(1)
  (api, options) = create_api_connection(opts)
  dc_id = get_dc_id(api, opts.dc)
  sds = get_sds(api, dc_id)
  if opts.committed:
    check_committed(api, sds, info, flags)
  elif opts.usage:
    check_used(api, sds, info, flags)
  else: 
    print("Please select usage or committed")
    sys.exit(1)


if __name__ == '__main__':
  p = OptionParser()
  p.add_option("-u", "--user", dest="username", help="Username for ovirtmanager")
  p.add_option("-U", "--url", dest="url", help="Url of the ovirt api: https://ovirtmanager.example.com/ovirt-engine/api")
  p.add_option("-p", "--password", dest="password", help="Password for ovirtmanager")
  p.add_option("-z", "--credentials", dest="credentials", help="Credentials location")
  p.add_option("-w", "--warning", dest="warn", help="Warning treshold")
  p.add_option("-c", "--critical", dest="crit", help="Critical treshold")
  p.add_option("-D", "--datacenter", dest="dc", help="Datacenter to check")
  p.add_option("--committed", dest="committed", action="store_true", help="Check the committed percentage")
  p.add_option("--used", dest="usage", action="store_true", help="Check usage percentage")
  (opts, args) = p.parse_args()
  main() 