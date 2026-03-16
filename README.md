# 🔄 Real-Time Streaming Data Pipeline

A containerized real-time data pipeline built with Apache Kafka, Kubernetes, and Neo4j — processing high-volume NYC taxi trip data and enabling graph-based analytics using BFS and PageRank algorithms.

## 🏗️ Architecture
```
NYC Taxi Data (Parquet) → Kafka Producer → Kafka Broker → Neo4j Sink Connector → Neo4j Graph DB → Graph Analytics (BFS + PageRank)
```

## 🛠️ Tech Stack
- **Apache Kafka** — Real-time message streaming
- **Apache Zookeeper** — Kafka cluster coordination
- **Kubernetes** — Container orchestration
- **Neo4j** — Graph database for storing trip relationships
- **Neo4j Graph Data Science (GDS)** — BFS and PageRank algorithms
- **Docker** — Containerization
- **Python** — Data loading and graph interface

## 📁 Dataset
- **Source:** NYC Taxi Trip Data (Yellow Cab, March 2022)
- **Format:** Parquet
- **Scope:** Bronx borough trips filtered by location IDs

## ⚙️ Components

### `data_loader.py`
- Reads NYC taxi parquet data
- Filters trips within the Bronx
- Cleans and transforms data
- Loads trips into Neo4j as graph nodes and relationships

### `interface.py`
- **BFS (Breadth-First Search)** — Finds shortest path between two taxi locations
- **PageRank** — Identifies most and least important locations by trip volume/fare

### Kubernetes Configs
- `kafka-setup.yaml` — Kafka broker deployment and service
- `zookeeper-setup.yaml` — Zookeeper deployment and service
- `kafka-neo4j-connector.yaml` — Kafka Connect with Neo4j sink connector
- `neo4j-values.yaml` — Neo4j Helm chart configuration with GDS plugin

## 🔍 Graph Analytics

### BFS — Shortest Path
Finds the shortest route between two Bronx taxi locations using Breadth-First Search on the trip graph.

### PageRank — Location Importance
Ranks taxi locations by importance based on trip connections and fare weights — identifies the busiest and least active pickup/dropoff zones.

## 🚀 How to Run

### Prerequisites
- Kubernetes cluster (minikube or cloud)
- Helm installed
- Docker installed

### Setup
```bash
# Deploy Zookeeper
kubectl apply -f zookeeper-setup.yaml

# Deploy Kafka
kubectl apply -f kafka-setup.yaml

# Deploy Kafka-Neo4j Connector
kubectl apply -f kafka-neo4j-connector.yaml

# Deploy Neo4j via Helm
helm install neo4j -f neo4j-values.yaml neo4j/neo4j
```

### Load Data
```bash
python data_loader.py
```

## 💡 Key Features
- Fully containerized and orchestrated with Kubernetes
- Real-time event streaming with Kafka
- Graph-based analytics on taxi trip network
- BFS pathfinding between Bronx locations
- PageRank scoring to identify high-traffic zones
