import ipaddress
from subprocess import run

ipv4address = run(["curl checkip.amazonaws.com"], shell=True)
ipv6address = run(["curl https://ipv6.icanhazip.com"], shell=True)

ipv4 = ipaddress.IPv4Address(ipv4address)
ipv6 = ipaddress.IPv6Address(ipv6address)

if ipv4.is_global:
    ipv4_is_global = True
    if ipv4.is_link_local:
        ipv4_is_linklocal = True
        print("Ip v4 address is global and link-local!")
    elif not ipv4.is_link_local:
        ipv4_is_linklocal = False
        print("Ip v4 address is global but not link-local!")
elif not ipv4.is_global:
    ipv4_is_global = False
    if ipv4.is_link_local:
        ipv4_is_linklocal = True
        print("Ip v4 address isn't global but is link-local!")
    elif not ipv4.is_link_local:
        ipv4_is_linklocal = False
        print("Ip v4 adress isn't local neither global!")

if ipv6.is_global:
    ipv6_is_global = True
    if ipv6.is_link_local:
        ipv6_is_linklocal = True
        print("Ip v6 address is global and link-local!")
    elif not ipv6.is_link_local:
        ipv6_is_linklocal = False
        print("Ip v6 address is global but not link-local!")
elif not ipv6.is_global:
    ipv6_is_global = False
    if ipv6.is_link_local:
        ipv6_is_linklocal = True
        print("Ip v6 address isn't global but is link-local!")
    elif not ipv6.is_link_local:
        ipv6_is_linklocal = False
        print("Ip v6 adress isn't local neither global!")
