# ---------------------------------------------------------------
# airflow 2.10.0, CHATGPT 답변 검증안됨.
# k8sexcutor에서 connection와 plugins 사용 샘플
# ---------------------------------------------------------------


# dags/k8s_exec_with_plugin.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from hello_operator import HelloOperator             # ⇦ ① 플러그인 import
from kubernetes.client import models as k8s          # ② pod_override 에 사용

# ─────────────────────────────────────────────────────────────
# 공통 executor_config 템플릿
# ─────────────────────────────────────────────────────────────
BASE_K8S_CONF = {
    "KubernetesExecutor": {
        "image": "python:3.9-slim",
        "request_memory": "256Mi",
        "limit_memory":   "512Mi",
        "request_cpu":    "100m",
        "limit_cpu":      "200m",
        "envs": {"PYTHONUNBUFFERED": "1"},
    }
}

def override_cpu(base, cpu):
    """CPU 제한만 덮어쓰는 헬퍼"""
    from copy import deepcopy
    conf = deepcopy(base)
    conf["KubernetesExecutor"]["limit_cpu"] = cpu
    return conf

# ─────────────────────────────────────────────────────────────
# DAG 정의
# ─────────────────────────────────────────────────────────────
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="k8s_exec_with_plugin",
    description="KubernetesExecutor + plugin operator + connection demo",
    start_date=datetime(2025, 6, 5),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
) as dag:

    # 1) 플러그인-기반 HelloOperator
    hello = HelloOperator(
        task_id="hello_plugin_task",
        conn_id="my_postgres",                    # Airflow UI 에 미리 등록
        executor_config=BASE_K8S_CONF,            # 기본 템플릿 그대로
    )

    # 2) 일반 PythonOperator (CPU 1 코어로 오버라이드)
    def just_print():
        import socket, os
        print("✅ PythonOperator inside K8s pod")
        print("host:", socket.gethostname())
        print("JOB_KIND:", os.getenv("JOB_KIND", "N/A"))

    python_task = PythonOperator(
        task_id="python_task",
        python_callable=just_print,
        executor_config=override_cpu(BASE_K8S_CONF, "1"),  # 일부만 덮어쓰기
    )

    # 의존 관계
    hello >> python_task
