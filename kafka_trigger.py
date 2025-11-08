# ----------------------------------------------------------------------------------
# airflow 3.0, ChatGPT가 알려준 코드로 아직 검증되지 않음
# ----------------------------------------------------------------------------------

# dags/kafka_event_dag.py
import json
from airflow.providers.apache.kafka.triggers.await_message import AwaitMessageTrigger
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime

# ✅ 최상위 함수 ― import 경로가 생김
def contains_trigger_event(msg):
    data = json.loads(msg.value())
    return data.get("event_type") == "RUN_PIPELINE"

trigger = AwaitMessageTrigger(
    topics=["climbing.events"],
    kafka_config_id="kafka_default",
    # ① 문자열 경로 또는 ② 직접 callable 둘 다 OK
    apply_function="kafka_event_dag.contains_trigger_event",
    # apply_function=contains_trigger_event,  # 이렇게 놔도 내부에서 경로로 변환
)

with DAG(
    dag_id="process_climbing_event",
    schedule=[trigger],          # Asset-Watcher 대신 Trigger 직접 사용 예시
    start_date=datetime(2025, 6, 5),
    catchup=False,
):
    EmptyOperator(task_id="start")
