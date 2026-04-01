
# 🚀 Kubernetes Setup — Real-Time Financial Data Pipeline

This document outlines the **production-style Kubernetes architecture** used to deploy and orchestrate a real-time financial data pipeline.

---

# 🧭 Architecture Overview

```text
Kafka → Spark → S3 → Snowflake → dbt → Power BI
                     ↑
                  Airflow
                     ↑
               Kubernetes
                     ↑
        Prometheus → Grafana
```

---

# 🧠 Production Design Principles

* **Decoupled systems** → each component runs independently
* **Namespace isolation** → better management and security
* **On-demand processing** → Spark and dbt run as jobs
* **Central orchestration** → Airflow controls execution
* **Observability-first** → monitoring integrated

---

# 🏗️ Namespace Strategy

```text
rtf-data-pipeline  → Application layer  
airflow            → Orchestration layer  
kafka              → Streaming layer  
monitoring         → Observability layer  
```

---

# ⚙️ Prerequisites

Install:

* Docker
* Minikube
* kubectl
* Helm

---

# 🚀 STEP 1 — Start Kubernetes Cluster

```bash
minikube start --driver=docker --memory=8192 --cpus=4
kubectl get nodes
```

### What

Starts a local Kubernetes cluster.

### Why

Simulates a real cloud environment (like EKS) for development and testing.

---

# 🧱 STEP 2 — Create Namespaces

```bash
kubectl create namespace rtf-data-pipeline
kubectl create namespace airflow
kubectl create namespace kafka
kubectl create namespace monitoring
```

### What

Creates isolated environments for each system.

### Why

Improves organization, scalability, and security.

---

# 📦 STEP 3 — Deploy Application Layer

### Apply Configuration

```bash
kubectl apply -f configmap.yaml -n rtf-data-pipeline
kubectl apply -f secret.yaml -n rtf-data-pipeline
```

### What

Loads configuration and sensitive data into Kubernetes.

### Why

Keeps application code clean and secure.

---

### Deploy Application

```bash
kubectl apply -f deployment.yaml -n rtf-data-pipeline
```

### What

Creates application pods.

### Why

Ensures:

* automatic restarts
* high availability
* scalability

---

### Expose Application

```bash
kubectl apply -f service.yaml -n rtf-data-pipeline
minikube service rtf-service -n rtf-data-pipeline
```

### What

Creates a stable endpoint for the application.

### Why

Pods have dynamic IPs, services provide consistent access.

---

# 🎯 STEP 4 — Deploy Airflow (Orchestration Layer)

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm install airflow apache-airflow/airflow \
  -n airflow \
  --create-namespace \
  -f airflow-values.yaml
```

### What

Deploys Airflow using Helm.

### Why

Apache Airflow is used to:

* orchestrate the pipeline
* schedule tasks
* trigger Spark and dbt jobs

---

### Verify Deployment

```bash
kubectl get pods -n airflow
```

---

### Access Airflow UI

```bash
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```

Open: [http://localhost:8080](http://localhost:8080)

---

# 📡 STEP 5 — Deploy Kafka (Streaming Layer)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install kafka bitnami/kafka -n kafka
```

### What

Deploys Kafka cluster.

### Why

Kafka enables real-time data ingestion and streaming.

---

### Verify Kafka

```bash
kubectl get pods -n kafka
kubectl get svc -n kafka
```

---

### Kafka Internal Access

```text
kafka.kafka.svc.cluster.local:9092
```

---

# ⚡ STEP 6 — Spark Execution Model (Important)

### What

Spark is used for data processing.

### How

* Not deployed as a permanent service
* Runs as temporary Kubernetes pods
* Triggered by Airflow

---

### Build Spark Image

```bash
docker build -t spark-job:1.0 .
minikube image load spark-job:1.0
```

---

### Why

Apache Spark:

* processes large-scale data
* runs only when needed
* improves efficiency and scalability

---

# 🔁 STEP 7 — dbt Execution

### What

Runs data transformation logic.

### How

* Packaged as a container
* Triggered by Airflow
* Executes as a Kubernetes pod

### Why

Ensures modular and repeatable data transformations.

---

# 📊 STEP 8 — Monitoring Setup

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace
```

---

### Access Grafana

```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

---

### What

Deploys monitoring tools.

### Why

* tracks system health
* monitors resource usage
* helps debugging and alerting

---

# 🔄 STEP 9 — Running the Pipeline

Inside Airflow UI:

1. Enable DAG
2. Trigger execution
3. Monitor tasks

---

### Execution Flow

```text
Airflow → creates Spark pod → processes data → stores in S3 → triggers dbt
```

---

# 🧹 Cleanup

```bash
helm uninstall airflow -n airflow
helm uninstall kafka -n kafka
kubectl delete namespace airflow kafka monitoring rtf-data-pipeline
minikube delete
```

---

# 💯 Key Takeaways

* Kubernetes separates systems into independent layers
* Airflow orchestrates workflows, not processing
* Spark and dbt run as on-demand jobs
* Kafka handles streaming
* Monitoring ensures reliability

---

# 👤 Author

**Guruvendra Singh**

---

# 🏁 Final Note

This setup reflects a **real-world production architecture**, where:

* systems are modular
* workloads are scalable
* orchestration is centralized
* infrastructure is observable

---

If you want next, I can help you convert this into:
👉 Resume bullets
👉 Architecture diagram
👉 Interview explanation (STAR format) 🔥
