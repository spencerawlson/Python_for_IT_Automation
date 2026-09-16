# Import the FastAPI class from the FastAPI library.
# FastAPI allows us to create a web API using Python.
from fastapi import FastAPI

# Import the SystemMonitor class from our system_monitor.py file.
# SystemMonitor contains the methods used to collect information
# about the computer.
from system_monitor import SystemMonitor


# Create the FastAPI application.
# This object represents our API and contains its configuration.
app = FastAPI(

    # Name of the API displayed in the automatic documentation.
    title="Windows System Information API",

    # Current version of our API.
    version="1.0.0",

    # Description explaining the purpose of the API.
    description="A local API that provides CPU, memory, disk, "
                "network and other system information for Windows machines."
)


# Create an object from the SystemMonitor class.
# We will use this object to call the methods inside SystemMonitor.
monitor = SystemMonitor()


# Create the root endpoint of the API.
# @app.get("/") means this function runs when someone sends
# a GET request to http://127.0.0.1:8000/
@app.get("/")
def home():

    # Return information to the client in JSON format.
    return {
        "message": "Windows System Information API is running",
        "documentation": "/docs"
    }


# Create the /system endpoint.
# This endpoint returns general information about the computer
# and operating system.
@app.get("/system")
def get_system_information():

    # Call the get_system_information() method from our
    # SystemMonitor object and return its results.
    return monitor.get_system_information()


# Create the /cpu endpoint.
# This endpoint returns information about the computer's processor.
@app.get("/cpu")
def get_cpu_information():

    # Ask SystemMonitor to collect CPU information.
    return monitor.get_cpu_information()


# Create the /memory endpoint.
# This endpoint returns information about the computer's RAM.
@app.get("/memory")
def get_memory_information():

    # Ask SystemMonitor to collect memory information.
    return monitor.get_memory_information()


# Create the /disk endpoint.
# This endpoint returns information about the computer's storage devices.
@app.get("/disk")
def get_disk_information():

    # Ask SystemMonitor to collect disk information.
    return monitor.get_disk_information()


# Create the /network endpoint.
# This endpoint returns information about the computer's network.
@app.get("/network")
def get_network_information():

    # Ask SystemMonitor to collect network information.
    return monitor.get_network_information()


# Create the /complete endpoint.
# This endpoint combines the different types of system information
# into one complete report.
@app.get("/complete")
def get_complete_report():

    # Ask SystemMonitor to generate and return the complete report.
    return monitor.get_complete_report()