#!/bin/sh

exec dnsmasq \
  --no-hosts \
  --no-resolv \
  --no-negcache \
  --log-facility=- \
  --hostsdir=/dnsmasq-hosts \
  --resolv-file=/dnsmasq/resolv.conf \
  --pid-file=/dnsmasq/dnsmasq.pid \
  --keep-in-foreground
