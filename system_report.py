#!/bin/python3.6
# Joey Guarino
# Feb 2024

import subprocess as sp

# runs a command and returns the result
def run(cmd) -> str:
    proc = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
    return str(proc.stdout.read())[2:-3]

# gets the hostname and domain of the machine and returns as (hostname, domain)
def get_device_info() -> tuple:
    hostname = run("hostname | cut -d '.' -f 1")
    domain = run("hostname | cut -d '.' -f 2")
    return (hostname, domain)

# changes the provided cidr notation to its netmask representation
def cidr_to_netmask(cidr) -> str:
    cidr = int(cidr)
    mask_bin = f"{'1'*cidr}{'0'*(32-cidr)}"
    out = f"{int(mask_bin[0:8], 2)}.{int(mask_bin[8:16], 2)}.{int(mask_bin[16:24], 2)}.{int(mask_bin[24:32], 2)}"
    return out

# gets network info and returns a tuple (ip_address, gateway_netmask, dns1, dns2)
def get_network_info() -> tuple:
    # ip, gateway, netmask, dns1, dns2
    ip = run("ip a | grep ens192 | grep inet | xargs | cut -d ' ' -f 2 | cut -d '/' -f 1")
    gateway = run("ip r | grep default | cut -d ' ' -f 3")
    netmask = cidr_to_netmask(run("ip a | grep ens192 | grep inet | xargs | cut -d ' ' -f 2 | cut -d \"/\" -f 2"))
    dns_list = run("cat /etc/resolv.conf | grep nameserver | cut -d ' ' -f 2").split("\\n")
    return (ip, gateway, netmask, dns_list[0], dns_list[1])

# gets os info and returns a tuple (os_name, os_version, kernel_version)
def get_os_info() -> tuple:
    # os, version, kernel version
    os = run("cat /etc/os-release | grep 'NAME=' | head -1 | cut -d '=' -f 2")[1:-1]
    version = run("cat /etc/os-release | grep VERSION_ID | cut -d '=' -f 2")[1:-1]
    kernel_version = run("uname -r")
    return (os, version, kernel_version)

# gets drive info and returns a tuple (total_capacity, available_space) both in GB
def get_storage_info() -> tuple:
    # drive capacity (gb), available space (gb)
    cap = int(run("df / | grep / | xargs | cut -d ' ' -f 4"))/1000000
    avail = int(run("df / | grep / | xargs | cut -d ' ' -f 3"))/1000000
    return (cap, avail)

# gets cpu info and returns a tuple (model, number_of_cpus, number_of_cores)
def get_cpu_info() -> tuple:
    # model, num cpus, num cores
    model = run("lscpu | grep 'Model name' | cut -d ':' -f 2 | xargs")
    cpus = run("lscpu | grep 'CPU(s):' | head -1 | cut -d ':' -f 2 | xargs")
    cores = int(run("lscpu | grep 'Core' | cut -d ':' -f 2 | xargs")) * int(cpus) # num cores * cores per cpu
    return (model, cpus, cores)

# gets memory info and returns a tuple (total_ram, available_ram) both in GB
def get_ram_info() -> tuple:
    # total ram (gb), available ram (gb)
    tot = int(run("free | grep Mem | xargs | cut -d ' ' -f 2"))/1000000
    avail = int(run("free | grep Mem | xargs | cut -d ' ' -f 4"))/1000000
    return (tot, avail)

# writes the string to the provided file and also prints it to the screen
def wp(file, str: str):
    file.write(f"{str}\n")
    print(str)

# makes the log of all the info
def make_log(info: tuple):
    print("")
    date = run("date")
    with open(f"./{info[0][0]}_system_report.log", "w") as file:
        wp(file, f"\tSystem Report - {date}")
        wp(file, "")
        wp(file, "Device Information")
        wp(file, f"\tHostname:\t\t{info[0][0]}")
        wp(file, f"\tDomain:\t\t\t{info[0][1]}")
        wp(file, "")

        wp(file, "Network Information")
        wp(file, f"\tIP Address:\t\t{info[1][0]}")
        wp(file, f"\tGateway:\t\t{info[1][1]}")
        wp(file, f"\tNetmask:\t\t{info[1][2]}")
        wp(file, f"\tDNS 1:\t\t\t{info[1][3]}")
        wp(file, f"\tDNS 2:\t\t\t{info[1][4]}")
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
        wp(file, f"\tTotal RAM:\t\t{info[5][0]} GB")
        wp(file, f"\tAvailable RAM:\t\t{info[5][1]} GB")


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