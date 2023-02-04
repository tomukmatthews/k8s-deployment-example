# k8s local deployment example (MacOS only)

## Prerequisites
1. Install Docker, kubectl, minikube and poetry
2. `brew install nginx`


## Run the app locally from a single container

1. Build the Docker image `docker build -t k8s-deployment-example .`
2. Run the container `docker run --rm -p 80:80 k8s-deployment-example`
3. Test the endpoint `curl http://0.0.0.0:80` 

You should get something like: `{"message":"Hello World","instance_id":"ddf3de45-0234-4fb0-82d5-0c9a5460a49e"}`

Where the instance_id is the same for all requests as we've fired up a single containerised instance of the app.

## Deploy the app locally with Kubernetes

We're going to use Minikube to run a local Kubernetes cluster - we're going to fire up 5 replicas of the app and expose it via an Ingress.

### Configure Minikube

We must allow enable ingress and ingress-dns addons for Minikube to work with Ingress.
- `minikube addons enable ingress`
- `minikube addons enable ingress-dns`

Start a local Kubernetes cluster with Minikube
`minikube start --driver=docker`

Load the Docker image into Minikube
`minikube image load k8s-deployment-example`

### Create the deployment

The defines what pods we want to run and how many replicas we want to run them.

`kubectl apply -f k8s/static/deployment.yaml`

### Create the service

`kubectl apply -f k8s/static/service.yaml`

View the serivce resource:

`kubectl get svc`

```
NAME                  TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
fastapi-app-service   ClusterIP   10.101.126.141   <none>        80/TCP    18h
kubernetes            ClusterIP   10.96.0.1        <none>        443/TCP   8d
```

You can now ssh into the minikube k8s cluster and test the service is running:

`ssh minikube`

Then you can curl the service:

`curl 10.101.126.141`

`{"message":"Hello World","instance_id":"e82c0a45-bddb-402b-b8aa-42fd17b50129"}`

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

Now you can curl the ingress:

`curl -X POST fastapi-app.com/entropy -H 'Content-Type: application/json' -d '{"values":[1,12,2,3,2,43,2,4,2,42]}'`

### Load testing

Now the fun part, lets load test the app. We'll use Locust to do this.

First we need to install the dependencies:

`poetry install`

Now we can run the load test:

`poetry run locust -f load_test/locustfile.py --host=http://fastapi-app.com`

## Appendix

If you run into issues I found this helpful:

https://stackoverflow.com/questions/58561682/minikube-with-ingress-example-not-working