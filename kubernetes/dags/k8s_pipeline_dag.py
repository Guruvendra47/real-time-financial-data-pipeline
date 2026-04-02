from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.cncf.kubernetes.secret import Secret

# ✅ NEW IMPORTS (ADD THESE)
from airflow.providers.cncf.kubernetes.volume import Volume
from airflow.providers.cncf.kubernetes.volume_mount import VolumeMount

from datetime import datetime

default_args = {
    "owner": "guruvendra",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

# ==========================================
# ✅ K8s Secrets → Env Variables (UNCHANGED)
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
# ✅ NEW: VOLUME + MOUNT (ADD THIS BLOCK)
# ==========================================
volume_mount = VolumeMount(
    name="spark-checkpoint-volume",
    mount_path="/checkpoint",  
    sub_path=None,
    read_only=False
)

volume = Volume(
    name="spark-checkpoint-volume",
    configs={
        "persistentVolumeClaim": {
            "claimName": "spark-checkpoint-pvc"
        }
    }
)

with DAG(
    dag_id="k8s_data_pipeline",
    default_args=default_args,
    schedule="@hourly",
    catchup=False,
) as dag:

    # ==========================================
    # SPARK JOB (UPDATED ONLY WHERE NEEDED)
    # ==========================================
    spark_job = KubernetesPodOperator(
        task_id="spark_job",
        name="spark-job",
        namespace="rtf-data-pipeline",
        image="spark-job:15.0",
        image_pull_policy="Never",

        cmds=["/opt/spark/bin/spark-submit"],

        arguments=[
            "--jars",
            "/opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.1.jar,"
            "/opt/spark/jars/kafka-clients-3.5.1.jar,"
            "/opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.1.jar,"
            "/opt/spark/jars/commons-pool2-2.11.1.jar,"
            "/opt/spark/jars/hadoop-aws-3.3.4.jar,"
            "/opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar",

            "/opt/spark-app/spark-streaming-s3-aws.py"
        ],

        secrets=[aws_access, aws_secret],

        env_vars={
            "AWS_DEFAULT_REGION": "us-east-1",
            "S3_BUCKET": "real-time-financial-data-pipeline",
            "KAFKA_BROKER": "rtf-kafka-kafka-bootstrap.kafka:9092"
        },

        # ✅ NEW (VERY IMPORTANT)
        volumes=[volume],
        volume_mounts=[volume_mount],

        is_delete_operator_pod=True,
        get_logs=True,
    )

    # ==========================================
    # DBT JOB (UNCHANGED)
    # ==========================================
    dbt_run = KubernetesPodOperator(
        task_id="dbt_run",
        name="dbt-job",
        namespace="rtf-data-pipeline",
        image="your-dbt-image",
        cmds=["dbt", "run"],
        is_delete_operator_pod=True,
    )

    spark_job >> dbt_run
