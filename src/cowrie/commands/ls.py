from __future__ import annotations
from twisted.python import log
import getopt
import os.path
import stat
import time
from cowrie.shell import fs
from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.pwd import Group, Passwd

commands = {}


class Command_ls(HoneyPotCommand):
    def uid2name(self, uid: int) -> str:
        try:
            name: str = Passwd().getpwuid(uid)["pw_name"]
        except Exception:
            return str(uid)
        else:
            return name

    def gid2name(self, gid: int) -> str:
        try:
            group: str = Group().getgrgid(gid)["gr_name"]
        except Exception:
            return str(gid)
        else:
            return group

    def call(self) -> None:
        path = self.protocol.cwd
        paths = []
        self.showHidden = False
        self.showDirectories = False
        self.showHumanReadable = False
        func = self.do_ls_normal

        # Parse options or display no files
        try:
            opts, args = getopt.gnu_getopt(
                self.args,
                "1@ABCFGHLOPRSTUWabcdefghiklmnopqrstuvwx",
                ["help", "version", "param"],
            )
        except getopt.GetoptError as err:
            self.errorWrite(f"ls: {err}\n")
            self.errorWrite("Try 'ls --help' for more information.\n")
            return
        for x, _a in opts:
            if x in ("-l"):
                func = self.do_ls_l
            if x in ("-h"):
                self.showHumanReadable = True

            if x in ("-a"):
                self.showHidden = True
            if x in ("-d"):
                self.showDirectories = True

        for arg in args:
            paths.append(self.protocol.fs.resolve_path(arg, self.protocol.cwd))

        if not paths:
            func(path)
        else:
            for path in paths:
                func(path)

    def get_dir_files(self, path):
        try:
            if self.protocol.fs.isdir(path) and not self.showDirectories:
                files = self.protocol.fs.get_path(path)[:]
                if self.showHidden:
                    dot = self.protocol.fs.getfile(path)[:]
                    dot[fs.A_NAME] = "."
                    files.append(dot)
                    dotdot = self.protocol.fs.getfile(os.path.split(path)[0])[:]
                    if not dotdot:
                        dotdot = self.protocol.fs.getfile(path)[:]
                    dotdot[fs.A_NAME] = ".."
                    files.append(dotdot)
                else:
                    files = [x for x in files if not x[fs.A_NAME].startswith(".")]
                files.sort()
            else:
                file = self.protocol.fs.getfile(path)[:]
                file[fs.A_NAME] = path
                files = [file]
        except Exception:
            self.errorWrite(f"ls: cannot access {path}: No such file or directory\n")
            return
        return files

    def do_ls_normal(self, path: str) -> None:
        files = self.get_dir_files(path)
        if not files:
            return

        # Use a list of tuples (visible_name, color_name)
        # where color_name is the name with ANSI codes
        file_list = []
        for f in files:
            name = f[fs.A_NAME]
            color_name = name
            if f[fs.A_TYPE] == fs.T_DIR:
                color_name = f"\033[1;34m{name}\033[0m"
            elif f[fs.A_TYPE] == fs.T_LINK:
                color_name = f"\033[1;36m{name}\033[0m"
            elif f[fs.A_MODE] & stat.S_IXUSR:
                color_name = f"\033[1;32m{name}\033[0m"
            file_list.append((name, color_name))

        if not file_list:
            return

        maxlen = max(len(x[0]) for x in file_list)

        try:
            wincols = int(self.environ.get("COLUMNS", 80))
        except Exception:
            wincols = 80

        if wincols <= 0:
            wincols = 80

        perline = int(wincols / (maxlen + 1))
        if perline <= 0:
            perline = 1

        count = 0
        for name, color_name in file_list:
            if count == perline:
                count = 0
                self.write("\n")
            # We use name for padding but color_name for writing
            self.write(color_name + " " * (maxlen + 1 - len(name)))
            count += 1
        self.write("\n")

    def do_ls_l(self, path: str) -> None:
        """
        Display detailed information about files
        Mimics the output of GNU ls -l and supports the following options:
        -a, -h

        :param path: The path to list
        """
        files = self.get_dir_files(path)
        if not files:
            return
        # Create a list to hold formatted sizes for display
        formatted_sizes = []
        filesize_str_extent = 0
        if len(files):
            filesize_str_extent = max(len(str(x[fs.A_SIZE])) for x in files)
            if self.showHumanReadable:
                for x in files:
                    size = x[fs.A_SIZE]  # Original size
                    if size >= 1024 * 1024 * 1024:
                        formatted_size = f"{size / 1024 / 1024 / 1024:.1f}G"
                    elif size >= 1024 * 1024:
                        formatted_size = f"{size / 1024 / 1024:.1f}M"
                    elif size >= 1024:
                        formatted_size = f"{size / 1024:.1f}K"
                    else:
                        formatted_size = str(size)

                    formatted_sizes.append(formatted_size)
                # Recalculate the extent with the formatted sizes
                filesize_str_extent = max(len(size) for size in formatted_sizes)
            else:
                formatted_sizes = [str(x[fs.A_SIZE]) for x in files]

        try:
            wincols = int(self.environ.get("COLUMNS", 80))
        except (TypeError, ValueError):
            wincols = 80

        if wincols <= 0:
            wincols = 80

        user_name_str_extent = 0
        if len(files):
            user_name_str_extent = max(len(self.uid2name(x[fs.A_UID])) for x in files)

        group_name_str_extent = 0
        if len(files):
            group_name_str_extent = max(len(self.gid2name(x[fs.A_GID])) for x in files)

        for i, file in enumerate(files):
            if file[fs.A_NAME].startswith(".") and not self.showHidden:
                continue

            perms = ["-"] * 10
            if file[fs.A_MODE] & stat.S_IRUSR:
                perms[1] = "r"
            if file[fs.A_MODE] & stat.S_IWUSR:
                perms[2] = "w"
            if file[fs.A_MODE] & stat.S_IXUSR:
                perms[3] = "x"
            if file[fs.A_MODE] & stat.S_ISUID:
                perms[3] = "S"
            if file[fs.A_MODE] & stat.S_IXUSR and file[fs.A_MODE] & stat.S_ISUID:
                perms[3] = "s"

            if file[fs.A_MODE] & stat.S_IRGRP:
                perms[4] = "r"
            if file[fs.A_MODE] & stat.S_IWGRP:
                perms[5] = "w"
            if file[fs.A_MODE] & stat.S_IXGRP:
                perms[6] = "x"
            if file[fs.A_MODE] & stat.S_ISGID:
                perms[6] = "S"
            if file[fs.A_MODE] & stat.S_IXGRP and file[fs.A_MODE] & stat.S_ISGID:
                perms[6] = "s"

            if file[fs.A_MODE] & stat.S_IROTH:
                perms[7] = "r"
            if file[fs.A_MODE] & stat.S_IWOTH:
                perms[8] = "w"
            if file[fs.A_MODE] & stat.S_IXOTH:
                perms[9] = "x"
            if file[fs.A_MODE] & stat.S_ISVTX:
                perms[9] = "T"
            if file[fs.A_MODE] & stat.S_IXOTH and file[fs.A_MODE] & stat.S_ISVTX:
                perms[9] = "t"

            linktarget = ""

            name = file[fs.A_NAME]
            color_name = name
            if file[fs.A_TYPE] == fs.T_DIR:
                perms[0] = "d"
                color_name = f"\033[1;34m{name}\033[0m"
            elif file[fs.A_TYPE] == fs.T_LINK:
                perms[0] = "l"
                color_name = f"\033[1;36m{name}\033[0m"
                linktarget = f" -> {file[fs.A_TARGET]}"
            elif file[fs.A_MODE] & stat.S_IXUSR:
                color_name = f"\033[1;32m{name}\033[0m"

            permstr = "".join(perms)
            ctime = time.localtime(file[fs.A_CTIME])

            line = "{} 1 {} {} {} {} {}{}".format(
                permstr,
                self.uid2name(file[fs.A_UID]).ljust(user_name_str_extent),
                self.gid2name(file[fs.A_GID]).ljust(group_name_str_extent),
                formatted_sizes[i].rjust(filesize_str_extent),
                time.strftime("%Y-%m-%d %H:%M", ctime),
                color_name,
                linktarget,
            )

            self.write(f"{line}\n")


commands["/bin/ls"] = Command_ls
commands["ls"] = Command_ls
commands["/bin/dir"] = Command_ls
commands["dir"] = Command_ls
