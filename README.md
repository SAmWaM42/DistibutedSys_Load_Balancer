# Dynamic Load Balancer using Consistent Hashing

## Participants

-**Gichuru Samuel Wamae  157660**
-**Tashobya Daniel Mutabazi 169494**
-**Omedi Alvin Eredi 168560**
-**Danni Podho 168333**



## Overview

This project implements a dynamic load balancing system using **consistent hashing** with **virtual servers** to distribute requests across multiple backend server replicas.

The system is capable of:

- Dynamically spawning server replicas
- Removing active replicas
- Monitoring server health through heartbeat requests
- Automatically replacing failed servers
- Maintaining request routing using a consistent hashing ring
- Visualizing server statistics through a simple client dashboard

Docker is used to simulate multiple backend servers while Flask provides the HTTP API for communication between the client, load balancer and replicas.

---

# Features

- Consistent Hashing
- Virtual Server Mapping
- Dynamic Addition and Removal of Replicas
- Automatic Failure Detection
- Automatic Replica Recovery
- Docker Container Management
- Runtime Statistics Dashboard
- Simulation Scripts for Experimental Evaluation

---

# Project Structure

```
.
├── Balancer
│   ├── balancer.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── Client
│   ├── Figures
│   │   ├── A1.png
│   │   ├── A2.png
│   │   ├── A3_bar.png
│   │   └── A3_line.png
│   ├── request.py
│   ├── simulation.py
│   ├── requirements.txt
│   └── templates
│       └── dashboard.html
│
├── Server
│   ├── routes.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── setup.sh
├── simulate.sh
├── test.py
└── README.md
```

---

# System Architecture

```
                 Client
                    │
                    │ HTTP Requests
                    ▼
          +----------------------+
          |    Load Balancer     |
          |----------------------|
          | Consistent Hash Ring |
          | Virtual Servers      |
          | Health Monitor       |
          +----------------------+
            │      │        │
            ▼      ▼        ▼
       Server1  Server2  Server3
          │        │        │
      Docker    Docker   Docker
     Container Container Container
```

---

# Components

## Load Balancer

The load balancer is responsible for:

- Maintaining the consistent hashing ring
- Mapping requests onto virtual servers
- Creating and removing Docker containers
- Forwarding client requests
- Monitoring server health
- Automatically replacing failed servers
- Recording runtime statistics

---

## Backend Servers

Each backend server executes inside its own Docker container.

Each server exposes:

- Home endpoint
- Heartbeat endpoint
- Server identification

---

## Client

The client application is responsible for:

- Sending concurrent requests
- Collecting runtime statistics
- Displaying the dashboard
- Running experimental simulations

---

# Consistent Hashing

Incoming requests are assigned positions on a fixed-size hash ring.

Each physical server is represented by several **virtual servers** positioned throughout the ring.

When a request arrives:

1. The request identifier is hashed.
2. The corresponding ring slot is computed.
3. The ring is searched clockwise until a virtual server is encountered.
4. The request is forwarded to the associated physical server.

Using virtual servers improves load distribution and minimizes request redistribution whenever replicas join or leave the system.

---

# Monitoring

A background monitoring thread periodically sends heartbeat requests to every active server.

If a server becomes unavailable:

1. The failed replica is removed from the hash ring.
2. The Docker container is terminated.
3. A replacement container is created.
4. The replacement server is inserted into the ring.
5. The system continues serving requests without manual intervention.

---

# REST API

## Replica Information

```
GET /rep
```

Returns all active replicas.

---

## Add Replicas

```
POST /add
```

Example request:

```json
{
    "n":2
}
```

or

```json
{
    "n":2,
    "hostnames":[
        "serverA",
        "serverB"
    ]
}
```

---

## Remove Replicas

```
POST /rm
```

Example:

```json
{
    "n":1
}
```

or

```json
{
    "n":1,
    "hostnames":[
        "serverA"
    ]
}
```

---

## Runtime Statistics

```
GET /statistics
```

Returns statistics used by the client dashboard.

---

## Forward Requests

Any remaining GET request is automatically forwarded to an available server using the consistent hashing ring.

Example:

```
GET /home
```

---

# Installation

## Requirements

- Python 3
- Docker
- Bash

---

## Initial Setup

Make the setup script executable

```bash
chmod +x setup.sh
```

Run

```bash
./setup.sh
```

The setup script automatically:

- Builds the backend server Docker image
- Builds the load balancer Docker image
- Creates the Docker network
- Starts the load balancer
- Installs the Python dependencies required by the client

---

# Running Simulations

Execute

```bash
chmod +x simulate.sh
./simulate.sh
```

The simulation script performs the required experimental evaluation by:

- Generating the request distribution graph
- Generating the scalability graph
- Simulating server failure
- Producing figures stored inside

```
Client/Figures
```

---

# Experimental Results

## A-1 Request Distribution

10,000 requests were issued while maintaining three server replicas.

### Observation

The workload was distributed across all active replicas. Although the distribution was not perfectly uniform, no individual server handled more than approximately **50%** of the total workload. This demonstrates that the chosen hashing strategy provides a reasonable distribution while maintaining deterministic request routing.

---

## A-2 Scalability

The number of replicas was increased from **2** to **5** while maintaining a workload of **10,000 requests**.

### Observation

As additional replicas were introduced, the average workload handled by each server decreased proportionally. Since the experiment used only four measurements (N = 2–5), the resulting graph appears as connected straight line segments rather than a smooth curve.

---

## A-3 Fault Tolerance

Server failures were simulated while the monitoring thread remained active.

### Observation

The monitoring process successfully detected failed replicas, removed them from the consistent hashing ring and automatically launched replacement Docker containers. Runtime statistics illustrating this behaviour are available through the dashboard and the accompanying figures.

---

## A-4 Modified Hash Functions

The request and virtual server hash functions were modified and compared with the original implementation.

### Observation

Using a simplified linear hashing function resulted in a noticeably biased request distribution, with a significantly larger proportion of requests being directed toward a single server. This highlights the importance of selecting hash functions that produce a more uniform distribution across the hash ring.

---

# Technologies Used

- Python
- Flask
- Docker
- Requests
- Jinja2
- Matplotlib
- ThreadPoolExecutor
- Bash

---

# Known Limitations

- Tested on Linux.
- Uses Flask's built-in development server.
- Statistics are maintained in memory.
- Designed for execution on a single Docker host.
- Monitoring uses periodic heartbeat polling rather than event-driven failure detection.

---

# Future Improvements

Potential extensions include:

- Asynchronous request forwarding
- Persistent statistics storage
- Multiple coordinated load balancers
- Configurable monitoring intervals
- Improved dashboard visualizations
- More advanced hashing strategies

---

