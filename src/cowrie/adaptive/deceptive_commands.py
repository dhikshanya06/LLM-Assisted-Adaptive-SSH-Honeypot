DECEPTIVE_COMMANDS = {
    'mysql': "Welcome to the MariaDB monitor.  Commands end with ; or \\g.\nYour MariaDB connection id is 132\nServer version: 10.6.12-MariaDB-0ubuntu0.22.04.1 Ubuntu 22.04\n\nCopyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.\n\nType 'help;' or '\\h' for help. Type '\\c' to clear the current input statement.\n\nmysql> \n",
    'nmap': "Nmap 7.91 ( https://nmap.org )\nUsage: nmap [Scan Type(s)] [Options] {target specification}\nQUICK HELP: nmap -v -A scanme.nmap.org\n",
    'docker': "CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES\n",
    'sudo': "root is not in the sudoers file.  This incident will be reported.\n",
    'iptables': "iptables v1.8.7 (nf_tables): can't initialize iptables table `filter': Table does not exist (do you need to insmod?)\n",
    'git': "usage: git [--version] [--help] [-C <path>] [-c <name>=<value>]\n           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]\n           [-p | --paginate | -P | --no-pager] [--no-replace-objects] [--bare]\n           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]\n           <command> [<args>]\n",
    'python3': "Python 3.10.12 (main, Jun 11 2023, 05:26:28) [GCC 11.4.0] on linux\nType \"help\", \"copyright\", \"credits\" or \"license\" for more information.\n>>> \n"
}

def get_deceptive_output(command):
    return DECEPTIVE_COMMANDS.get(command)
