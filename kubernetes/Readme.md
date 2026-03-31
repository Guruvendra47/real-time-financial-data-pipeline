# Kubernetes Setup — Real-Time Financial Data Pipeline

This section documents how I designed and deployed the Kubernetes layer for my **real-time financial data pipeline project**.

The goal of this setup was to build a **production-style environment** that supports orchestration, scalability, monitoring, and secure configuration management.

---

## Project Overview

The pipeline processes real-time financial data across multiple systems:

```text
Kafka → Spark → S3 → Snowflake → dbt → Power BI
                     ↑
                  Airflow
                     ↑
               Kubernetes
                     ↑
        Prometheus → Grafana
```

### Why I used Kubernetes

In this project, I used Kubernetes to:

* manage containerized applications efficiently,
* ensure high availability and automatic recovery,
* scale workloads when needed,
* separate configuration from application code,
* and simulate a real-world production environment.

---

## Kubernetes Resources Used

All files which i used in this project are stored inside the `kubernetes/` folder

### Files I created

* `deployment.yaml` → defines how my application runs (Pods, replicas)
* `service.yaml` → exposes the application inside the cluster
* `configmap.yaml` → stores non-sensitive configuration
* `secret.yaml` → stores sensitive credentials securely
* `airflow-values.yaml` → custom configuration for Airflow Helm deployment

This structure allowed me to maintain a clean separation between application logic and infrastructure.

---

## Environment Setup

To run this locally, I used the following tools:

* Docker
* Minikube
* kubectl
* Helm

### Why this setup

I used Minikube to simulate a real Kubernetes cluster locally, which helped me test deployments before moving to a cloud environment.

---

## Step 1 — Starting the Cluster

```bash
minikube start --driver=docker --memory=8144 --cpus=4
```

I configured higher memory and CPU to support Airflow and monitoring tools.

---

## Step 2 — Namespace Design

```bash
kubectl create namespace rtf-data-pipeline
```

I used a dedicated namespace to isolate all resources related to this pipeline and keep the environment organized.

---

## Step 3 — Application Deployment

```bash
kubectl apply -f deployment.yaml -n rtf-data-pipeline
```

The Deployment ensures:

* Pods are always running,
* failed containers are restarted automatically,
* and scaling can be handled easily.

### Scaling Example

```bash
kubectl scale deployment rtf-deployment --replicas=3 -n rtf-data-pipeline
```

This allowed me to simulate increased workload handling.

---

## Step 4 — Service Exposure

```bash
kubectl apply -f service.yaml -n rtf-data-pipeline
```

I used a Service to provide a stable endpoint for accessing the application, since Pod IPs are dynamic.

```bash
minikube service rtf-service -n rtf-data-pipeline
```

---

## Step 5 — Configuration Management

### ConfigMap

```bash
kubectl apply -f configmap.yaml -n rtf-data-pipeline
```

I used ConfigMap to store:

* Kafka configuration
* S3 details
* pipeline environment variables

### Secret

```bash
echo -n "password" | base64
kubectl apply -f secret.yaml -n rtf-data-pipeline
```

Secrets were used to securely store:

* Snowflake credentials
* API keys

This approach ensured no sensitive data was hardcoded in the application.

---

## Step 6 — Injecting Configuration into Pods

```yaml
envFrom:
  - configMapRef:
      name: rtf-config
  - secretRef:
      name: rtf-secret
```

This allowed my containers to dynamically read configuration at runtime.

---

## Step 7 — Airflow Deployment (Helm)

I used Helm to deploy Airflow because it simplifies managing multiple components.

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm install airflow apache-airflow/airflow \
  --namespace airflow \
  --create-namespace \
  -f airflow-values.yaml
```

This setup enabled orchestration of the entire pipeline.

---

## Step 8 — DAG Integration using GitSync

```yaml
dags:
  gitSync:
    enabled: true
    repo: https://github.com/Guruvendra47/real-time-financial-data-pipeline.git
    branch: main
    subPath: kubernetes/dags
```

I configured GitSync so Airflow automatically pulls DAGs from GitHub, ensuring continuous updates without manual intervention.

---

## Step 9 — Monitoring Setup

To monitor the system, I deployed Prometheus and Grafana using Helm.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### Why monitoring was important in this project

It allowed me to track:

* system health
* resource utilization
* service availability

---

## Step 10 — Accessing Tools

### Airflow

```bash
kubectl port-forward svc/airflow-api-server 8080:8080 -n airflow
```

### Grafana

```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

### Prometheus

```bash
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring
```

---

## Step 11 — Running the Pipeline

Inside Airflow:

* enabled the DAG
* triggered execution
* monitored tasks in Graph View

This validated the full orchestration flow of the pipeline.

---

## Cleanup

```bash
helm uninstall airflow -n airflow
kubectl delete namespace airflow
minikube delete
```

---

## Key Takeaways from This Project

Through this implementation, I gained hands-on experience in:

* Kubernetes deployment and scaling
* Airflow orchestration using Helm
* secure configuration management using ConfigMaps and Secrets
* monitoring with Prometheus and Grafana
* designing a production-style data pipeline environment

---

## Author

**Guruvendra Singh**

---

This setup reflects a real-world architecture approach where scalability, monitoring, and maintainability are key considerations.
