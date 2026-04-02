Got it — now I’ll **fully merge everything cleanly here**, keep your original structure, **retain GitSync**, and only **add missing + corrected steps** in the right places.

---

# **Kubernetes Setup — Real-Time Financial Data Pipeline**

This document outlines the **production-style Kubernetes architecture** I used to deploy and orchestrate a **real-time financial data pipeline**.

---

# **Architecture Overview**

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

# **Production Design Principles**

* I designed the system to be **decoupled**, where each component runs independently
* I used **namespace isolation** for better organization and security
* I implemented **on-demand processing**, where Spark and dbt run as jobs
* I centralized orchestration using **Airflow**
* I followed an **observability-first approach** by including monitoring

---

# **Namespace Strategy**

```text
rtf-data-pipeline  → Application layer  
airflow            → Orchestration layer  
kafka              → Streaming layer  
monitoring         → Observability layer  
```

---

# **Prerequisites & Tool Installation**

Before starting, I installed the **required tools**.

---

## **Install Docker**

I downloaded and installed Docker from: [https://www.docker.com/](https://www.docker.com/)

```bash
docker --version
```

---

## **Install Minikube**

```bash
choco install minikube
minikube version
```

---

## **Install kubectl**

```bash
choco install kubernetes-cli
kubectl version --client
```

---

## **Install Helm**

```bash
choco install kubernetes-helm
helm version
```

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

**Why**

I used this to avoid writing `-n rtf-data-pipeline` repeatedly.

---

# **STEP 4 — Deploy Application Layer**

```bash
kubectl apply -f configmap.yaml -n rtf-data-pipeline
kubectl apply -f secret.yaml -n rtf-data-pipeline
kubectl apply -f deployment.yaml -n rtf-data-pipeline
kubectl apply -f service.yaml -n rtf-data-pipeline
minikube service rtf-service -n rtf-data-pipeline
```

---

# **STEP 5 — Deploy Airflow (Orchestration Layer)**

## **First — Configure DAG Sync (GitSync)**

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

## **Deploy Airflow**

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

# **STEP 6 — Deploy Kafka (Streaming Layer)**

⚠️ I initially used Bitnami, but I switched to **Strimzi** for stability.

---

## **STEP 6.0 — Install Strimzi Operator**

```bash
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
```

---

## **STEP 6.1 — Create Kafka Cluster**

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: rtf-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
```

```bash
kubectl apply -f kafka-cluster.yaml
```

---

## **STEP 6.2 — Kafka Service (IMPORTANT FIX)**

```text
rtf-kafka-kafka-bootstrap.kafka:9092
```

---

## **STEP 6.3 — Create Kafka Topic**

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: trades
  namespace: kafka
  labels:
    strimzi.io/cluster: rtf-kafka
spec:
  partitions: 1
  replicas: 1
```

```bash
kubectl apply -f kafka-topic.yaml
```

---

## **STEP 6.4 — Deploy Kafka Producer**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-producer
  namespace: rtf-data-pipeline
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: producer
        image: your-producer-image:1.0
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: rtf-kafka-kafka-bootstrap.kafka:9092
        - name: KAFKA_TOPIC
          value: trades
```

```bash
kubectl apply -f producer.yaml
```

---

## **STEP 6.5 — Verify Kafka Data**

```bash
kubectl run kafka-test -n kafka --rm -it --image=bitnami/kafka -- bash
```

```bash
kafka-console-consumer.sh \
--bootstrap-server rtf-kafka-kafka-bootstrap.kafka:9092 \
--topic trades --from-beginning
```

---

# **STEP 7 — Spark Execution Model**

## **Fix Kafka Connection**

```python
"KAFKA_BROKER": "rtf-kafka-kafka-bootstrap.kafka:9092"
```

---

## **Required Dependencies**

```text
spark-sql-kafka
kafka-clients
hadoop-aws
aws-java-sdk
```

---

## **Build Image**

```bash
docker build -t spark-job:1.0 .
minikube image load spark-job:1.0
```

---

# **STEP 8 — dbt Execution**

Runs as Kubernetes job triggered by Airflow.

---

# **STEP 9 — Monitoring Setup**

```bash
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
```

---

# **STEP 10 — Run Pipeline**

1. Enable DAG
2. Trigger run
3. Monitor

---

# **STEP 10.1 — Validate Output (NEW)**

```bash
aws s3 ls s3://real-time-financial-data-pipeline/raw/trades/
```

```python
import pandas as pd
print(pd.read_parquet("file.parquet").head())
```

---

# **FINAL FLOW**

```text
Finnhub → Producer → Kafka → Spark → S3 → dbt → Power BI
```

---

# **KEY TAKEAWAYS**

* I used Kubernetes for orchestration
* I used Airflow for scheduling
* I used Strimzi for stable Kafka
* I ensured data flow using producer validation
* I verified output in S3

---

If you want next level:

👉 I can turn this into a **top 1% GitHub README (with diagram + badges + recruiter hooks)**
👉 Or prepare **perfect interview explanation (very important for data engineer roles)**
