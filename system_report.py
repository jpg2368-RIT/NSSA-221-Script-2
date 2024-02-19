#!/bin/python3.6

import subprocess as sp
import platform as pf

# runs a command and returns the result
def run(cmd) -> str:
    proc = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
    return str(proc.stdout.read())[2:-3]

def get_device_info() -> tuple:
    hostname = run("hostname | cut -f \".\" -f 1")
    domain = run("hostname | cut -f \".\" -f 2")
    return (hostname, domain)


def cidr_to_netmask(cidr):
    cidr = int(cidr)
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return (str((0xff000000 & mask) >> 24) + "." +
            str((0xff000000 & mask) >> 16) + "." +
            str((0xff000000 & mask) >> 8) + "." +
            str((0xff000000 & mask))
            )

def get_network_info() -> tuple:
    # ip, gateway, netmask, dns1, dns2
    ip = run("ip a | grep ens192 | grep inet | xargs | cut -d \" \" -f 2 | cut -d \"/\" -f 1")
    gateway = run("ip r | grep default | cut -d \" \" -f 3")
    netmask = cidr_to_netmask(run("ip a | grep ens192 | grep inet | xargs | cut -d \" \" -f 2 | cut -d \"/\" -f 2"))
    dns_list = run("cat /etc/resolv.conf | grep nameserver | cut -d \" \" -f 2").split("\\n")
    return (ip, gateway, netmask, dns_list[0], dns_list[1])

def get_os_info() -> tuple:
    # os, version, kernel version
    os = pf.system()
    version = pf.release()
    kernel_version = pf.version()
    return (os, version, kernel_version)


def get_storage_info() -> tuple:
    # drive capacity (gb), available space (gb)
    cap = int(run("df / | grep / | xargs | cut -d ' ' -f 4"))/100000
    avail = int(run("df / | grep / | xargs | cut -d ' ' -f 3"))/1000000
    return (cap, avail)

def get_cpu_info() -> tuple:
    # model, num cpus, num cores
    pass

def get_ram_info() -> tuple:
    # total ram, available ram
    tot = int(run("free | grep Mem | xargs | cut -d ' ' -f 2"))/1000000
    avail = int(run("free | grep Mem | xargs | cut -d ' ' -f 4"))/1000000
    return (tot, avail)

def wp(file, str: str):
    file.write(str)
    print(str)

def info_str(label: str, info: str) -> str:
    return f"\t{label}:\t\t\t{info}" 

def make_log(info: tuple):
    with open(f"{info[0][0]}_system_report.log") as file:
        wp(file, "\t\t\tSystem Report - ")
        wp(file, "")
        wp(file, "Device Information")
        wp(file, info_str("Hostname", info[0][0]))
        wp(file, info_str("Domain", info[0][1]))

        wp(file, "Network Information")
        wp(file, info_str("IP Address", info[1][0]))
        wp(file, info_str("Gateway", info[1][1]))

        
        wp(file, "OS Information")

        wp(file, "Storage Information")

        wp(file, "Processor Information")

        wp(file, "Memory Information")


def main():
    dev_info = get_device_info()
    net_info = get_network_info()
    os_info = get_os_info()
    storage_info = get_storage_info()
    cpu_info = get_cpu_info()
    ram_info = get_ram_info()
    make_log((dev_info, net_info, os_info, storage_info, cpu_info, ram_info))

if __name__ == "__main__":
    run("clear")
    main()