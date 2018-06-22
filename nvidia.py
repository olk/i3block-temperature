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

from subprocess import Popen, PIPE

class Smi(object):
    class QueryOptions(object):
        def __init__(self, id=-1, noheader=True, nounit=True):
            self.__id = id
            self.__noheader = noheader
            self.__nounit = nounit
            self.__options = []

        def accounting_mode(self):
            self.__options.append("accounting_mode")

        def clock_current_sm(self):
            self.__options.append("clocks.current.sm")

        def clock_current_memory(self):
            self.__options.append("clocks.current.memory")

        def compute_mode(self):
            self.__options.append("compute_mode")

        def count(self):
            self.__options.append("count")

        def display_active(self):
            self.__options.append("display_active")

        def display_mode(self):
            self.__options.append("display_mode")

        def fan_speed(self):
            self.__options.append("fan.speed")

        def index(self):
            self.__options.append("index")

        def memory_free(self):
            self.__options.append("memory.free")

        def memory_total(self):
            self.__options.append("memory.total")

        def memory_used(self):
            self.__options.append("memory.used")

        def name(self):
            self.__options.append("name")

        def pci_bus_id(self):
            self.__options.append("pci.bus_id")

        def pci_bus(self):
            self.__options.append("pci.bus")

        def pci_device_id(self):
            self.__options.append("pci.device_id")

        def pci_device(self):
            self.__options.append("pci.device")

        def pci_sub_device_id(self):
            self.__options.append("pci.sub_device_id")

        def pci_domain(self):
            self.__options.append("pci.domain")

        def performance_state(self):
            self.__options.append("pstate")

        def persistence_mode(self):
            self.__options.append("persistence_mode")

        def power_draw(self):
            self.__options.append("power.draw")

        def power_limit(self):
            self.__options.append("power.limit")

        def power_management(self):
            self.__options.append("power.management")

        def serial(self):
            self.__options.append("serial")

        def temperature(self):
            self.__options.append("temperature.gpu")

        def utilization_gpu(self):
            self.__options.append("untilization.gpu")

        def utilization_memory(self):
            self.__options.append("untilization.memory")

        def uuid(self):
            self.__options.append("uuid")

        def arguments(self):
            args = []
            if self.__options:
                qry_args = ""
                for option in self.__options:
                    qry_args += "," + option
                args.extend(["--query-gpu=" + qry_args[1:]])
                format_args = ""
                if self.__noheader:
                    format_args += ",noheader"
                if self.__nounit:
                    format_args += ",nounits"
                args.extend(["--format=csv" + format_args])
            else:
                args.extend(["-q"])
            if 0 <= self.__id:
                args.extend(["-id " + self.__id])
            return args


    class ModificationOptions(object):
        def __init__(self):
            pass

        def arguments(self):
            args = []
            return args


    class Status(object):
        def __init__(self, proc, timeout=2):
            self.__proc = proc
            self.__timeout = timeout

        def wait(self):
            try:
                out, err = self.__proc.communicate(timeout=self.__timeout)
            except TimeoutExpired:
                self.__proc.kill()
                out, err = self.__proc.communicate()
            return [self.__proc.returncode, out, err]


    def _locate(self):
        with Popen(["which", "nvidia-smi"],
                    stdout=PIPE,
                    universal_newlines=True) as proc:
            try:
                out, _ = proc.communicate(timeout=self.timeout)
            except TimeoutExpired:
                proc.kill()
                out, _ = proc.communicate()
        return out.strip()

    def __init__(self, options, timeout=1):
        self.timeout = timeout
        self.cmd = self._locate()
        if not self.cmd:
            raise IOError("failed to locate nvidia-smi")
        if not isinstance(options, (Smi.QueryOptions, Smi.ModificationOptions)):
            raise TypeError("invalid options provided")
        self.args = options.arguments()

    def execute(self):
        return Smi.Status(Popen([self.cmd] + self.args,
                    stdout=PIPE, stderr=PIPE,
                    universal_newlines=True))
