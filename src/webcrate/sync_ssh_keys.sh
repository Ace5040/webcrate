#!/bin/bash

if [[ -f /webcrate/ssh_keys/ssh_host_dsa_key ]];
  then
    rm /etc/ssh/ssh_host_dsa_key
    cp /webcrate/ssh_keys/ssh_host_dsa_key /etc/ssh/ssh_host_dsa_key
  else
    cp /etc/ssh/ssh_host_dsa_key /webcrate/ssh_keys/ssh_host_dsa_key
fi

if [[ -f /webcrate/ssh_keys/ssh_host_dsa_key.pub ]];
  then
    rm /etc/ssh/ssh_host_dsa_key.pub
    cp /webcrate/ssh_keys/ssh_host_dsa_key.pub /etc/ssh/ssh_host_dsa_key.pub
  else
    cp /etc/ssh/ssh_host_dsa_key.pub /webcrate/ssh_keys/ssh_host_dsa_key.pub
fi

if [[ -f /webcrate/ssh_keys/ssh_host_ecdsa_key ]];
  then
    rm /etc/ssh/ssh_host_ecdsa_key
    cp /webcrate/ssh_keys/ssh_host_ecdsa_key /etc/ssh/ssh_host_ecdsa_key
  else
    cp /etc/ssh/ssh_host_ecdsa_key /webcrate/ssh_keys/ssh_host_ecdsa_key
fi

if [[ -f /webcrate/ssh_keys/ssh_host_ecdsa_key.pub ]];
  then
    rm /etc/ssh/ssh_host_ecdsa_key.pub
    cp /webcrate/ssh_keys/ssh_host_ecdsa_key.pub /etc/ssh/ssh_host_ecdsa_key.pub
  else
    cp /etc/ssh/ssh_host_ecdsa_key.pub /webcrate/ssh_keys/ssh_host_ecdsa_key.pub
fi

if [[ -f /webcrate/ssh_keys/ssh_host_ed25519_key ]];
  then
    rm /etc/ssh/ssh_host_ed25519_key
    cp /webcrate/ssh_keys/ssh_host_ed25519_key /etc/ssh/ssh_host_ed25519_key
  else
    cp /etc/ssh/ssh_host_ed25519_key /webcrate/ssh_keys/ssh_host_ed25519_key
fi

if [[ -f /webcrate/ssh_keys/ssh_host_ed25519_key.pub ]];
  then
    rm /etc/ssh/ssh_host_ed25519_key.pub
    cp /webcrate/ssh_keys/ssh_host_ed25519_key.pub /etc/ssh/ssh_host_ed25519_key.pub
  else
    cp /etc/ssh/ssh_host_ed25519_key.pub /webcrate/ssh_keys/ssh_host_ed25519_key.pub
fi

if [[ -f /webcrate/ssh_keys/ssh_host_rsa_key ]];
  then
    rm /etc/ssh/ssh_host_rsa_key
    cp /webcrate/ssh_keys/ssh_host_rsa_key /etc/ssh/ssh_host_rsa_key
  else
    cp /etc/ssh/ssh_host_rsa_key /webcrate/ssh_keys/ssh_host_rsa_key
fi

if [[ -f /webcrate/ssh_keys/ssh_host_rsa_key.pub ]];
  then
    rm /etc/ssh/ssh_host_rsa_key.pub
    cp /webcrate/ssh_keys/ssh_host_rsa_key.pub /etc/ssh/ssh_host_rsa_key.pub
  else
    cp /etc/ssh/ssh_host_rsa_key.pub /webcrate/ssh_keys/ssh_host_rsa_key.pub
fi

chown -R $WEBCRATE_UID:$WEBCRATE_GID /webcrate/ssh_keys
