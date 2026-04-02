
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
