# k8s-deployment-example

## Prerequisites
1. Install Docker, kubectl, minikubekubectl describe ingress
2. `brew install nginx`

Example deployment of an ML Model using Kubernetes

1. Build the Docker image `docker build -t k8s-deployment-example .`
2. Run the container `docker run --rm -p 80:80 k8s-deployment-example`
3. Test the endpoint `curl http://0.0.0.0:80` 


<!-- k8s -->
`minikube addons enable ingress`
`minikube addons enable ingress-dns`
`minikube start --driver=docker`
`minikube image load k8s-deployment-example`

https://stackoverflow.com/questions/58561682/minikube-with-ingress-example-not-working

`kubectl get pods -n ingress-nginx`
`echo "127.0.0.1 fastapi-app.com" | sudo tee -a /etc/hosts`
`minikube tunnel`

`curl -X POST fastapi-app.com/entropy -H 'Content-Type: application/json' -d '{"values":[1,12,2,3,2,43,2,4,2,42]}'`


`docker build -t locust-fastapi-load-test ./load_test`

`poetry run locust -f load_test/locustfile.py --host=http://fastapi-app.com`