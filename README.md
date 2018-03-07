# Simple ovirtsdk4 utils

## Add  vm


Tool will add a VM to ovirt or rhev 4.x using the API.

    Options:
        -u, --user: ovirt username
        -U, --url: url of the ovirt manager (https://hostname.domain.tld/ovirt-engine/api)
        -p, --password: your password
        -n, --name: name of the vm you want to create (defaults to uuid)
        -c, --cpus: Number of cpu cores (default: 1)
        -r, --ram: Amount of ram in GB (default: 2 GB)
        -o, --osdisk: Size of OS disk in GB (default: 30 GB)
        -d, --datacenter: Name of datacenter (default: Hypercube1)
        -z, --credentials: Location and name of credentials ini-file.
        -s, --system: Operating system (default: rhel_7x64)
        -N, --network Name of the network to use
        -S, --storagedomain Name of the storage domain
        --pxe: Boot the system with pxe
        --cdrom: Boot the system from cdrom with name.iso
        --csv: Create and start VM's from a CSV File.
        -h, --help: This help text

Credentials can be provided in various ways:
    * Command line with -u, -p
    * Environment variables: ovirt_user, ovirt_password, ovirt_url
    * INI file as described below
    * And if none of the above, interactive prompt for hostname + password.

Example credentials ini:

    [ovirt]
    url=https://hostname.domain.tld/ovirt-engine/api
    user=admin@internal
    pass=abc123

Tested on ovirt 4.2.0.2-1.el7.centos

### Example usage

**Add a vm named myvm2 with 3 cpus and 3 GB or ram and 10 GB OS disk with rhel 6 x64 in DC Hypercube1**

    ./add_vm.py --name myvm2 --cpus 3 --ram 3 --osdisk 10 -z /home/peter/credentials/ovirt_api.conf -d Hypercube1 -l rhel_6x64

**Add a vm named bamboozle with 4 cpus and 32 GB or ram and 30 GB OS disk with rhel 7 x64 in DC Hypercube1**

    ./add_vm.py --name bamboozle --cpus 3 --ram 32 --osdisk 30 -z /home/peter/credentials/ovirt_api.conf -d Hypercube1 -l rhel_7x64


### Add host with a CSV File (create_from_csv.py) --csv ins add_vm.py id Deprecated

If you are going to add a large number of hosts in many datacenters. You can add them with a csv file.
This functionality is not heavily tested and might break.

This is the format of the csv-file:

    vm_name,num_cpus,ram_amount,dc,cluster,storagedomain,os_disk,os_type,BootDevice,network_name,Disk1,Disk2,Disk3,Disk4
    name01,1,2,DATACENTER,CLUSTERNAMEINDC,random,30,rhel_7x64,ks.iso,VLAN10,10:app,None,None,None
    name02,1,2,DATACENTER,CLUSTERNAMEINDC,random,30,rhel_7x64,ks.iso,VLAN10,10:app,10:misc,10:app2,10:misc2
    name03,1,2,DATACENTER,CLUSTERNAMEINDC,random,30,rhel_6x64,pxe,VLAN200,None,None,20:misc2,None


### Remove VM

    Turn off and remove VM.

    ./remove_vm.py -z /home/peter/credentials/ovirt_api.conf -n foo3


### Requirements

The ovirtsk4 has quite a few dependencies, YMMV with these instructions. Tested on Ubuntu.

    Debian/Ubuntu: sudo apt-get -y install python-pycurl python-libxml2 libxml2-dev


    Rhel/CentOS: sudo yum install -y libxml2-python.x86_64 libxml2-devel python-pycurl python python-pip

    pip install -r requirements.txt

### Hypervisor stats 

Nagios compatible simple check script for hypervisors in a cluster, alerting on % of hypervisors in non-up state 

    hypervisor_stats.py -z credentials.conf --nagios --warning 80 --critical 50 --cluster ovirt1 

Will trigger a warning if 20% of the hypervisors are in non-up state (non_operations, maintenance or other) and critical if 50%. 

### Ovirt metrics to graphite 

This will scrape the API of ovirt for all the hypervisors regardless of cluster and push stats to graphite, it will also scrape stats on migrating vms, number of vms total and active vms. Active VM that is moving, will end up in migrating state.

There is also a systemd service file to run the script as a service with automatic restarts. 

For the service file to work the ovirt_lib.py has to be in /usr/local/share/ovirt 


#### License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
