from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from datetime import datetime

default_args = {
    "owner": "guruvendra",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="k8s_data_pipeline",
    default_args=default_args,
    schedule="@hourly",
    catchup=False,
) as dag:

    spark_job = KubernetesPodOperator(
        task_id="spark_job",
        name="spark-job",
        namespace="rtf-data-pipeline",
        image="spark-job:5.0",
        image_pull_policy="Never",
        cmds=["/opt/spark/bin/spark-submit"],
        arguments=["/opt/spark-app/spark-streaming-s3-aws.py"],
        is_delete_operator_pod=True,
        get_logs=True,
    )

    dbt_run = KubernetesPodOperator(
        task_id="dbt_run",
        name="dbt-job",
        namespace="rtf-data-pipeline",
        image="your-dbt-image",   # we will fix later
        cmds=["dbt", "run"],
        is_delete_operator_pod=True,
    )

    spark_job >> dbt_run
