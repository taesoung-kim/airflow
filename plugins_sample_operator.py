# plugins/hello_operator.py
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook
from airflow.plugins_manager import AirflowPlugin


class HelloOperator(BaseOperator):
    """
    conn_id 로 지정한 커넥션 정보를 읽어 로그에 출력한다.
    KubernetesExecutor 로 실행해도 get_connection() 은 그대로 동작한다.
    """
    @apply_defaults
    def __init__(self, conn_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn_id = conn_id

    def execute(self, context):
        conn = BaseHook.get_connection(self.conn_id)
        self.log.info("👋  Hello from %s!", self.conn_id)
        self.log.info(" ↪ host=%s, schema=%s, login=%s",
                      conn.host, conn.schema, conn.login)

# DAG만 import 해서 쓸 목적이라면 HelloPlugin 클래스를 빼도 실행에는 지장 없습니다.
# **플러그인 형태(재사용·UI 노출·airflow plugins 확인 등)**로 관리하려면 AirflowPlugin 서브클래스를 하나 두는 편이 여전히 권장

class HelloPlugin(AirflowPlugin):
    name = "hello_plugin"
    operators = [HelloOperator]
