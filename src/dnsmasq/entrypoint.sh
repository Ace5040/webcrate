#!/bin/sh

exec dnsmasq \
  --no-hosts \
  --log-facility=- \
  --hostsdir=/dnsmasq/hosts\
  --resolv-file=/dnsmasq/resolv.conf \
  --keep-in-foreground

# --all-servers \
# --strict-order \
# --no-negcache \

# --auth-zone=<domain>[,<subnet>[/<prefix length>][,<subnet>[/<prefix length>].....][,exclude:<subnet>[/<prefix length>]].....]
#   Define a DNS zone for which dnsmasq acts as authoritative server. Locally defined DNS records which are in the domain will be served. If subnet(s) are given, A and AAAA records must be in one of the specified subnets.
#   As alternative to directly specifying the subnets, it's possible to give the name of an interface, in which case the subnets implied by that interface's configured addresses and netmask/prefix-length are used; this is useful when using constructed DHCP ranges as the actual address is dynamic and not known when configuring dnsmasq. The interface addresses may be confined to only IPv6 addresses using <interface>/6 or to only IPv4 using <interface>/4. This is useful when an interface has dynamically determined global IPv6 addresses which should appear in the zone, but RFC1918 IPv4 addresses which should not. Interface-name and address-literal subnet specifications may be used freely in the same --auth-zone declaration.
#   It's possible to exclude certain IP addresses from responses. It can be used, to make sure that answers contain only global routeable IP addresses (by excluding loopback, RFC1918 and ULA addresses).
#   The subnet(s) are also used to define in-addr.arpa and ip6.arpa domains which are served for reverse-DNS queries. If not specified, the prefix length defaults to 24 for IPv4 and 64 for IPv6. For IPv4 subnets, the prefix length should be have the value 8, 16 or 24 unless you are familiar with RFC 2317 and have arranged the in-addr.arpa delegation accordingly. Note that if no subnets are specified, then no reverse queries are answered.
# --auth-soa=<serial>[,<hostmaster>[,<refresh>[,<retry>[,<expiry>]]]]
#   Specify fields in the SOA record associated with authoritative zones. Note that this is optional, all the values are set to sane defaults.
# --auth-sec-servers=<domain>[,<domain>[,<domain>...]]
#   Specify any secondary servers for a zone for which dnsmasq is authoritative. These servers must be configured to get zone data from dnsmasq by zone transfer, and answer queries for the same authoritative zones as dnsmasq.
# --auth-peer=<ip-address>[,<ip-address>[,<ip-address>...]]
#   Specify the addresses of secondary servers which are allowed to initiate zone transfer (AXFR) requests for zones for which dnsmasq is authoritative. If this option is not given but --auth-sec-servers is, then AXFR requests will be accepted from any secondary. Specifying --auth-peer without --auth-sec-servers enables zone transfer but does not advertise the secondary in NS records returned by dnsmasq.
