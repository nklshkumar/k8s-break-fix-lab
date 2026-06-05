# Kubernetes Break-Fix Learning Lab

## Overview

This project was created to learn Kubernetes through hands-on troubleshooting rather than just deploying applications.

The lab uses:

* GitHub Codespaces
* Docker
* Kind (Kubernetes in Docker)
* Flask Application
* Kubernetes Deployments
* Kubernetes Services
* Readiness & Liveness Probes
* Resource Limits

---

# Project Structure

```text
.
├── app.py
├── Dockerfile
├── deployment.yaml
├── service.yaml
└── README.md
```

---

# Prerequisites

Verify tools are installed:

```bash
docker --version
kubectl version --client
kind version
```

---

# Create Kind Cluster

```bash
kind create cluster --name k8s-lab
```

Verify:

```bash
kubectl cluster-info
kubectl get nodes
```

Expected:

```text
NAME                         STATUS
k8s-lab-control-plane        Ready
```

---

# Build Docker Image

```bash
docker build -t flask-demo:v1 .
```

Load image into Kind:

```bash
kind load docker-image flask-demo:v1 --name k8s-lab
```

---

# Deploy Application

Apply deployment:

```bash
kubectl apply -f deployment.yaml
```

Verify:

```bash
kubectl get deployments
kubectl get pods
```

---

# Create Service

Apply service:

```bash
kubectl apply -f service.yaml
```

Verify:

```bash
kubectl get svc
```

---

# Service Discovery Testing

Create temporary BusyBox pod:

```bash
kubectl run testpod --image=busybox:1.36 -it --rm -- sh
```

Inside pod:

```bash
nslookup flask-service
```

Expected:

```text
flask-service.default.svc.cluster.local
```

Test service communication:

```bash
wget -qO- http://flask-service
```

Expected:

```text
Hello from Kubernetes!
```

---

# Port Forwarding

Expose service locally:

```bash
kubectl port-forward svc/flask-service 8080:80
```

Access:

```bash
curl localhost:8080
```

---

# Troubleshooting Labs

---

## Lab 1 - ImagePullBackOff

### Purpose

Learn how Kubernetes behaves when an image cannot be pulled.

### Break It

Change image:

```yaml
image: flask-demo:does-not-exist
```

Apply:

```bash
kubectl apply -f deployment.yaml
```

### Observe

```bash
kubectl get pods
```

Expected:

```text
ImagePullBackOff
```

### Diagnose

```bash
kubectl describe pod <pod-name>
```

Look at:

```text
Events
```

Expected:

```text
Failed to pull image
```

### Fix

Restore valid image.

```yaml
image: flask-demo:v1
```

Apply again.

---

## Lab 2 - CrashLoopBackOff

### Purpose

Learn application startup failure troubleshooting.

### Break It

Modify Flask app:

```python
raise Exception("Application Startup Failed")
```

Build new image.

```bash
docker build -t flask-demo:v2 .
kind load docker-image flask-demo:v2 --name k8s-lab
```

Update deployment.

```yaml
image: flask-demo:v2
```

Apply.

### Observe

```bash
kubectl get pods
```

Expected:

```text
CrashLoopBackOff
```

### Diagnose

```bash
kubectl logs <pod-name>
```

Expected:

```text
Application Startup Failed
```

### Fix

Remove exception and rebuild image.

---

## Lab 3 - Readiness Probe Failure

### Purpose

Understand traffic removal without restart.

### Break It

Modify readiness probe:

```yaml
readinessProbe:
  httpGet:
    path: /broken
    port: 5000
```

Apply.

### Observe

```bash
kubectl get pods
```

Expected:

```text
READY 0/1
STATUS Running
```

### Verify

```bash
kubectl get endpoints flask-service
```

Pod endpoint disappears.

### Learning

* Pod is running.
* Pod is not ready.
* Service stops sending traffic.

---

## Lab 4 - Liveness Probe Failure

### Purpose

Understand automatic container restarts.

### Break It

Modify liveness probe:

```yaml
livenessProbe:
  httpGet:
    path: /dead
    port: 5000
```

Apply.

### Observe

```bash
kubectl get pods -w
```

Expected:

```text
RESTARTS increasing
```

### Diagnose

```bash
kubectl describe pod <pod-name>
```

Look for:

```text
Liveness probe failed
```

### Learning

Readiness:

* Controls traffic.

Liveness:

* Controls restarts.

---

## Lab 5 - OOMKilled

### Purpose

Understand memory limit violations.

### Add Resources

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"

  limits:
    memory: "128Mi"
    cpu: "200m"
```

### Create Memory Leak

Modify application:

```python
memory = []

@app.route("/")
def home():
    while True:
        memory.append("A" * 1024 * 1024)
```

Build:

```bash
docker build -t flask-demo:v3 .
kind load docker-image flask-demo:v3 --name k8s-lab
```

Update deployment image:

```yaml
image: flask-demo:v3
```

Apply.

Trigger:

```bash
curl localhost:8080
```

### Observe

```bash
kubectl get pods -w
```

Restart count increases.

### Diagnose

```bash
kubectl describe pod <pod-name>
```

Expected:

```text
Reason: OOMKilled
```

### Important Command

View previous crashed logs:

```bash
kubectl logs <pod-name> --previous
```

---

# Useful Commands

Get pods:

```bash
kubectl get pods
```

Watch pods:

```bash
kubectl get pods -w
```

Describe pod:

```bash
kubectl describe pod <pod-name>
```

View logs:

```bash
kubectl logs <pod-name>
```

View previous logs:

```bash
kubectl logs <pod-name> --previous
```

Deployment history:

```bash
kubectl rollout history deployment/flask-demo
```

ReplicaSets:

```bash
kubectl get rs
```

Services:

```bash
kubectl get svc
```

Endpoints:

```bash
kubectl get endpoints
```

---

# Cleanup

Delete deployment:

```bash
kubectl delete deployment flask-demo
```

Delete service:

```bash
kubectl delete service flask-service
```

Delete cluster:

```bash
kind delete cluster --name k8s-lab
```

Verify:

```bash
kind get clusters
```

Expected:

```text
(no output)
```

---

# Key Learnings

* Deployment → ReplicaSet → Pod relationship
* Service discovery using DNS
* Service to Pod communication
* ImagePullBackOff troubleshooting
* CrashLoopBackOff troubleshooting
* Readiness Probe behavior
* Liveness Probe behavior
* Resource Requests vs Limits
* OOMKilled troubleshooting
* Rollout history and ReplicaSets
* Kubernetes production debugging workflow
