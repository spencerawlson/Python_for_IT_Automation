# Import os to interact with operating-system information,
# such as Windows environment variables.
import os

# Import platform to retrieve information about the
# operating system and processor.
import platform

# Import socket to retrieve hostname and work with
# IPv4 and IPv6 network address types.
import socket

# Import psutil to retrieve CPU, RAM, disk,
# and network information from the computer.
import psutil


# Create a class responsible for collecting
# information about the computer.
class SystemMonitor:

    # The constructor runs automatically whenever
    # a new SystemMonitor object is created.
    def __init__(self):

        # Get the hostname (computer name) of the machine.
        self.hostname = socket.gethostname()

        # Get the name of the operating system.
        # On this computer, this should return "Windows".
        self._operation_system = platform.system()

        # Get the operating system version.
        self._os_version = platform.version()


    # Return general information about the computer
    # and its operating system.
    def get_system_information(self):

        return {

            # Return the hostname stored when the object was created.
            "hostname": self.hostname,

            # Return the operating system name.
            "operating_system": self._operation_system,

            # Return the operating system version.
            "os_version": self._os_version,

            # Get information about the computer's processor.
            "processor": platform.processor(),
        }


    # Return information about the CPU.
    def get_cpu_information(self):

        return {

            # Number of physical CPU cores.
            # logical=False tells psutil not to count logical threads.
            "physical_cores": psutil.cpu_count(logical=False),

            # Number of logical CPU cores/threads.
            # This includes technologies such as Hyper-Threading.
            "logical_cores": psutil.cpu_count(logical=True),

            # Measure the current CPU usage percentage.
            # interval=1 measures CPU activity over one second.
            "cpu_usage_percent": psutil.cpu_percent(interval=1),

            # Get the current CPU frequency in MHz.
            "cpu_frequency": psutil.cpu_freq().current,
        }


    # Return information about the computer's RAM.
    def get_memory_information(self):

        # Retrieve the current virtual memory statistics.
        memory = psutil.virtual_memory()

        return {

            # Total amount of installed RAM converted to GB.
            "total_gb": self.bytes_to_gb(memory.total),

            # Amount of RAM currently available for programs.
            "available_gb": self.bytes_to_gb(memory.available),

            # Amount of RAM currently being used.
            "used_gb": self.bytes_to_gb(memory.used),

            # Percentage of RAM currently being used.
            "usage_percent": memory.percent,
        }


    # Return information about the Windows system drive.
    def get_disk_information(self):

        # Get the Windows system drive from the SystemDrive
        # environment variable.
        #
        # Usually this will return "C:".
        # If SystemDrive cannot be found, "C:" is used by default.
        #
        # "\\" adds the backslash so the final path becomes:
        # C:\
        disk_path = os.environ.get("SystemDrive", "C:") + "\\"

        # Retrieve storage usage information for the drive.
        disk = psutil.disk_usage(disk_path)

        return {

            # Total storage capacity converted from bytes to GB.
            "total_gb": self.bytes_to_gb(disk.total),

            # Amount of storage currently being used.
            "used_gb": self.bytes_to_gb(disk.used),

            # Amount of free storage remaining.
            "free_gb": self.bytes_to_gb(disk.free),

            # Percentage of the disk currently being used.
            "usage_percent": disk.percent,
        }


    # Return information about the computer's
    # network interfaces and network activity.
    def get_network_information(self):

        # Create an empty list that will eventually contain
        # information about every network interface.
        interfaces = []

        # Get all network interfaces and their addresses.
        #
        # .items() allows us to retrieve both:
        #     interface_name
        #     addresses
        #
        # Example interface names:
        # Ethernet
        # Wi-Fi
        # Loopback
        for interface_name, addresses in psutil.net_if_addrs().items():

            # Create a dictionary for the current network interface.
            interface = {

                # Store the interface name.
                "name": interface_name,

                # Create an empty list where IP addresses
                # belonging to this interface will be stored.
                "addresses": [],
            }


            # Loop through every address assigned
            # to the current network interface.
            for address in addresses:

                # Check whether the address is an IPv4 address.
                if address.family == socket.AF_INET:

                    # Add the IPv4 information to the
                    # addresses list for this interface.
                    interface["addresses"].append({

                        "type": "IPv4",

                        # Store the IPv4 address.
                        "address": address.address,

                        # Store the IPv4 subnet mask.
                        "subnet_mask": address.netmask,
                    })


                # Check whether the address is an IPv6 address.
                elif address.family == socket.AF_INET6:

                    # Add the IPv6 information to the
                    # addresses list for this interface.
                    interface["addresses"].append({

                        "type": "IPv6",

                        # Store the IPv6 address.
                        "address": address.address,

                        # Store the IPv6 subnet mask.
                        "subnet_mask": address.netmask,
                    })


            # Add the completed interface dictionary
            # to the interfaces list.
            interfaces.append(interface)


        # Retrieve network traffic statistics.
        network_io = psutil.net_io_counters()


        # Return the network information.
        return {

            # Return all network interfaces we collected.
            "interfaces": interfaces,

            # Total number of bytes transmitted by the computer
            # since the operating system started.
            "bytes_sent": network_io.bytes_sent,

            # Total number of bytes received by the computer
            # since the operating system started.
            "bytes_received": network_io.bytes_recv,
        }


    # Combine all of the previous methods into
    # one complete system report.
    def get_complete_report(self):

        return {

            # General system information.
            "system": self.get_system_information(),

            # CPU information.
            "cpu": self.get_cpu_information(),

            # Memory information.
            "memory": self.get_memory_information(),

            # Disk information.
            "disk": self.get_disk_information(),

            # Network information.
            "network": self.get_network_information(),
        }


    # staticmethod means this function belongs to the class
    # but does not need access to a specific object's attributes.
    @staticmethod
    def bytes_to_gb(bytes_value):

        # Computers commonly measure memory/storage using powers of 1024.
        #
        # 1024 bytes = 1 KB
        # 1024 KB    = 1 MB
        # 1024 MB    = 1 GB
        #
        # Therefore:
        # 1024 ** 3 = 1,073,741,824 bytes
        #
        # Divide the number of bytes by that value to convert to GB.
        # round(..., 2) keeps two decimal places.
        return round(bytes_value / (1024 ** 3), 2)