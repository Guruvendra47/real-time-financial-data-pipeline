
# 🚀 Kubernetes Setup — Real-Time Financial Data Pipeline

This document outlines the **production-style Kubernetes architecture** used to deploy and orchestrate a real-time financial data pipeline.

---

# 🧭 Architecture Overview

```text id="h8v0g7"
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
* **Namespace isolation** → better organization and security
* **On-demand processing** → Spark and dbt run as jobs
* **Central orchestration** → Airflow controls execution
* **Observability-first** → monitoring included

---

# 🏗️ Namespace Strategy

```text id="r5dtqc"
rtf-data-pipeline  → Application layer  
airflow            → Orchestration layer  
kafka              → Streaming layer  
monitoring         → Observability layer  
```

---

# ⚙️ Prerequisites & Tool Installation

Before starting, install the required tools.

---

## 🔧 Install Docker

Download and install from: [https://www.docker.com/](https://www.docker.com/)

Verify:

```bash
docker --version
```

---

## 🔧 Install Minikube

```bash id="3vh6ux"
choco install minikube
```

Verify:

```bash id="zspc3o"
minikube version
```

---

## 🔧 Install kubectl

```bash id="v7rvwm"
choco install kubernetes-cli
```

Verify:

```bash id="tbo1sb"
kubectl version --client
```

---

## 🔧 Install Helm

```bash id="b2ybz2"
choco install kubernetes-helm
```

Verify:

```bash id="q3nh4t"
helm version
```

---

### Why these tools

* **Docker** → builds container images
* **Minikube** → local Kubernetes cluster
* **kubectl** → interacts with Kubernetes
* **Helm** → installs complex apps like Apache Airflow, Kafka, and monitoring stacks

---

# 🚀 STEP 1 — Start Kubernetes Cluster

```bash id="2v9n9n"
minikube start --driver=docker --memory=8192 --cpus=4
kubectl get nodes
```

### What

Starts a local Kubernetes cluster.

### Why

Simulates a real cloud environment (like AWS EKS).

---

# 🧱 STEP 2 — Create Namespaces

```bash id="sq3k6d"
kubectl create namespace rtf-data-pipeline
kubectl create namespace airflow
kubectl create namespace kafka
kubectl create namespace monitoring
```

### What

Creates isolated environments for each system.

### Why

Improves scalability, organization, and security.

---

# 📦 STEP 3 — Deploy Application Layer

### Apply Configuration

```bash id="r2lfr5"
kubectl apply -f configmap.yaml -n rtf-data-pipeline
kubectl apply -f secret.yaml -n rtf-data-pipeline
```

### What

Loads configuration and secrets.

### Why

Separates configuration from application code.

---

### Deploy Application

```bash id="m11z1u"
kubectl apply -f deployment.yaml -n rtf-data-pipeline
```

### What

Creates application pods.

### Why

Ensures:

* automatic recovery
* scaling
* high availability

---

### Expose Application

```bash id="j4q1i4"
kubectl apply -f service.yaml -n rtf-data-pipeline
minikube service rtf-service -n rtf-data-pipeline
```

### What

Exposes the application.

### Why

Provides a stable endpoint (Pods have dynamic IPs).

---

# 🎯 STEP 4 — Deploy Airflow (Orchestration Layer)

```bash id="jmm7vy"
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm install airflow apache-airflow/airflow -n airflow --create-namespace -f airflow-values.yaml
```
* Here *-n* means namespace and *-f* means file and you can mention full name also instead just -n or -f
---

### Verify

```bash id="yjv6s7"
kubectl get pods -n airflow
```

---

### Access UI

```bash id="kvf9le"
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```

Open: [http://localhost:8080](http://localhost:8080)

---

### What

Deploys Airflow.

### Why

Apache Airflow is used to:

* orchestrate pipelines
* schedule tasks
* trigger Spark and dbt jobs

---

## 🔁 DAG Synchronization (GitSync)

### What

GitSync automatically pulls DAG files from your GitHub repository into Airflow.

### Where

Configured inside `airflow-values.yaml`.

### How

```yaml
dags:
  gitSync:
    enabled: true
    repo: "https://github.com/Guruvendra47/real-time-financial-data-pipeline.git"
    branch: "main"
    subPath: "kubernetes/dags"   # change if needed
    wait: 60
    recommendedProbeSetting: true
```

### When to use

Used when you want:

* automatic DAG updates
* version control for pipelines
* no manual file copying

### Why

Ensures your Airflow DAGs stay synced with your GitHub repository in real time.

---

# 📡 STEP 5 — Deploy Kafka (Streaming Layer)

```bash id="ch7u79"
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install kafka bitnami/kafka -n kafka
```

---

### Verify

```bash id="wj8qmx"
kubectl get pods -n kafka
kubectl get svc -n kafka
```

---

### Kafka Access (inside cluster)

```text id="k1u5pk"
kafka.kafka.svc.cluster.local:9092
```

---

### What

Deploys Kafka.

### Why

Kafka enables real-time streaming between systems.

---

# ⚡ STEP 6 — Spark Execution Model

### What

Apache Spark processes streaming data.

### How

* Not deployed as a permanent service
* Runs as temporary Kubernetes pods
* Triggered by Airflow

---

### Build Spark Image

```bash id="8h7m0s"
docker build -t spark-job:1.0 .
minikube image load spark-job:1.0
```

---

### Why

* scalable distributed processing
* efficient resource usage
* runs only when needed

---

# 🔁 STEP 7 — dbt Execution

### What

Transforms data inside Snowflake.

### How

* packaged as container
* triggered by Airflow
* runs as Kubernetes pod

### Why

Ensures modular, repeatable transformations.

---

# 📊 STEP 8 — Monitoring Setup

```bash id="m2yjlwm"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace
```

---

### Access Grafana

```bash id="r1tbbh"
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

---

### What

Deploys monitoring tools.

### Why

* monitor system health
* track performance
* detect failures

---

# 🔄 STEP 9 — Run the Pipeline

Inside Airflow UI:

1. Enable DAG
2. Trigger run
3. Monitor execution

---

### Execution Flow

```text id="8n93mf"
Airflow → Spark pod → S3 → dbt → analytics output
```

---

# 🧹 Cleanup

```bash id="qk4d4y"
helm uninstall airflow -n airflow
helm uninstall kafka -n kafka
kubectl delete namespace airflow kafka monitoring rtf-data-pipeline
minikube delete
```

---

# 💯 Key Takeaways

* Kubernetes separates systems into independent layers
* Airflow orchestrates workflows
* Spark and dbt run on demand
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

If you want next, I can help you make:
👉 **Interview explanation (very easy to speak)**
👉 **Resume bullets (high impact)**
👉 **Architecture diagram (visual GitHub ready)** 🔥
