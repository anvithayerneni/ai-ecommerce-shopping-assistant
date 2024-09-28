# ☸️ Kubernetes Deployment Guide

This directory contains cloud-native Kubernetes manifests to deploy the **AI-Powered E-Commerce Shopping & Recommendation Assistant** with high availability, automated horizontal scaling, secret management, and ingress routing.

---

## 🏛️ Architecture Overview

```text
               [ Internet / Client Traffic ]
                             │
                             ▼
                    ┌─────────────────┐
                    │ NGINX Ingress   │
                    └────────┬────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │  ClusterIP Service (Port 80) │
              └──────────────┬──────────────┘
                             │
       ┌─────────────────────┴─────────────────────┐
       │                                           │
       ▼                                           ▼
┌──────────────┐                            ┌──────────────┐
│  Pod Replica │ ◄── [ HPA Autoscaling ] ──►│  Pod Replica │
│ (FastAPI/AI) │     (Min: 2, Max: 10)      │ (FastAPI/AI) │
└──────┬───────┘                            └──────┬───────┘
       │                                           │
       └─────────────────────┬─────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Postgres Service:5432 │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ PersistentVolumeClaim│ (10Gi)
                  └──────────────────────┘
```

---

## 📦 Manifest Inventory

| Manifest | Kind | Purpose |
| :--- | :--- | :--- |
| `namespace.yaml` | `Namespace` | Creates isolated `ecommerce-assistant` namespace |
| `configmap.yaml` | `ConfigMap` | Non-sensitive configurations (database host, environment) |
| `secret.yaml` | `Secret` | Credentials for Azure OpenAI, Azure Search, and Postgres |
| `postgres.yaml` | `PVC`, `Deployment`, `Service` | State-managed PostgreSQL database service with persistent volume |
| `deployment.yaml` | `Deployment` | FastAPI assistant with rolling updates & health/readiness probes |
| `service.yaml` | `Service` | Internal load balancing and cluster traffic routing |
| `hpa.yaml` | `HorizontalPodAutoscaler` | Auto-scales pods from 2 to 10 based on CPU/memory utilization |
| `ingress.yaml` | `Ingress` | Reverse proxy and TLS endpoint routing |
| `kustomization.yaml` | `Kustomization` | Enables one-command declarative cluster rollout |

---

## 🚀 Quickstart Deployment

### 1. Prerequisites
- `kubectl` installed
- A running Kubernetes cluster (Minikube, Kind, AWS EKS, GCP GKE, or Azure AKS)

### 2. Deploy All Resources with Kustomize

```bash
# 1. Apply all resources in declarative order
kubectl apply -k k8s/

# 2. Verify all pods are running and healthy
kubectl get pods -n ecommerce-assistant

# 3. Check services and endpoints
kubectl get svc,ingress,hpa -n ecommerce-assistant
```

### 3. Port Forwarding for Local Testing

```bash
kubectl port-forward svc/ecommerce-api-service 8000:80 -n ecommerce-assistant
```
Visit the interactive UI at `http://localhost:8000/demo/` or check health at `http://localhost:8000/health`.

---

## 🛡️ Production Best Practices Implemented
1. **Zero Downtime Updates:** Rolling update strategy (`maxSurge: 1`, `maxUnavailable: 0`).
2. **Container Health Monitoring:** Liveness and Readiness probes configured on `/health`.
3. **Elastic Autoscaling:** HPA automatically adjusts pod count when CPU load crosses 70%.
4. **Decoupled Secrets:** Sensitive API keys kept out of application images via native Kubernetes `Secret` resources.
