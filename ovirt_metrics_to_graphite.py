#!/usr/bin/env python
"""Pump metrics from ovirt to graphite."""

from optparse import OptionParser
from ovirt_lib import create_api_connection
# import sys
import socket
import time
import logging
import logging.handlers


class Graphite(object):
    """Graphite class."""

    def __init__(self, host, port):
        """Create socket."""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.connect((host, port))

    def send(self, prefix, data, point_in_time):
        """Send data."""
        message = "%s %s %s\n" % (prefix, str(data), point_in_time)
        self.s.sendall(message)

    def __del__(self):
        """Close socket."""
        self.s.close()


def get_hypervisor_stats(api, prefix, applogging):
    """List hypervisors with status."""
    start_time = time.time()
    data = []
    hosts_service = api.system_service().hosts_service()
    hosts = hosts_service.list()
    for host in hosts:
        host_name = host.name
        hostname = host_name.replace('.', '_')
        stats = api.follow_link(host.statistics)
        for stat in stats:
            d = "%s.%s.%s %s" % (prefix, hostname, stat.name, stat.values[0].datum)
            data.append(d)
        d = "%s.%s.vms.total %s" % (prefix, hostname, host.summary.total)
        data.append(d)
        d = "%s.%s.vms.active %s" % (prefix, hostname, host.summary.active)
        data.append(d)
        d = "%s.%s.vms.migrating %s" % (prefix, hostname, host.summary.migrating)
        data.append(d)
    end_time = time.time()
    total_time = end_time - start_time
    log_output = "Get stats time: %s" % str(total_time)
    d = "%s.api.scrape.time %s" % (prefix, str(total_time))
    data.append(d)
    applogging.info(log_output)
    return data


def graphite_dump(api, graphite, data, t, applogging):
    """Dump data list to graphite."""
    start_time = time.time()
    for d in data:
        scratch = d.split(' ')
        graphite.send(scratch[0], scratch[1], t)
    end_time = time.time()
    total_time = end_time - start_time
    log_output = "Graphite dump time: %s" % str(total_time)
    applogging.info(log_output)


def main(opts):
    """Magic main."""
    (api, options) = create_api_connection(opts)
    rootlogger = logging.getLogger('')
    rootlogger.setLevel(logging.DEBUG)
    sockethandler = logging.handlers.SysLogHandler(address=('localhost', 514), facility=logging.handlers.SysLogHandler.LOG_LOCAL0, socktype=socket.SOCK_DGRAM)
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
    sockethandler.setFormatter(formatter)
    rootlogger.addHandler(sockethandler)
    applogging = logging.getLogger('ovirt-stats-to-graphite')
    graphite = Graphite(opts.carbon_server, int(opts.carbon_port))
    while True:
        if time.strftime("%S") in ['00', '10', '20', '30', '40', '50']:
            log_output = "Starting data collection at: %s" % time.strftime("%Y-%m-%d %H:%M:%S")
            applogging.info(log_output)
            t = str(time.time())
            data = get_hypervisor_stats(api, opts.carbon_prefix, applogging)
            graphite_dump(api, graphite, data, t, applogging)
        time.sleep(0.3)
    api.close()


if __name__ == '__main__':
    p = OptionParser()
    p.add_option("-u", "--user", dest="username", help="Username for ovirtmanager")
    p.add_option("-U", "--url", dest="url", help="Url of the ovirt api: https://ovirtmanager.example.com/ovirt-engine/api")
    p.add_option("-p", "--password", dest="password", help="Password for ovirtmanager")
    p.add_option("-z", "--credentials", dest="credentials", help="Credentials location")
    p.add_option("-C", "--carbon", dest="carbon_server", default='127.0.0.1', help="Carbon server hostname")
    p.add_option("-P", "--carbon-port", dest="carbon_port", default=2003, help="Carbon server port")
    p.add_option("--prefix", dest="carbon_prefix", default="ovirt.hypervisors", help="Prefix in graphite")
    (opts, args) = p.parse_args()
    main(opts)
