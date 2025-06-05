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


class HelloPlugin(AirflowPlugin):
    name = "hello_plugin"
    operators = [HelloOperator]
