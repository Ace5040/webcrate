#!/bin/bash

if [[ -f /sitesbox/ssh_keys/ssh_host_dsa_key ]];
  then
    rm /etc/ssh/ssh_host_dsa_key
    cp /sitesbox/ssh_keys/ssh_host_dsa_key /etc/ssh/ssh_host_dsa_key
  else
    cp /etc/ssh/ssh_host_dsa_key /sitesbox/ssh_keys/ssh_host_dsa_key
fi

if [[ -f /sitesbox/ssh_keys/ssh_host_dsa_key.pub ]];
  then
    rm /etc/ssh/ssh_host_dsa_key.pub
    cp /sitesbox/ssh_keys/ssh_host_dsa_key.pub /etc/ssh/ssh_host_dsa_key.pub
  else
    cp /etc/ssh/ssh_host_dsa_key.pub /sitesbox/ssh_keys/ssh_host_dsa_key.pub
fi

if [[ -f /sitesbox/ssh_keys/ssh_host_ecdsa_key ]];
  then
    rm /etc/ssh/ssh_host_ecdsa_key
    cp /sitesbox/ssh_keys/ssh_host_ecdsa_key /etc/ssh/ssh_host_ecdsa_key
  else
    cp /etc/ssh/ssh_host_ecdsa_key /sitesbox/ssh_keys/ssh_host_ecdsa_key
fi

if [[ -f /sitesbox/ssh_keys/ssh_host_ecdsa_key.pub ]];
  then
    rm /etc/ssh/ssh_host_ecdsa_key.pub
    cp /sitesbox/ssh_keys/ssh_host_ecdsa_key.pub /etc/ssh/ssh_host_ecdsa_key.pub
  else
    cp /etc/ssh/ssh_host_ecdsa_key.pub /sitesbox/ssh_keys/ssh_host_ecdsa_key.pub
fi

if [[ -f /sitesbox/ssh_keys/ssh_host_ed25519_key ]];
  then
    rm /etc/ssh/ssh_host_ed25519_key
    cp /sitesbox/ssh_keys/ssh_host_ed25519_key /etc/ssh/ssh_host_ed25519_key
  else
    cp /etc/ssh/ssh_host_ed25519_key /sitesbox/ssh_keys/ssh_host_ed25519_key
fi

if [[ -f /sitesbox/ssh_keys/ssh_host_ed25519_key.pub ]];
  then
    rm /etc/ssh/ssh_host_ed25519_key.pub
    cp /sitesbox/ssh_keys/ssh_host_ed25519_key.pub /etc/ssh/ssh_host_ed25519_key.pub
  else
    cp /etc/ssh/ssh_host_ed25519_key.pub /sitesbox/ssh_keys/ssh_host_ed25519_key.pub
fi

if [[ -f /sitesbox/ssh_keys/ssh_host_rsa_key ]];
  then
    rm /etc/ssh/ssh_host_rsa_key
    cp /sitesbox/ssh_keys/ssh_host_rsa_key /etc/ssh/ssh_host_rsa_key
  else
    cp /etc/ssh/ssh_host_rsa_key /sitesbox/ssh_keys/ssh_host_rsa_key
fi

if [[ -f /sitesbox/ssh_keys/ssh_host_rsa_key.pub ]];
  then
    rm /etc/ssh/ssh_host_rsa_key.pub
    cp /sitesbox/ssh_keys/ssh_host_rsa_key.pub /etc/ssh/ssh_host_rsa_key.pub
  else
    cp /etc/ssh/ssh_host_rsa_key.pub /sitesbox/ssh_keys/ssh_host_rsa_key.pub
fi
