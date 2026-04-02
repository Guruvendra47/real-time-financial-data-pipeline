I merged the new steps into your README and kept the GitSync section, the original flow, and the corrected Kafka producer fix. This is based on the README you uploaded earlier. 

# **Kubernetes Setup — Real-Time Financial Data Pipeline**

This document outlines the **production-style Kubernetes architecture** I used to deploy and orchestrate a **real-time financial data pipeline**.

---

# **Project Overview**

I built this project as a **production-style real-time data pipeline** using Kubernetes and modern data engineering tools.

* Kafka for streaming ingestion
* Spark Structured Streaming for processing
* AWS S3 for data lake storage
* Airflow for orchestration
* dbt for transformation
* Kubernetes for deployment and scaling

---

# **Architecture Overview**

```text
Producer → Kafka → Spark → S3 → Snowflake → dbt → Power BI
                     ↑
                  Airflow
                     ↑
               Kubernetes
                     ↑
        Prometheus → Grafana
```

---

# **Pipeline Flow**

```text
Finnhub Producer → Kafka → Spark → S3 (Bronze → Silver → Gold) → dbt → Analytics
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

### **What I did**

I started a local Kubernetes cluster.

### **Why I did it**

To simulate a real cloud environment such as AWS EKS.

```bash
minikube start --driver=docker --memory=8192 --cpus=4
kubectl get nodes
```

---

# **STEP 2 — Create Namespaces**

### **What I did**

I created isolated environments for each system.

### **Why I did it**

To improve scalability, organization, and security.

```bash
kubectl create namespace rtf-data-pipeline
kubectl create namespace airflow
kubectl create namespace kafka
kubectl create namespace monitoring
```

---

# **STEP 3 — Set Default Namespace (Optional but Pro Move)**

### **What I did**

I set the default namespace for my current kubectl context.

### **Why I did it**

So I do not need to write `-n rtf-data-pipeline` every time.

### **Where I used it**

Inside my local Kubernetes context.

```bash
kubectl config set-context --current --namespace=rtf-data-pipeline
```

---

# **STEP 4 — Deploy Application Layer**

### **Apply Configuration**

### **What I did**

I loaded configuration and secrets.

### **Why I did it**

To separate configuration from application code.

```bash
kubectl apply -f configmap.yaml -n rtf-data-pipeline
kubectl apply -f secret.yaml -n rtf-data-pipeline
```

---

### **Deploy Application**

### **What I did**

I created application pods.

### **Why I did it**

To ensure automatic recovery, scaling, and high availability.

```bash
kubectl apply -f deployment.yaml -n rtf-data-pipeline
```

---

### **Expose Application**

### **What I did**

I exposed the application.

### **Why I did it**

To provide a stable endpoint since Pods have dynamic IPs.

```bash
kubectl apply -f service.yaml -n rtf-data-pipeline
minikube service rtf-service -n rtf-data-pipeline
```

---

# **STEP 5 — Deploy Airflow (Orchestration Layer)**

## **First — Configure DAG Sync (GitSync)**

### **What I did**

I configured GitSync to automatically pull DAG files from my GitHub repository into Airflow.

### **Why I did it**

To keep my DAGs in sync with GitHub and avoid manual file copying.

### **Where I configured it**

Inside `airflow-values.yaml`.

### **How I configured it**

```yaml
dags:
  gitSync:
    enabled: true
    repo: "https://github.com/Guruvendra47/real-time-financial-data-pipeline.git"
    branch: "main"
    subPath: "kubernetes/dags"
    wait: 60
    recommendedProbeSetting: true
```

---

## **Deploy Airflow**

### **What I did**

I deployed Airflow on Kubernetes using Helm.

### **Why I did it**

I used Airflow to orchestrate pipelines, schedule tasks, and trigger Spark and dbt jobs.

### **Where I deployed it**

Inside the `airflow` namespace.

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm install airflow apache-airflow/airflow -n airflow --create-namespace -f airflow-values.yaml
```

---

### **Verify**

```bash
kubectl get pods -n airflow
```

---

### **Access UI**

### **What I did**

I forwarded the Airflow web service to my local machine.

### **Why I did it**

