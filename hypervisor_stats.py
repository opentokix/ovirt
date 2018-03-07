#!/usr/bin/env python
"""List hosts stats."""

from optparse import OptionParser
from ovirt_lib import create_api_connection
import sys


def list_hosts_with_status(api, cluster):
    """List hypervisors with status."""
    hosts_service = api.system_service().hosts_service()
    search_cluster = "Cluster=%s" % cluster
    hosts = hosts_service.list(search=search_cluster)
    for host in hosts:
        print "%s: %s" % (host.name, host.status)
        # stats = api.follow_link(host.statistics)


def hosts_status_percent(api, cluster):
    """Print percent non up."""
    status_flags = {'up': 0,
                    'down': 0,
                    'maintenance': 0,
                    'non_operational': 0,
                    'other': 0}
    hosts_service = api.system_service().hosts_service()
    search_cluster = "Cluster=%s" % cluster
    hosts = hosts_service.list(search=search_cluster)
    total = 0
    for host in hosts:
        if str(host.status) == 'up':
            status_flags['up'] += 1
        elif str(host.status) == 'down':
            status_flags['down'] += 1
        elif str(host.status) == 'maintenance':
            status_flags['maintenance'] += 1
        elif str(host.status) == 'non_operational':
            status_flags['non_operational'] += 1
        else:
            status_flags['other'] += 1
        total += 1
    non_up = total - status_flags['down'] - status_flags['maintenance'] - status_flags['non_operational'] - status_flags['other']
    percent = float(non_up) / float(total) * 100
    return percent


def nagios_output(api, cluster, warning, critical):
    """Compatible ouput and exit code with nagios."""
    percent = hosts_status_percent(api, opts.cluster_name)
    if percent < float(critical):
        print "CRITICAL: Less then %f.1%% hypervisors is in state up in %s" % (float(critical), cluster)
        sys.exit(2)
    elif percent < float(warning):
        print "WARNING: Less then %f.1%% hypervisors is in state up in %s" % (float(warning), cluster)
        sys.exit(0)
    else:
        print "OK: %.1f%% Hypervisors is in state up in %s" % (float(percent), cluster)
        sys.exit(0)


def main(opts):
    """Magic main."""
    (api, options) = create_api_connection(opts)
    if opts.status:
        list_hosts_with_status(api, opts.cluster_name)
    elif opts.glance:
        percent = hosts_status_percent(api, opts.cluster_name)
        print "%.1f%% of hypervisors in %s is in state up" % (percent, opts.cluster_name)
    elif opts.nagios:
        nagios_output(api, opts.cluster_name, opts.warning, opts.critical)
    api.close()


if __name__ == '__main__':
    p = OptionParser()
    p.add_option("-u", "--user", dest="username", help="Username for ovirtmanager")
    p.add_option("-U", "--url", dest="url", help="Url of the ovirt api: https://ovirtmanager.example.com/ovirt-engine/api")
    p.add_option("-p", "--password", dest="password", help="Password for ovirtmanager")
    p.add_option("-z", "--credentials", dest="credentials", help="Credentials location")
    p.add_option("--status", dest="status", action="store_true", default=False, help="Get a list of all the hosts with status and name")
    p.add_option("--glance", dest="glance", action="store_true", default=False, help="Get a percent of hypervisors up")
    p.add_option("-C", "--cluster", dest="cluster_name", default="ovirt1", help="Name of cluster to check")
    p.add_option("--nagios", dest="nagios", action="store_true", default=False, help="Nagios compatible check")
    p.add_option("-w", "--warning", dest="warning", default=90, help="Nagios warning treshold in percent")
    p.add_option("-c", "--critical", dest="critical", default=70, help="Nagios critical level in percent")
    (opts, args) = p.parse_args()
    main(opts)
