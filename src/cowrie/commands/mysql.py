# Copyright (c) 2025 Cowrie Developers
# See the COPYRIGHT file for more information

from __future__ import annotations

import time

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_mysql(HoneyPotCommand):
    def call(self) -> None:
        if not self.args:
            self.write("ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: NO)\n")
            return

        # Simple check for common arguments
        if "-u" in self.args and "-p" in self.args:
            user_idx = self.args.index("-u") + 1
            user = self.args[user_idx] if user_idx < len(self.args) else "root"
            
            self.write(f"Welcome to the MariaDB monitor.  Commands end with ; or \\g.\n")
            self.write(f"Your MariaDB connection id is {time.time_ns() % 10000}\n")
            self.write("Server version: 10.6.12-MariaDB-0ubuntu0.22.04.1 Ubuntu 22.04\n\n")
            self.write("Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.\n\n")
            self.write("Type 'help;' or '\\h' for help. Type '\\c' to clear the current input statement.\n\n")
            
            # Switch to interactive mode or just simulate a few commands
            # For now, let's just simulate the login and a bit of a fake shell if they give more commands or if we want to be more advanced
            # But the user asked for fake results, so maybe just a fake output is enough for now or a small interactive loop.
            
            self.protocol.ps1 = "mysql> "
            # We would need to handle lineReceived to make it truly interactive, but HoneyPotCommand can do that.
            self.is_interactive = True
            return

        self.write("ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)\n")

    def lineReceived(self, line: str) -> None:
        line = line.strip().lower()
        if line in ("exit", "quit", "\\q", "exit;", "quit;"):
            self.write("Bye\n")
            self.exit()
        elif line in ("show databases;", "show schemas;"):
            self.write("+--------------------+\n")
            self.write("| Database           |\n")
            self.write("+--------------------+\n")
            self.write("| information_schema |\n")
            self.write("| mysql              |\n")
            self.write("| performance_schema |\n")
            self.write("| sys                |\n")
            self.write("| wordpress          |\n")
            self.write("+--------------------+\n")
            self.write("5 rows in set (0.001 sec)\n\n")
        elif line.startswith("use "):
            db = line[4:].strip("; ")
            self.write(f"Database changed\n")
            self.protocol.ps1 = f"mysql [{db}]> "
        elif line == "show tables;" or line == "show tables from mysql;":
            self.write("+---------------------------+\n")
            self.write("| Tables_in_mysql           |\n")
            self.write("+---------------------------+\n")
            self.write("| column_stats              |\n")
            self.write("| columns_priv              |\n")
            self.write("| db                        |\n")
            self.write("| event                     |\n")
            self.write("| func                      |\n")
            self.write("| gtid_slave_pos            |\n")
            self.write("| help_category             |\n")
            self.write("| help_keyword              |\n")
            self.write("| help_relation             |\n")
            self.write("| help_topic                |\n")
            self.write("| host                      |\n")
            self.write("| index_stats               |\n")
            self.write("| innodb_index_stats        |\n")
            self.write("| innodb_table_stats        |\n")
            self.write("| plugin                    |\n")
            self.write("| proc                      |\n")
            self.write("| procs_priv                |\n")
            self.write("| proxies_priv              |\n")
            self.write("| roles_mapping             |\n")
            self.write("| servers                   |\n")
            self.write("| table_stats               |\n")
            self.write("| tables_priv               |\n")
            self.write("| time_zone                 |\n")
            self.write("| time_zone_leap_second     |\n")
            self.write("| time_zone_name            |\n")
            self.write("| time_zone_transition      |\n")
            self.write("| time_zone_transition_type |\n")
            self.write("| user                      |\n")
            self.write("+---------------------------+\n")
            self.write("28 rows in set (0.001 sec)\n\n")
        else:
            self.write(f"ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near '{line}' at line 1\n\n")
        
        self.write(self.protocol.ps1)

commands["/usr/bin/mysql"] = Command_mysql
commands["mysql"] = Command_mysql
