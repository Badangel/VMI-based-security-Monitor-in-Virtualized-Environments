#!/usr/bin/env python
"""
The LibVMI Library is an introspection library that simplifies access to
memory in a target virtual machine or in a file containing a dump of
a system's physical memory.  LibVMI is based on the XenAccess Library.

Copyright 2011 Sandia Corporation. Under the terms of Contract
DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government
retains certain rights in this software.

Author: Bryan D. Payne (bdpayne@acm.org)

This file is part of LibVMI.

LibVMI is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

LibVMI is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
License for more details.

You should have received a copy of the GNU Lesser General Public License
along with LibVMI.  If not, see <http://www.gnu.org/licenses/>.
"""
import pyvmi
import sys

def get_os_params(vmi):
    ostype = vmi.get_ostype()
    if ostype.lower() == "windows":
        return get_windows_params(vmi)
    elif ostype.lower() == "linux":
        return get_linux_params(vmi)
    else:
        print("Sorry, {} ostype is not supported in this example yet.".format(
            ostype))
        exit(1)


def get_linux_params(vmi):
    tasks_offset = vmi.get_offset("linux_tasks")
    name_offset = vmi.get_offset("linux_name") - tasks_offset
    pid_offset = vmi.get_offset("linux_pid") - tasks_offset

    list_head = vmi.translate_ksym2v("init_task")

    return (tasks_offset, name_offset, pid_offset, list_head)


def get_windows_params(vmi):
    tasks_offset = vmi.get_offset("win_tasks")
    name_offset = vmi.get_offset("win_pname") - tasks_offset
    pid_offset = vmi.get_offset("win_pid") - tasks_offset

    list_head = vmi.read_addr_ksym("PsInitialSystemProcess")

    return (tasks_offset, name_offset, pid_offset, list_head)


def processes(vmi):
    tasks_offset, name_offset, pid_offset, list_head = get_os_params(vmi)

    next_process = vmi.read_addr_va(list_head + tasks_offset, 0)
    list_head = next_process

    while True:
        procname = vmi.read_str_va(next_process + name_offset, 0)
        pid = vmi.read_32_va(next_process + pid_offset, 0)
        next_process = vmi.read_addr_va(next_process, 0)

        if (pid < 1<<16):
            yield pid, procname
        if (list_head == next_process):
            break

def main(argv):
    vmi = pyvmi.init(argv[1], "complete")

    if vmi.get_access_mode() == 'file':
        print("Process listing for File {}".format(vmi.get_name()))
    else:
        print("Process listing for VM {}".format(vmi.get_name()))

    for pid, procname in processes(vmi):
        print "[%5d] %s" % (pid, procname)

if __name__ == "__main__":
    main(sys.argv)
