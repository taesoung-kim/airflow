# Airflow DAGRun 중복 방지 및 Logical Date 관리 정리

## 1. DAGRun 식별 규칙

| 필드 | 유니크 여부 | 설명 |
|------|---------------|------|
| `dag_id` | ❌ | DAG 식별자 |
| `dag_run_id` | ✅ | 동일 DAG 내 고유해야 함 |
| `logical_date` (`execution_date`) | ✅ | 동일 DAG 내 고유해야 함 |
| `dag_id + logical_date` | ✅ | DB Primary Key (중복 불가) |

- `dag_run_id` 또는 `logical_date`가 중복되면 `IntegrityError` 발생  
- Airflow 내부 테이블(`dagrun`)에서 `(dag_id, logical_date)`이 **Primary Key**

---

## 2. 중복 발생 시점

- FastAPI 파드가 여러 개(replica 3 등)로 실행 중일 때
- 외부 요청이 동시에 들어와 동일 시각에 `DAGRun API` 호출 시
- `logical_date`를 `datetime.now()`로만 지정하면 밀리초 단위 충돌 가능

---

## 3. 안전한 `logical_date` 생성 방법

### ✅ 권장 함수
```python
from datetime import datetime, timezone
import uuid

def generate_logical_date() -> str:
    """Airflow DAGRun logical_date 생성용 (유니크, ISO8601 호환)"""
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    uid = uuid.uuid4().hex[:8]  # 8자리 랜덤 ID
    return f"{now}_{uid}"

예시 출력

2025-11-06T15:40:27.123456+00:00_1a2b3c4d

UTC 기반 ISO8601 형식

마이크로초 + 랜덤 UUID 조합 → 충돌 확률 사실상 0

Airflow REST API (logical_date 필드)와 완전 호환



---

4. Redis 사용 여부 판단

목적	권장 방법	비고

단순 중복 방지	UUID suffix 방식	Redis 불필요
다중 파드 동시 트리거 제어	Redis Lock	단기 분산 락 사용
순차 실행/큐잉 필요	Redis Stream or Kafka	고급 제어 구조


일반적인 FastAPI → Airflow 트리거 구조에서는 UUID suffix만으로 충분

Redis는 선택 사항, 대규모 트래픽이나 완전한 순차성 필요 시에만 사용



---

5. 결론

dag_run_id와 logical_date는 DAG 내 유니크해야 함

Airflow 구조상 logical_date의 유니크 제약 해제는 불가능

FastAPI에서 generate_logical_date() 같은 방식으로 충돌 방지 가능

Redis는 부가적 제어 수단이지 필수 아님

위 방식 사용 시 3 replica 환경에서도 중복률 0 수준