# Welcome to RAN Fusion
****v1.0.0 - Baseline***
## Overview

Welcome to the RANFusion, RAN Simulator, a simple tool that simulates the behavior and performance of 5G, and 6G networks, such as handover activities. Our simulator provides a detailed framework for testing and analyzing various components of 5G technology. 
Here's a sample result from running 10 UE and viewing the logs:

![Example Image](images/init-ue.png)

![Example Image](images/log.png)

![Example Image](images/InfluxDB-GUI.png)
## Features

- **Realistic RAN Simulation:** Experience accurately modeling 5G network elements and protocols.
- **Support Multiple gNodeB, Cell, Sector, UE**
- **API Enable** To add, Remove, and update each UE with its parameters
- **Customizable Scenarios:** Easily configure different network scenarios.
- **Supported Scenarios in this version:** Generate traffic for each UE per service type and soft handover inside the GnodeB(Intra-gNodeB Intra-Frequency Handover).
- **Performance Metrics via InfluxDB:** Performance Metrics: The simulator provides a comprehensive set of metrics, including throughput, latency, and packet loss. These metrics enable users to gain valuable insights into the performance and behavior of 5G networks under different conditions.

## Getting Started

### Prerequisites

Before you start, make sure you have the following installed:
- Windows, Linux, or macOS
- Python 3.x
- Install Dependencies via pip install -r requirements.txt

### Installation

Follow these steps to set up the RANFusion Simulator:

1. **Clone the Repository**
2. **Navigate to the Directory**
3. **RUN the setup.py and wait**
4. **Install InfluxDB**
5. **Get the API token of the Influxdb via GUI (http://localhost:8086/)**
6. **past Token into setup.py**
7. **run main.py**
   
   




   
