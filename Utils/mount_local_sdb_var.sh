#!/bin/bash
sshfs 127.0.0.1:$HOME/sdb/var var -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3
