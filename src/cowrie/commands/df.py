# Copyright (c) 2025 Cowrie Developers
# See the COPYRIGHT file for more information

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_df(HoneyPotCommand):
    def call(self) -> None:
        self.write("Filesystem     1K-blocks    Used Available Use% Mounted on\n")
        self.write("udev              481352       0    481352   0% /dev\n")
        self.write("tmpfs             100140     928     99212   1% /run\n")
        self.write("/dev/sda1       20145664 4567892  14561234  24% /\n")
        self.write("tmpfs             500692       0    500692   0% /dev/shm\n")
        self.write("tmpfs               5120       0      5120   0% /run/lock\n")
        self.write("tmpfs             500692       0    500692   0% /sys/fs/cgroup\n")
        self.write("tmpfs             100140       0    100140   0% /run/user/1000\n")

commands["/bin/df"] = Command_df
commands["df"] = Command_df
