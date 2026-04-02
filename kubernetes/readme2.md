
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
