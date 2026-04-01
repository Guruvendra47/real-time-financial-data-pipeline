# **Kubernetes Setup — Real-Time Financial Data Pipeline**

This document outlines the **production-style Kubernetes architecture** I used to deploy and orchestrate a **real-time financial data pipeline**.

---

# **Architecture Overview**

```text id="d8d3zw"
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

```text id="m5km74"
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

I downloaded and installed **Docker** from: [https://www.docker.com/](https://www.docker.com/)

Verify:

```bash id="1cfq4f"
docker --version
```

---

## **Install Minikube**

```bash id="0yxj2j"
choco install minikube
```

Verify:

```bash id="k4s6pk"
minikube version
```

---

## **Install kubectl**

```bash id="fbnzjb"
choco install kubernetes-cli
```

Verify:

```bash id="8m35yn"
kubectl version --client
```

---

## **Install Helm**

```bash id="4kws03"
choco install kubernetes-helm
```

Verify:

```bash id="8az2zl"
helm version
```

---

### **Why I used these tools**

* **Docker** to build container images
* **Minikube** to run a local Kubernetes cluster
* **kubectl** to interact with Kubernetes
* **Helm** to install complex applications like **Airflow, Kafka, and monitoring stacks**

---

# **STEP 1 — Start Kubernetes Cluster**

```bash id="32cdng"
minikube start --driver=docker --memory=8192 --cpus=4
kubectl get nodes
```

### **What I did**

I started a **local Kubernetes cluster**.

### **Why I did it**

To simulate a **real cloud environment** such as AWS EKS.

---

# **STEP 2 — Create Namespaces**

```bash id="m7huc2"
kubectl create namespace rtf-data-pipeline
kubectl create namespace airflow
kubectl create namespace kafka
kubectl create namespace monitoring
```

### **What I did**

I created **isolated environments** for each system.

### **Why I did it**

To improve **scalability, organization, and security**.

---

# **STEP 3 — Deploy Application Layer**

### **Apply Configuration**

```bash id="vcv90u"
kubectl apply -f configmap.yaml -n rtf-data-pipeline
kubectl apply -f secret.yaml -n rtf-data-pipeline
```

### **What I did**

I loaded **configuration and secrets**.

### **Why I did it**

To separate **configuration from application code**.

---

### **Deploy Application**

```bash id="t37mqb"
kubectl apply -f deployment.yaml -n rtf-data-pipeline
```

### **What I did**

I created **application pods**.

### **Why I did it**

To ensure **automatic recovery, scaling, and high availability**.

---

### **Expose Application**

```bash id="hzyxlk"
kubectl apply -f service.yaml -n rtf-data-pipeline
minikube service rtf-service -n rtf-data-pipeline
```

### **What I did**

I exposed the **application**.

### **Why I did it**

To provide a **stable endpoint** since Pods have dynamic IPs.

---

# **STEP 4 — Deploy Airflow (Orchestration Layer)**

```bash id="u7zdsv"
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm install airflow apache-airflow/airflow -n airflow --create-namespace -f airflow-values.yaml
```

* Here **-n** means namespace and **-f** means file; full names can also be used instead of shorthand.

---

### **Verify**

```bash id="xyjn18"
kubectl get pods -n airflow
```

---

### **Access UI**

```bash id="7zxte3"
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```

Open: [http://localhost:8080](http://localhost:8080)

---

### **What I did**

I deployed **Airflow**.

### **Why I did it**

I used Airflow to **orchestrate pipelines, schedule tasks, and trigger Spark and dbt jobs**.

---

## **DAG Synchronization (GitSync)**

### **What I did**

I configured **GitSync** to automatically pull DAG files from my GitHub repository into Airflow.

### **Where I configured it**

Inside **airflow-values.yaml**.

### **How I configured it**

```yaml id="p0p6q3"
dags:
  gitSync:
    enabled: true
    repo: "https://github.com/Guruvendra47/real-time-financial-data-pipeline.git"
    branch: "main"
    subPath: "kubernetes/dags"
    wait: 60
    recommendedProbeSetting: true
```

### **When I use it**

I use this when I want **automatic DAG updates, version control for pipelines, and no manual file copying**.

### **Why I used it**

To ensure my **Airflow DAGs stay synced** with my GitHub repository in real time.

---

# **STEP 5 — Deploy Kafka (Streaming Layer)**

```bash id="jknb8j"
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install kafka bitnami/kafka -n kafka
```

---

### **Verify**

```bash id="t3cr18"
kubectl get pods -n kafka
kubectl get svc -n kafka
```

---

### **Kafka Access (inside cluster)**

```text id="gl85ka"
kafka.kafka.svc.cluster.local:9092
```

---

### **What I did**

I deployed **Kafka**.

### **Why I did it**

I used Kafka to enable **real-time streaming between systems**.

---

# **STEP 6 — Spark Execution Model**

### **What I did**

I used **Apache Spark** to process streaming data.

### **How I implemented it**

* I did not deploy Spark as a **permanent service**
* I ran it as **temporary Kubernetes pods**
* I triggered it using **Airflow**

---

### **Build Spark Image**

```bash id="t0txe7"
docker build -t spark-job:1.0 .
minikube image load spark-job:1.0
```

---

### **Why I did it**

* **scalable distributed processing**
* **efficient resource usage**
* **runs only when needed**

---

# **STEP 7 — dbt Execution**

### **What I did**

I used **dbt** to transform data inside **Snowflake**.

### **How I implemented it**

* packaged as a **container**
* triggered by **Airflow**
* runs as a **Kubernetes pod**

### **Why I did it**

To ensure **modular and repeatable transformations**.

---

# **STEP 8 — Monitoring Setup**

```bash id="9s7k3q"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace
```

---

### **Access Grafana**

```bash id="sv9n4l"
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

---

### **What I did**

I deployed **monitoring tools**.

### **Why I did it**

To **monitor system health, track performance, and detect failures**.

---

# **STEP 9 — Run the Pipeline**

Inside **Airflow UI**:

1. I enable the **DAG**
2. I trigger the **run**
3. I monitor **execution**

---

### **Execution Flow**

```text id="rsc22l"
Airflow → Spark pod → S3 → dbt → analytics output
```

---

# **Cleanup**

```bash id="y3pqlm"
helm uninstall airflow -n airflow
helm uninstall kafka -n kafka
kubectl delete namespace airflow kafka monitoring rtf-data-pipeline
minikube delete
```

---

# **Key Takeaways**

* I used **Kubernetes** to separate systems into independent layers
* I used **Airflow** to orchestrate workflows
* I ran **Spark and dbt on demand**
* I used **Kafka for streaming**
* I implemented **monitoring to ensure reliability**

---

# **Author**

**Guruvendra Singh**
