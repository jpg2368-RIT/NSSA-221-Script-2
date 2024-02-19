#!/bin/python3.6

import subprocess as sp
import platform as pf

# runs a command and returns the result
def run(cmd) -> str:
    proc = sp.Popen(cmd, shell=True, stdout=sp.PIPE, )
    return str(proc.stdout.read())[2:-3]

def get_device_info() -> tuple:
    hostname = run("hostname | cut -d '.' -f 1")
    domain = run("hostname | cut -d '.' -f 2")
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
    ip = run("ip a | grep ens192 | grep inet | xargs | cut -d ' ' -f 2 | cut -d '/' -f 1")
    gateway = run("ip r | grep default | cut -d ' ' -f 3")
    netmask = cidr_to_netmask(run("ip a | grep ens192 | grep inet | xargs | cut -d ' ' -f 2 | cut -d \"/\" -f 2"))
    dns_list = run("cat /etc/resolv.conf | grep nameserver | cut -d ' ' -f 2").split("\\n")
    return (ip, gateway, netmask, dns_list[0], dns_list[1])

def get_os_info() -> tuple:
    # os, version, kernel version
    os = pf.system()
    version = pf.release()
    kernel_version = pf.version()
    return (os, version, kernel_version)


def get_storage_info() -> tuple:
    # drive capacity (gb), available space (gb)
    cap = int(run("df / | grep / | xargs | cut -d ' ' -f 4"))/1000000
    avail = int(run("df / | grep / | xargs | cut -d ' ' -f 3"))/1000000
    return (cap, avail)

def get_cpu_info() -> tuple:
    # model, num cpus, num cores
    model = None
    cpus = None
    cores = None
    return (model, cpus, cores)

def get_ram_info() -> tuple:
    # total ram (gb), available ram (gb)
    tot = int(run("free | grep Mem | xargs | cut -d ' ' -f 2"))/1000000
    avail = int(run("free | grep Mem | xargs | cut -d ' ' -f 4"))/1000000
    return (tot, avail)

def wp(file, str: str):
    file.write(f"{str}\n")
    print(str)

def make_log(info: tuple):
    print("")
    date = run("date")
    with open(f"./{info[0][0]}_system_report.log", "w") as file:
        wp(file, f"\tSystem Report - {date}")
        wp(file, "")
        wp(file, "Device Information")
        wp(file, f"\tHostname:\t{info[0][0]}")
        wp(file, f"\tDomain:\t\t{info[0][1]}")
        wp(file, "")

        wp(file, "Network Information")
        wp(file, f"\tIP Address:\t{info[1][0]}")
        wp(file, f"\tGateway:\t{info[1][1]}")
        wp(file, f"\tDNS 1:\t\t{info[1][2]}")
        wp(file, f"\tDNS 2:\t\t{info[1][3]}")
        wp(file, "")

        wp(file, "OS Information")
        wp(file, f"\tOperating System:\t{info[2][0]}")
        wp(file, f"\tOperating Version:\t{info[2][1]}")
        wp(file, f"\tKernel Version:\t\t{info[2][2]}")
        wp(file, "")

        wp(file, "Storage Information")
        wp(file, f"\tDrive Capacity:\t\t{info[3][0]} GB")
        wp(file, f"\tAvailable Space:\t{info[3][1]} GB")
        wp(file, "")

        wp(file, "Processor Information")
        wp(file, f"\tCPU Model:\t\t{info[4][0]}")
        wp(file, f"\tNumber of Processors:\t{info[4][1]}")
        wp(file, f"\tNumber of Cores:\t{info[4][2]}")
        wp(file, "")

        wp(file, "Memory Information")
        wp(file, f"\tTotal RAM:\t{info[5][0]} GB")
        wp(file, f"\tAvailable RAM:\t{info[5][1]} GB")


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