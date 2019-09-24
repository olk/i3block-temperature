#!/bin/python
'''
                     Copyright Oliver Kowalke 2018.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>. 
'''


import re
from ipmi import Tool
from nvidia import Smi
from nvme import NVMe
from subprocess import Popen, PIPE

def fork_gpu():
    options = Smi.QueryOptions()
    options.index()
    options.temperature()
    smi = Smi(options)
    return smi.execute()

def process_gpu_temp(status):
    exit_code, out, _ = status.wait()
    if 0 != exit_code:
        raise RuntimeError("failed to execute nvidia-smi")
    regex = re.compile(r'(\d+),\s+(\d+)')
    data = "GPU: "
    lines = out.splitlines()
    for line in lines:
        match = regex.search(line.rstrip())
        data += "%s°C " % match.group(2)
    return data.strip()

def fork_cpu_pch():
    options = Tool.QueryOptions()
    options.temperature()
    tool = Tool(options)
    return tool.execute();

def process_cpu_pch_temp(status):
    exit_code, out, _ = status.wait()
    if 0 != exit_code:
        raise RuntimeError("failed to execute ipmitool")
    regex = re.compile(r'CPU(\d+) Temp,(\d+).')
    data = "CPU: "
    tuples = regex.findall(out)
    for tpl in tuples:
        data += "%s°C " % tpl[1]
    data = data.strip()
    regex = re.compile(r'PCH Temp,(\d+).')
    match = regex.search(out)
    data += "  PCH: %s°C " % match.group(1)
    return data.strip()

def fork_nvme():
    options = NVMe.QueryOptions()
    options.temperature()
    tool = NVMe(options)
    return tool.execute();

def process_nvme_temp(status):
    exit_code, out, _ = status.wait()
    if 0 != exit_code:
        raise RuntimeError("failed to execute smartctl")
    data = "NVMe: "
    matches = re.findall(r'Temperature:\s+(\d+) Celsius', out)
    for match in matches:
        data += "%s°C " % match
    return data.strip()


if __name__ == "__main__":
    status_gpu = fork_gpu()
    status_cpu_pch = fork_cpu_pch()
    status_nvme = fork_nvme()
    print(process_gpu_temp(status_gpu) + "  " + process_cpu_pch_temp(status_cpu_pch) + "  " + process_nvme_temp(status_nvme))
