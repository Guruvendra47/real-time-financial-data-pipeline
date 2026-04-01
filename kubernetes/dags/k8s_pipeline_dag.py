from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.cncf.kubernetes.secret import Secret
from datetime import datetime

# ==========================================
# DEFAULT ARGS
# ==========================================
default_args = {
    "owner": "guruvendra",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

# ==========================================
# KUBERNETES SECRETS (🔥 IMPORTANT)
# ==========================================
aws_access = Secret(
    deploy_type="env",
    deploy_target="AWS_ACCESS_KEY",
    secret="rtf-secret",
    key="AWS_ACCESS_KEY"
)

aws_secret = Secret(
    deploy_type="env",
    deploy_target="AWS_SECRET_KEY",
    secret="rtf-secret",
    key="AWS_SECRET_KEY"
)

# ==========================================
# DAG DEFINITION
# ==========================================
with DAG(
    dag_id="k8s_data_pipeline",
    default_args=default_args,
    schedule="@hourly",
    catchup=False,
) as dag:

    # ==========================================
    # SPARK JOB
    # ==========================================
    spark_job = KubernetesPodOperator(
        task_id="spark_job",
        name="spark-job",
        namespace="rtf-data-pipeline",
        image="spark-job:6.0",
        image_pull_policy="Never",

        cmds=["/opt/spark/bin/spark-submit"],
        arguments=["/opt/spark-app/spark-streaming-s3-aws.py"],

        # 🔥 THIS WAS MISSING
        secrets=[aws_access, aws_secret],

        # Optional env vars
        env_vars={
            "AWS_DEFAULT_REGION": "us-east-1",
            "S3_BUCKET": "real-time-financial-data-pipeline",
            "KAFKA_BROKER": "kafka:29092"
        },

        is_delete_operator_pod=True,
        get_logs=True,
    )

    # ==========================================
    # DBT JOB (LATER)
    # ==========================================
    dbt_run = KubernetesPodOperator(
        task_id="dbt_run",
        name="dbt-job",
        namespace="rtf-data-pipeline",
        image="your-dbt-image",
        cmds=["dbt", "run"],
        is_delete_operator_pod=True,
    )

    # ==========================================
    # PIPELINE FLOW
    # ==========================================
    spark_job >> dbt_run
