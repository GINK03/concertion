#!/usr/bin/bash
sudo socat TCP-LISTEN:443,reuseaddr,pktinfo,fork TCP:127.0.0.1:8443
