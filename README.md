# k8s local deployment walkthrough (MacOS only)

In this tutorial, we will be deploying a simple FastAPI app with an endpoint that calculates the entropy of a list of numbers to a local Kubernetes cluster. The goal is to help you understand how to deploy a containerized application on a local Kubernetes cluster and the concepts involved in it.

## Prerequisites

Before setting up your environment for this project, you need to install the following tools:

1. [Docker](https://www.docker.com/products/docker-desktop)
2. [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
3. [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)
4. [poetry](https://python-poetry.org/docs/#installation)
5. nginx:
   - `brew install nginx`


## Run the app locally from a single container

1. Build the Docker image `docker build -t fastapi-entropy-app .`
2. Run the container `docker run --rm -p 80:80 fastapi-entropy-app`
3. Test the endpoint `curl http://0.0.0.0:80` 

You should get something like: `{"message":"Hello World","instance_id":"ddf3de45-0234-4fb0-82d5-0c9a5460a49e"}`

Where the instance_id is the same for all requests as we've fired up a single containerised instance of the app.

## Deploy the app locally with Kubernetes

We're going to use Minikube to run a local Kubernetes cluster - we're going to fire up 5 replicas of the app and expose it via an Ingress.

### Configure Minikube

We need this Minikube addons to get ingress working and check pod usage metrics later on.

- `minikube addons enable ingress`
- `minikube addons enable ingress-dns`
- `minikube addons enable metrics-server`

Start a local Kubernetes cluster with Minikube
`minikube start --driver=docker`

Load the Docker image into Minikube
`minikube image load fastapi-entropy-app`

### Optional
You can open the minikube dashboard to see the cluster resources in a GUI:

`minikube dashboard`

### Create the deployment

The deployment defines what pods we want to run and how many replicas we want to run them.

`kubectl apply -f k8s/static/deployment.yaml`

### Create the service

The service defines how we want to access the pods, which will be via a cluster IP.

`kubectl apply -f k8s/static/service.yaml`

View the service resource: `kubectl get svc`

```
NAME                  TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
fastapi-app-service   ClusterIP   10.101.126.141   <none>        80/TCP    18h
kubernetes            ClusterIP   10.96.0.1        <none>        443/TCP   8d
```

As a sanity check you can ssh into the minikube k8s cluster and test the service is running:

`ssh minikube`

Then you can curl the service:

`curl <CLUSTER-IP>` from the fastapi-app-service CLUSTER-IP above.

```
{"message":"Hello World","instance_id":"e82c0a45-bddb-402b-b8aa-42fd17b50129"}
```

Now note that you get different instance ids as you're hitting different pods.

### Create the ingress

We want to be able to access the service via a domain name, so we need to create an ingress resource. This will create a load balancer and route traffic to the service.

We'll use ngingx as the ingress controller. Check the ingress controller is running:

`kubectl get pods -n ingress-nginx`

You should see something like:

```
ingress-nginx-controller-5959f988fd-p2krf   1/1     Running     4 (8m18s ago)   2d11h
```

Now create the ingress resource:

`kubectl apply -f k8s/static/ingress.yaml`

Add the ingress domain to your hosts file:

`echo "127.0.0.1 fastapi-app.com" | sudo tee -a /etc/hosts`

Open a new terminal window and tunnel the ingress:

`minikube tunnel`

Now you can curl the host surfaced by the ingress:

`curl -X POST fastapi-app.com/entropy -H 'Content-Type: application/json' -d '{"values":[1,12,2,3,2,43,2,4,2,42]}'`

### Load testing

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

You can scale up the number of replicas to 10 pods with:

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

If you run into issues I found this helpful:

https://stackoverflow.com/questions/58561682/minikube-with-ingress-example-not-working
