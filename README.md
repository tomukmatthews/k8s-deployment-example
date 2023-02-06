# k8s local deployment example

In this tutorial, we will be deploying a simple FastAPI app with an endpoint that calculates the entropy of a list of numbers to a local Kubernetes cluster. The goal is to help you understand how to deploy a containerized application on a local Kubernetes cluster, see Kubernetes Key Concepts section in the Appendix for a primer on Kubernetes concepts.

### Caveats:
- This is a very simple getting started type example, it's not production ready. This is a local deployment, so it's not really a cluster, but it's a good way to get started with Kubernetes.
- Assumes familiarity with Docker, Kubernetes, and FastAPI (but not necessary for the walkthrough)
- Has only been tested on MacOS.

## Prerequisites

Before setting up your environment for this project, you need to install the following tools:

1. [Docker](https://www.docker.com/products/docker-desktop)
2. [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
3. [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)
4. [poetry](https://python-poetry.org/docs/#installation)
5. nginx:
   - `brew install nginx`

### Configure Minikube

We need this Minikube addons to get ingress working and check pod usage metrics later on.

1. `minikube addons enable ingress`
2. `minikube addons enable ingress-dns`
3. `minikube addons enable metrics-server`

## Deployment with Kubernetes

We're going to use Minikube to run a local Kubernetes cluster - we're going to fire up 5 replicas of the app and expose it via an Ingress.

1. Build the Docker image `docker build -t fastapi-entropy-app .`
   1. You can verify test the image locally by running the container with `docker run --rm -p 80:80 fastapi-entropy-app` and testing the endpoint with `curl http://0.0.0.0:80`. You should get something like: `{"message":"Hello World","instance_id":"ddf3de45-0234-4fb0-82d5-0c9a5460a49e"}` - the instance_id is the same for all requests as we've fired up a single containerised instance of the app.
2. Start a local Kubernetes cluster with Minikube `minikube start --driver=docker` (in a new terminal window).
3. Load the Docker image into Minikube `minikube image load fastapi-entropy-app`
4. Configure Minikube addons for ingress and metrics-server `minikube addons enable ingress && minikube addons enable ingress-dns && minikube addons enable metrics-server`
5. Create the deployment `kubectl apply -f k8s/static/deployment.yaml` and view it `kubectl get deploy`.
6. Create the service `kubectl apply -f k8s/static/service.yaml` and view it `kubectl get svc`.
   1. At this point we have a service running on the cluster consisting of 5 replicas, and we can access it from within the cluster.
   2. `minikube ssh` to ssh into the cluster, then you can `curl <CLUSTER-IP>` from the fastapi-app-service CLUSTER-IP above to check the service is running as expected. Now note that you get different instance_id's as you're hitting different pods thanks to the load balancing.
   3. However, we want to access the service from outside the cluster, so we need to create an ingress.
7. Create the ingress `kubectl apply -f k8s/static/ingress.yaml` and add the ingress domain to your hosts file: `echo "127.0.0.1 fastapi-app.com" | sudo tee -a /etc/hosts`.
   1. Troubleshooting: First check that the ingress is running and ready with `kubectl get pods -n ingress-nginx`.
8. `minikube tunnel` (in a new terminal window) - opens a secure tunnel between the Minikube cluster and the host machine to route the traffic to the service`minikube tunnel`
9.  (Optional) Open the minikube dashboard `minikube dashboard` to see the cluster resources in a GUI.
10. Now you can send API requests to the host surfaced by the ingress (A.K.A our locally deployed Kubernetes cluster!): `curl -X POST fastapi-app.com/entropy -H 'Content-Type: application/json' -d '{"values":[1,12,2,3,2,43,2,4,2,42]}'`

## Load testing

Now the fun part, lets load test the app. We'll use Locust to do this - it's a simple Python based load testing tool.

First we need to install the dependencies:

`poetry install`

Now we can run the load test:

`poetry run locust -f load_test/locustfile.py --host=http://fastapi-app.com`

Then open the Web UI at http://localhost:8089 and start the load test (you can change the number of users and spawn rate, 
I used 10 users and 1 spawn rate).

Spawn rate is the rate in which users are spawned. So if you have 100 users and a spawn rate of 10, then 10 users will be spawned every second.

Number of users is the total number of users that will be spawned.

You can experiment with different values to see how the app performs under load. Try ramping up the load test, then you can
view the pods handling the load with:

`kubectl top pods`

There's a delay in load scaling and the metrics to keep re-running `kubectl top pods` and you should see the pods usage metrics increase. You can scale up the number of replicas to 10 pods with:

`kubectl scale --replicas=10 deployment/fastapi-app-deployment`

### Locust Demo

![](https://github.com/tomukmatthews/k8s-deployment-example/blob/main/gifs/locust_demo.gif)

## Autoscaling

We can use the Horizontal Pod Autoscaler to scale the number of pods based on CPU usage. In `k8s/autoscale.yaml` we create
a `HorizontalPodAutoscaler` resource that will scale the number of pods based on the CPU usage of the pods. We set a minimum of 2 pod and a maximum of 10 pods.

Create the resource:  `kubectl apply -f k8s/autoscale.yaml`

Then you can test that the autoscaler is working by **running the load test again** (e.g. spawn rate - 10, num users - 50):

Check the pod usage metrics:

`kubectl top pods`

You should see the number of pods **eventually** increase as the load increases (you can lower the `averageUtilization` in the `k8s/autoscale.yaml` to make it scale up quicker).

## Appendix

If you run into issues, ask chatGPT for help, 90% of the time it will guide you to a solution.

### Kubernetes Key Concepts

Kubernetes is a container orchestration system that automates the management and deployment of containerized applications. It provides a set of core concepts that are used to define and manage the components of a Kubernetes cluster. Here are some of the core concepts of Kubernetes:

- **Pods**: A Pod is the smallest and simplest unit in the Kubernetes object model. It represents a single instance of a running process in a cluster. Pods can contain one or more containers, and all containers in a Pod share the same network namespace, IP address, and storage volumes.
- **Replication Controllers**: A Replication Controller ensures that a specified number of replicas of a Pod are running at any given time. It replaces or automatically restarts Pods that fail or are deleted.
- **Deployments**: A Deployment is an abstraction that provides declarative updates for Pods and Replication Controllers. It allows you to define the desired state of your application (e.g. the number of replicas and the container image to use) and the system takes care of making the necessary updates to reach that state.
- **Services**: A Service provides a stable endpoint for accessing one or more Pods in a cluster. It abstracts the network details of the Pods from the clients that need to access them, and can load balance traffic across multiple replicas of a Pod.
- **Namespaces**: Namespaces provide a way to group resources together in a cluster. Each Namespace has its own set of resources, including Pods, Services, and Deployments, and can be used to isolate different parts of an application or different teams.
- **Volumes**: Volumes provide a way to persist data in a cluster. They can be used to store data that should survive the lifetime of a Pod, such as logs or configuration files. Kubernetes supports different types of volumes such as HostPath, EmptyDir, ConfigMap, Secret etc.
- **Ingress**: Ingress allows external users to access Services in a cluster by providing a single point of entry. It allows to configure rules to route external requests to different Services based on the URL path or hostname.
- **ConfigMaps**: ConfigMaps allow you to decouple configuration artifacts from image content to keep containers portable. You can use a ConfigMap to store configuration files, environment variables, command-line arguments, or other data that a container needs to run.
- **Secrets**: Secrets allow you to store sensitive information, such as passwords, tokens, or certificates, in a Kubernetes cluster. They are similar to ConfigMaps but with added encryption and more strict access controls.
