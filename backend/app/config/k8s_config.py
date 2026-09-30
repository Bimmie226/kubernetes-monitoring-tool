from kubernetes import client, config
from kubernetes.dynamic import DynamicClient

from app.config.settings import settings


api_client = config.new_client_from_config(
    config_file=settings.KUBERNETES_PATH
)

dynamic_client = DynamicClient(api_client)

core_v1 = client.CoreV1Api(api_client)
apps_v1 = client.AppsV1Api(api_client)