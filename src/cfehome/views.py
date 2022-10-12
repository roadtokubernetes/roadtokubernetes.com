import markdown
from django.shortcuts import render


def index(request):
    title="Road to Kubernetes"
    content = """
## Coming Soon

`k8s/hello-world.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
    name: roadtok8s
```

## Are you ready?

```bash
kubectl apply -f k8s/hello-world.yaml
```
    """
    context = {
        "title": title,
        "content":  content
    }
    return render(request, 'index.html', context)
