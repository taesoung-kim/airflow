다음 순서대로 만들고 쓴다. 불필요한 말은 없다.

1) 준비

Airflow 2.10.0 기준.

HTTP 커넥션 생성: Conn Id = rise_messenger

Conn Type = HTTP

Host = https://messenger.example.com

Extra 예:

{"headers": {"Authorization": "Bearer XXX"}, "timeout": 5}


또는 Airflow Variable에 RISE_MESSENGER_TOKEN 저장.


2) 커스텀 데코레이터 파일 생성

dags/_common/rise_messenger_task.py

from airflow.decorators import task
from airflow.hooks.base import BaseHook
from functools import wraps
import logging, json, requests

def messenger_task(
    conn_id: str = "rise_messenger",
    endpoint: str = "/api/v1/message",
    timeout: int | None = None,
):
    """
    메신저 전송 전용 데코레이터.
    원본 함수가 반환한 payload(dict|str)를 POST로 전송한다.
    """
    def decorator(func):
        @task(retries=2, retry_delay_seconds=30)  # 필요 시 조정
        @wraps(func)
        def wrapper(*args, **kwargs):
            payload = func(*args, **kwargs)
            if isinstance(payload, str):
                payload = {"text": payload}

            # Airflow Connection 로드
            conn = BaseHook.get_connection(conn_id)
            base = conn.host.rstrip("/")
            url = f"{base}{endpoint}"

            # 헤더 병합
            headers = {"Content-Type": "application/json"}
            if conn.extra_dejson.get("headers"):
                headers.update(conn.extra_dejson["headers"])

            # 타임아웃
            to = timeout or conn.extra_dejson.get("timeout", 5)

            try:
                resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=to)
                resp.raise_for_status()
                logging.info("[Messenger] %s %s OK", url, resp.status_code)
                return {"ok": True, "status": resp.status_code, "body": resp.text}
            except requests.HTTPError as e:
                logging.error("[Messenger] HTTPError %s: %s", url, e)
                raise
            except Exception as e:
                logging.error("[Messenger] Error %s: %s", url, e)
                raise
        return wrapper
    return decorator

3) 메시지 생성 Task

다른 Task에서 전송할 메시지를 만든다. XCom으로 전달된다.

from airflow.decorators import task

@task
def generate_message(chatroom_id: str, text: str) -> dict:
    return {
        "chatroomId": chatroom_id,
        "msgType": "TEXT",
        "chatMsg": text,
    }

4) 메신저 전송 Task 정의

위 데코레이터를 적용한다.

from dags._common.rise_messenger_task import messenger_task

@messenger_task(conn_id="rise_messenger", endpoint="/api/v1/message", timeout=5)
def send_message(message: dict):
    return message  # generate_message의 결과를 그대로 전송

5) DAG에서 연결

from airflow.decorators import dag
from datetime import datetime

@dag(
    dag_id="RISE_MessagePipeline",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["messenger"],
)
def rise_message_pipeline():
    msg = generate_message(chatroom_id="195878155435574272", text="파이프라인 완료")
    send_message(msg)

dag = rise_message_pipeline()

6) 확장 포인트

파일·이미지·AdaptiveCard: generate_message에서 payload 스키마만 바꿔 반환.

엔드포인트 분기: @messenger_task(..., endpoint="/api/v1/appcard").

토큰 회전: Airflow Connection headers.Authorization만 갱신.

멱등성: messageId 필드를 만들어 서버측 중복 수신 방지.


7) 운영 체크리스트

네트워크: 워커에서 메신저 URL 통신 가능 여부.

보안: 토큰은 Connection/Secret에 보관. 코드에 하드코딩 금지.

재시도: 5xx만 재시도하려면 데코레ータ 내부에서 상태코드별 분기.

레이트리밋: 429 수신 시 time.sleep 또는 재시도 지수백오프 적용.


끝.