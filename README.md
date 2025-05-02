# OpenShift Flask Demo Application with CI/CD and Monitoring

## Overview

This repository contains a simple Flask demo application designed to run on OpenShift Container Platform (OCP) 4.18. It includes:

*   A basic Flask application serving static content and a sample API endpoint.
*   Structured logging and Prometheus metrics endpoint (`/metrics`) for observability.
*   A health check endpoint (`/healthz`) for OpenShift liveness/readiness probes.
*   A Dockerfile for containerizing the application.
*   OpenShift manifests (Deployment, Service, Route) for deployment.
*   A GitHub Actions CI/CD pipeline (`.github/workflows/main.yaml`) for automated build and deployment to OpenShift.
*   A sample Grafana dashboard (`grafana-dashboard.json`) for visualizing application metrics and logs.

## Directory Structure 

```
openshift-demo-app/
├── .github/
│   └── workflows/
│       └── main.yaml           # GitHub Actions CI/CD workflow
├── openshift/
│   ├── deployment.yaml       # OpenShift Deployment manifest
│   ├── route.yaml            # OpenShift Route manifest
│   └── service.yaml          # OpenShift Service manifest
├── src/
│   ├── static/               # Directory for static frontend files (e.g., index.html)
│   └── main.py             # Flask application entry point with logging & metrics
├── Dockerfile                # Container build instructions
├── grafana-dashboard.json    # Sample Grafana dashboard definition
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Prerequisites

1.  **OpenShift Cluster:** Access to an OpenShift 4.18 cluster.
2.  **OpenShift Project:** An existing project (namespace) within your OpenShift cluster where the application will be deployed.
3.  **OpenShift Monitoring:** Prometheus (usually via Prometheus Operator) installed and configured in your cluster to scrape metrics. Loki (optional, for log panel) installed and configured if you want to use the logs panel in the Grafana dashboard.
4.  **GitHub Repository:** A GitHub repository to host this code and run the Actions workflow.
5.  **OpenShift CLI (`oc`):** Optional, but useful for manual interaction with the cluster.

## Setup and Deployment

### 1. GitHub Actions CI/CD (Recommended)

This is the primary method for building and deploying the application.

*   **Push Code:** Push the contents of this directory to your GitHub repository.
*   **Configure Secrets:** In your GitHub repository settings (`Settings > Secrets and variables > Actions`), add the following secrets required by the `.github/workflows/main.yaml` workflow:
    *   `OPENSHIFT_SERVER_URL`: The API server URL of your OpenShift cluster (e.g., `https://api.your-cluster.openshift.com:6443`).
    *   `OPENSHIFT_TOKEN`: An API token for a service account or user with permissions to build images, push to the internal registry, and manage deployments, services, and routes in your target OpenShift project. You can create a service account and get its token using `oc` commands.
    *   `OPENSHIFT_REGISTRY_URL`: The URL of the OpenShift internal image registry (e.g., `image-registry.openshift-image-registry.svc:5000`).
    *   `OPENSHIFT_REGISTRY_USER`: The username for logging into the registry. Often the name of the service account used to get the token (e.g., `system:serviceaccount:your-project:your-service-account`).
    *   `OPENSHIFT_REGISTRY_PASSWORD`: The same API token used for `OPENSHIFT_TOKEN` often works as the password for the internal registry login.
*   **Update Workflow:** Edit `.github/workflows/main.yaml` and replace the placeholder `your-openshift-project` in the `env` section with the actual name of your OpenShift project.
*   **Trigger Workflow:** Push a change to the `main` branch (or the branch specified in the workflow's `on` trigger). The workflow will:
    1.  Log in to the OpenShift internal registry.
    2.  Build the Docker image.
    3.  Push the image to the internal registry with tags `latest` and based on the Git commit SHA.
    4.  Log in to the OpenShift cluster.
    5.  Apply the OpenShift manifests (`deployment.yaml`, `service.yaml`, `route.yaml`), substituting the correct image tag in the deployment.
    6.  Optionally trigger a deployment rollout.

### 2. Manual Deployment (Alternative)

You can also build and deploy manually:

1.  **Build Image:** Build the Docker image locally: `docker build -t openshift-demo-app:manual .`
2.  **Push Image:** Push the image to a registry accessible by your OpenShift cluster (like the internal registry or an external one like Docker Hub/Quay.io). You'll need to tag it appropriately first (e.g., `docker tag openshift-demo-app:manual image-registry.openshift-image-registry.svc:5000/your-project/openshift-demo-app:manual` and then `docker push ...`).
3.  **Update Manifests:** Edit `openshift/deployment.yaml` and replace the `image:` line with the full path to your manually pushed image.
4.  **Apply Manifests:** Log in to your OpenShift cluster using `oc login` and apply the manifests: `oc apply -f openshift/ -n your-project`

## Monitoring with Grafana

1.  **Prometheus:** Ensure Prometheus is scraping metrics in your OpenShift project. The service `openshift-demo-app-service` should be automatically discovered if Prometheus Operator is configured correctly (it looks for services with specific annotations or labels, which might need adding to `service.yaml` depending on your setup).
2.  **Grafana Data Sources:**
    *   In Grafana, add or ensure you have a Prometheus data source configured to point to your OpenShift cluster's Prometheus instance.
    *   (Optional) If using Loki for logs, add a Loki data source pointing to your Loki instance.
3.  **Import Dashboard:** In Grafana, import the `grafana-dashboard.json` file provided. Select the correct Prometheus (and optionally Loki) data source during import.
4.  **Verify:** The dashboard should start showing metrics like request rate, latency, and error counts scraped from the `/metrics` endpoint of the running application. The logs panel will show error logs if Loki is configured and scraping logs from the application pods.

## Application Endpoints

Once deployed via the Route, the application will be accessible at the generated hostname. It exposes:

*   `/`: Serves `static/index.html` (or a default message if not present).
*   `/healthz`: Health check endpoint (returns `{"status": "OK"}`).
*   `/metrics`: Prometheus metrics endpoint.
*   `/api/hello`: Sample API endpoint (returns `{"message": "Hello from the API!"}`).

