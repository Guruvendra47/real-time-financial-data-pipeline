# 🚀 Kubernetes Setup – Real-Time Financial Data Pipeline

This folder contains the complete Kubernetes setup for deploying and managing a **real-time financial data pipeline** using:

* Apache Airflow (Orchestration)
* Kubernetes (Container orchestration)
* Prometheus + Grafana (Monitoring)
* ConfigMap & Secrets (Configuration management)

---

# 🧠 Architecture Overview

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

# ⚙️ Prerequisites

* Docker installed
* Minikube installed
* kubectl installed
* Helm installed

---

# 🚀 1. Start Minikube

Start Kubernetes cluster locally:

```bash
minikube start --driver=docker --memory=6144 --cpus=3
```

---

# 🧱 2. Create Namespace

Namespace ensures isolation and organization.

```bash
kubectl create namespace rtf-data-pipline
kubectl get namespaces
```

---

# 📦 3. Deployment (Production Way)

Deployment manages Pods automatically.

```bash
kubectl apply -f deployment.yaml
kubectl get deployments -n rtf-data-pipline
kubectl get pods -n rtf-data-pipline
```

### Scaling

```bash
kubectl scale deployment rtf-deployment --replicas=3 -n rtf-data-pipline
```

---

# 🌐 4. Service (Expose Application)

```bash
kubectl apply -f service.yaml
kubectl get services -n rtf-data-pipline
minikube service rtf-service -n rtf-data-pipline
```

---

# 🔐 5. ConfigMap & Secret

## ConfigMap (Non-sensitive)

```bash
kubectl apply -f configmap.yaml
kubectl get configmap -n rtf-data-pipline
```

## Secret (Sensitive Data)

Encode values:

```bash
echo -n "password" | base64
```

Apply:

```bash
kubectl apply -f secret.yaml
kubectl get secrets -n rtf-data-pipline
```

---

# 🔗 6. Connect Config to Deployment

```yaml
envFrom:
  - configMapRef:
      name: rtf-config
  - secretRef:
      name: rtf-secret
```

Verify:

```bash
kubectl exec -it <pod-name> -n rtf-data-pipline -- printenv
```

---

# 🎯 7. Airflow Deployment (Helm)

## Add Airflow Repo

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update
```

---

## Install Airflow

```bash
helm install airflow apache-airflow/airflow \
  --namespace airflow \
  --create-namespace \
  -f airflow-values.yaml
```

---

## Verify Pods

```bash
kubectl get pods -n airflow
```

---

## Access Airflow UI

```bash
kubectl port-forward svc/airflow-api-server 8080:8080 -n airflow
```

Login:

* Username: `admin`
* Password: `admin`

---

# 🔄 8. DAG Deployment via GitSync

Airflow pulls DAGs from GitHub automatically.

```yaml
dags:
  gitSync:
    enabled: true
    repo: https://github.com/Guruvendra47/real-time-financial-data-pipeline.git
    branch: main
    subPath: kubernetes/dags
    wait: 60
```

---

# 📊 9. Monitoring (Prometheus + Grafana)

## Install Monitoring Stack

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

---

## Access Grafana

```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

URL:

```
http://localhost:3000
```

---

## Get Grafana Password

```bash
kubectl -n monitoring get secret monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d
```

---

## Verify Prometheus

```bash
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring
```

Query:

```
up
```

---

# 🧪 10. Run Airflow DAG

* Enable DAG in UI
* Click **Trigger DAG**
* Monitor execution in Graph View

---

# 🧹 Cleanup Commands

## Reset Airflow

```bash
helm uninstall airflow -n airflow
kubectl delete namespace airflow
```

---

## Full Reset

```bash
minikube delete
```

---

# 🔥 Key Learnings

* Kubernetes manages containers efficiently
* Airflow orchestrates data pipelines
* ConfigMap & Secret separate config from code
* Helm simplifies complex deployments
* Prometheus + Grafana provide observability

---

# 🎯 Real-World Skills Demonstrated

* Container orchestration (Kubernetes)
* Workflow orchestration (Airflow)
* Infrastructure monitoring (Prometheus + Grafana)
* Secure configuration management
* End-to-end data pipeline design

---

# 🚀 Author

**Guruvendra Singh**

---