To access the Airflow UI in the browser.

```bash
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```

Open: [http://localhost:8080](http://localhost:8080)

---

# **STEP 6 — Deploy Kafka (Streaming Layer)**

⚠️ I initially used Bitnami, but I switched to **Strimzi** for stability.

---

## **STEP 6.0 — Install Strimzi Operator**

### **What I did**

I installed the Strimzi Kafka Operator.

### **Why I did it**

It manages Kafka and Zookeeper as Kubernetes-native resources and is more stable for this setup.

### **Where I installed it**

Inside the `kafka` namespace.

```bash
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
```

---

### **Verify Operator**

```bash
kubectl get pods -n kafka
```

Expected:

```text
strimzi-cluster-operator-xxxxx   Running
```

---

## **STEP 6.1 — Create Kafka Cluster**

### **What I did**

I created a Kafka cluster using Strimzi.

### **Why I did it**

To run Kafka in a Kubernetes-native way with minimal local resources.

### **Where I defined it**

In `kafka-cluster.yaml`.

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
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
    storage:
      type: ephemeral

  zookeeper:
    replicas: 1
    storage:
      type: ephemeral

  entityOperator:
    topicOperator: {}
    userOperator: {}
```

```bash
kubectl apply -f kafka-cluster.yaml
```

---

### **Verify Kafka Pods**

```bash
kubectl get pods -n kafka -w
```

Expected:

```text
rtf-kafka-zookeeper-0   Running
rtf-kafka-kafka-0       Running
```

---

## **STEP 6.2 — Kafka Service (IMPORTANT FIX)**

### **What I did**

I used the Kubernetes service DNS for Kafka.

### **Why I did it**

Kubernetes resolves services using:

```text
<service-name>.<namespace>:<port>
```

### **Correct Broker Endpoint**

```text
rtf-kafka-kafka-bootstrap.kafka:9092
```

---

## **STEP 6.3 — Create Kafka Topic**

### **What I did**

I created the `trades` topic before running Spark.

### **Why I did it**

If Kafka has no topic or no data, Spark can still run but produce empty output.

### **Where I defined it**

In `kafka-topic.yaml`.

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

### **Verify Topic**

```bash
kubectl get kafkatopics -n kafka
```

Expected:

```text
trades   True
```

---

## **STEP 6.4 — Deploy Kafka Producer**

### **What I did**

I deployed a Kafka producer inside Kubernetes.

### **Why I did it**

Without a producer:

* Kafka remains empty
* Spark writes empty parquet
* The pipeline does not produce useful output

### **Where I defined it**

In `producer.yaml`.

### **Important Environment Variable Fix**

My producer code expects:

```python
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
```

So I updated the Kubernetes YAML to match the code.

### **How I configured it**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-producer
  namespace: rtf-data-pipeline
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka-producer
  template:
    metadata:
      labels:
        app: kafka-producer
    spec:
      containers:
      - name: kafka-producer
        image: kafka-producer:1.0
        imagePullPolicy: Never
        env:
        - name: KAFKA_BROKER
          value: "rtf-kafka-kafka-bootstrap.kafka:9092"
        - name: KAFKA_TOPIC
          value: "trades"
        - name: FINNHUB_API_KEY
          valueFrom:
            secretKeyRef:
              name: rtf-secret
              key: FINNHUB_API_KEY
        - name: SYMBOLS
          value: "AAPL,TSLA,MSFT,BINANCE:BTCUSDT"
```

```bash
kubectl apply -f producer.yaml
kubectl delete pod -l app=kafka-producer -n rtf-data-pipeline
```

---

### **Verify Producer**

```bash
kubectl logs -l app=kafka-producer -n rtf-data-pipeline -f
```

Expected:

```text
Connected to Kafka broker
Sending: {...}
Sending: {...}
```

---

## **STEP 6.5 — Verify Kafka Data**

### **What I did**

I verified that Kafka is actually receiving messages.

### **Why I did it**

This confirms the producer is working before I run Spark.

### **How I checked it**

```bash
kubectl run kafka-test -n kafka --rm -it --image=bitnami/kafka -- bash
```

Then:

```bash
kafka-console-consumer.sh \
--bootstrap-server rtf-kafka-kafka-bootstrap.kafka:9092 \
--topic trades --from-beginning
```

Expected:

```json
{"p": 210, "s": "AAPL", "t": 123, "v": 5}
```

---

# **STEP 7 — Spark Execution Model**

### **What I did**

I used Apache Spark to process streaming data.

### **Why I did it**

To read messages from Kafka, transform them, and write the output to S3.

### **How I implemented it**

* I did not deploy Spark as a permanent service
* I ran it as temporary Kubernetes pods
* I triggered it using Airflow

---

## **Kafka Connection Fix**

### **What I did**

I updated Spark to use the correct Kafka broker endpoint.

### **Why I did it**

The Spark pod cannot resolve `kafka:29092`; it must use the Kubernetes service DNS.

```python
"KAFKA_BROKER": "rtf-kafka-kafka-bootstrap.kafka:9092"
```

---

## **Spark Dependency Fix**

### **What I did**

I included the required Spark and AWS dependencies in my Spark image.

### **Why I did it**

Without these, Kafka reads and S3 writes can fail.

```text
spark-sql-kafka
kafka-clients
hadoop-aws
aws-java-sdk
```

---

### **Build Spark Image**

```bash
docker build -t spark-job:1.0 .
minikube image load spark-job:1.0
```

---

# **STEP 8 — dbt Execution**

### **What I did**

I used dbt to transform the data after Spark wrote it to S3.

### **Why I did it**

To keep transformations modular, repeatable, and easy to maintain.

### **How I ran it**

* packaged as a container
* triggered by Airflow
* runs as a Kubernetes pod or as a dbt job

```bash
dbt run
```

---

# **STEP 9 — Monitoring Setup**

### **What I did**

I deployed monitoring tools for cluster observability.

### **Why I did it**

To monitor system health, track performance, and detect failures.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace
```

---

### **Access Grafana**

```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

---

# **STEP 10 — Run the Pipeline**

Inside **Airflow UI**:

1. I enable the DAG
2. I trigger the run
3. I monitor execution

---

### **DAG Name**

```text
k8s_data_pipeline
```

---

### **Execution Flow**

```text
Producer → Kafka → Spark → S3 → dbt → Analytics
```

---

# **STEP 10.1 — Validate Output**

### **What I did**

I checked the final output in S3 and verified the processed file content.

### **Why I did it**

To confirm the pipeline produced data end to end.

### **How I checked it**

```bash
aws s3 ls s3://real-time-financial-data-pipeline/raw/trades/
```

```python
import pandas as pd

df = pd.read_parquet("file.parquet")
print(df.head())
```

### **If data is empty**

I checked:

* the producer is running
* Kafka has data
* Spark is connected correctly
* the broker name matches the code

---

# **Important Concepts**

---

## **Streaming Checkpoint**

### **What I did**

I stored streaming checkpoints in S3 instead of local disk.

### **Why I did it**

Local paths like `/tmp/checkpoint` are not reliable for production-style pipelines.

```text
s3://bucket/checkpoints/
```

---

## **Common Errors & Fixes**

### **Kafka not found**

Usually caused by missing Spark Kafka JARs.

### **AWS error**

Usually caused by missing credentials.

### **Checkpoint error**

Use S3 instead of `/tmp`.

### **Producer crash at startup**

Usually caused by a mismatch between the code and environment variables.
I fixed that by using `KAFKA_BROKER` consistently.

---

# **Cleanup**

```bash
helm uninstall airflow -n airflow
helm uninstall kafka -n kafka
kubectl delete namespace airflow kafka monitoring rtf-data-pipeline
minikube delete
```

---

# **Key Takeaways**

* I used Kubernetes to separate systems into independent layers
* I used Airflow to orchestrate workflows
* I ran Spark and dbt on demand
* I used Kafka for streaming
* I implemented monitoring to ensure reliability
* I fixed the producer environment mismatch by aligning code and YAML
* I validated data flow end to end from producer to S3

---

# **Author**

**Guruvendra Singh**

---

# **Final Note**

This setup reflects a real-world production architecture where systems are modular, workloads are scalable, orchestration is centralized, and infrastructure is observable.
