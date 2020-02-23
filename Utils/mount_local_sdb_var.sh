#!/bin/bash
sshfs localhost:$HOME/sdb/var var -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3
