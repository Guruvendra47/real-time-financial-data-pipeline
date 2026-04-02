This is **very well done** — I only made **minimal adjustments** to properly merge your first section (quick setup version) into your main README **without breaking flow**, and ensured:

* No duplication
* GitSync stays ✅
* Kafka (Strimzi) stays correct ✅
* Step-by-step remains clean
* “What / Why / How” preserved
* Your **simple quick-start + detailed production guide** both exist

---

# ✅ 🔥 **FINAL MERGED README (CLEAN + PROFESSIONAL + COMPLETE)**

---

# 🚀 **Real-Time Financial Data Pipeline (Kubernetes + Kafka + Spark + Airflow + S3 + dbt)**

---

## 📌 **Project Overview**

I built this project as a **production-style real-time data pipeline** using Kubernetes and modern data engineering tools.

* Kafka for streaming ingestion
* Spark Structured Streaming for processing
* AWS S3 for data lake storage
* Airflow for orchestration
* dbt for transformation
* Kubernetes for deployment and scaling

---

## 🏗️ **Architecture**

```text
Producer → Kafka → Spark → S3 (Bronze → Silver → Gold) → dbt → Analytics
```

---

## ⚙️ **Tech Stack**

* Kubernetes (Minikube)
* Apache Kafka (Strimzi)
* Apache Spark
* Apache Airflow
* AWS S3
* dbt (Snowflake optional)
* Docker

---

# 🧩 **QUICK START (HIGH LEVEL SETUP)**

> This section is for quickly running the project.
> Detailed production steps are provided below.

---

## 1️⃣ Start Kubernetes

```bash
minikube start
```

---

## 2️⃣ Create Namespace

```bash
kubectl create namespace rtf-data-pipeline
```

---

## 3️⃣ Deploy Kafka (Strimzi)

```bash
kubectl create namespace kafka
kubectl apply -f kafka-nodepool.yaml -n kafka
kubectl apply -f kafka-cluster.yaml -n kafka
kubectl apply -f rtf-kafka.yaml -n kafka
```

---

## 4️⃣ Create Kafka Topic

```bash
kubectl get kafkatopics -n kafka
```

Ensure:

```text
trades
```

---

## 5️⃣ Build & Load Images

```bash
docker build -t spark-job:latest ./spark
docker build -t kafka-producer:latest ./producer

minikube image load spark-job:latest
minikube image load kafka-producer:latest
```

---

## 6️⃣ Deploy Producer

```bash
kubectl apply -f producer-deployment.yaml
```

---

## 7️⃣ Run Airflow

```bash
docker-compose up -d
```

---

## 8️⃣ Trigger DAG

DAG:

```text
k8s_data_pipeline
```

---

## 9️⃣ Verify Output

Check S3:

```text
raw/
processed/
curated/
```

---

# 🧠 **DETAILED PRODUCTION SETUP (STEP-BY-STEP)**

---

# **STEP 1 — Start Kubernetes Cluster**

```bash
minikube start --driver=docker --memory=8192 --cpus=4
kubectl get nodes
```

---

# **STEP 2 — Create Namespaces**

```bash
kubectl create namespace rtf-data-pipeline
kubectl create namespace airflow
kubectl create namespace kafka
kubectl create namespace monitoring
```

---

# **STEP 3 — Set Default Namespace (Optional but Pro Move)**

```bash
kubectl config set-context --current --namespace=rtf-data-pipeline
```

---

# **STEP 4 — Deploy Application Layer**

```bash
kubectl apply -f configmap.yaml -n rtf-data-pipeline
kubectl apply -f secret.yaml -n rtf-data-pipeline
kubectl apply -f deployment.yaml -n rtf-data-pipeline
kubectl apply -f service.yaml -n rtf-data-pipeline
```

---

# **STEP 5 — Deploy Airflow (Orchestration Layer)**

## **GitSync (IMPORTANT)**

```yaml
dags:
  gitSync:
    enabled: true
    repo: "https://github.com/Guruvendra47/real-time-financial-data-pipeline.git"
    branch: "main"
    subPath: "kubernetes/dags"
    wait: 60
```

---

## **Deploy Airflow (Helm)**

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm install airflow apache-airflow/airflow -n airflow --create-namespace -f airflow-values.yaml
```

---

## **Access UI**

```bash
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```

---

# **STEP 6 — Deploy Kafka (Strimzi)**

---

## Install Operator

```bash
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
```

---

## Create Cluster

```bash
kubectl apply -f kafka-cluster.yaml
```

---

## Kafka Broker (IMPORTANT)

```text
rtf-kafka-kafka-bootstrap.kafka:9092
```

---

## Create Topic

```bash
kubectl apply -f kafka-topic.yaml
```

---

## Deploy Producer (CRITICAL FIX)

```yaml
env:
- name: KAFKA_BROKER
  value: "rtf-kafka-kafka-bootstrap.kafka:9092"
```

---

## Verify Kafka Data

```bash
kafka-console-consumer.sh \
--bootstrap-server rtf-kafka-kafka-bootstrap.kafka:9092 \
--topic trades --from-beginning
```

---

# **STEP 7 — Spark Execution**

### Kafka Fix

```python
"KAFKA_BROKER": "rtf-kafka-kafka-bootstrap.kafka:9092"
```

---

### Required JARs

```text
spark-sql-kafka
kafka-clients
hadoop-aws
aws-java-sdk
```

---

### Build

```bash
docker build -t spark-job:1.0 .
minikube image load spark-job:1.0
```

---

# **STEP 8 — dbt**

```bash
dbt run
```

---

# **STEP 9 — Monitoring**

```bash
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
```

---

# **STEP 10 — Run Pipeline**

1. Enable DAG
2. Trigger run
3. Monitor

---

# **STEP 10.1 — Validate Output**

```bash
aws s3 ls s3://real-time-financial-data-pipeline/raw/trades/
```

---

# 🧠 **Important Concepts**

### Kafka Broker

```text
rtf-kafka-kafka-bootstrap.kafka:9092
```

---

### Streaming Checkpoint

```text
s3://bucket/checkpoints/
```

---

# 🚨 **Common Errors & Fixes**

| Issue            | Fix                 |
| ---------------- | ------------------- |
| Empty parquet    | Producer missing    |
| Kafka connection | Wrong service name  |
| Spark error      | Missing JARs        |
| AWS error        | Missing credentials |

---

# 🚀 **Future Improvements**

* CI/CD (GitHub Actions)
* Monitoring dashboards
* Data quality checks
* Delta Lake

---

# 👨‍💻 **Author**

**Guruvendra Singh**

---

# ⭐ **Support**

If you like this project, give it a ⭐ on GitHub!

---

If you want, next I can:

👉 Add **architecture diagram (visual)**
👉 Add **resume bullet points (very strong for DE roles)**
👉 Add **interview explanation (story format)**
