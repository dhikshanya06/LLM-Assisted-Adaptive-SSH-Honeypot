# Copyright (c) 2025 Cowrie Developers
# See the COPYRIGHT file for more information

from __future__ import annotations

import random
import time

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_nmap(HoneyPotCommand):
    def call(self) -> None:
        if not self.args:
            self.write("nmap: missing host operand\n")
            self.write("Try 'nmap --help' for more information.\n")
            return

        host = self.args[-1]
        
        # Simulate some delay
        self.write(f"\nStarting Nmap 7.92 ( https://nmap.org ) at {time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        
        # Random delay for realism
        # We don't want to block the reactor for too long though
        
        if "-V" in self.args or "--version" in self.args:
            self.write("Nmap version 7.92 ( https://nmap.org )\n")
            self.write("Platform: x86_64-pc-linux-gnu\n")
            self.write("Compiled with: liblua-5.3.6 openssl-3.0.2 libz-1.2.11 libpcre-8.39 libpcap-1.10.1 nmap-libdnet-1.12 ipv6\n")
            return

        if "--help" in self.args or "-h" in self.args:
            self.write("Nmap 7.92 ( https://nmap.org )\n")
            self.write("Usage: nmap [Scan Type(s)] [Options] {target specification}\n")
            self.write("TARGET SPECIFICATION:\n")
            self.write("  Can pass hostnames, IP addresses, networks, etc.\n")
            self.write("  Ex: scanme.nmap.org, microsoft.com/24, 192.168.0.1; 10.0.0-255.1-254\n")
            # ... truncated help ...
            return

        self.write(f"Nmap scan report for {host}\n")
        self.write("Host is up (0.00045s latency).\n")
        self.write("Not shown: 997 closed tcp ports (reset)\n")
        self.write("PORT    STATE SERVICE\n")
        self.write("22/tcp  open  ssh\n")
        self.write("80/tcp  open  http\n")
        self.write("443/tcp open  https\n")
        self.write("\n")
        self.write(f"Nmap done: 1 IP address (1 host up) scanned in {random.uniform(0.1, 0.5):.2f} seconds\n")

commands["/usr/bin/nmap"] = Command_nmap
commands["nmap"] = Command_nmap
