FROM locustio/locust:latest

COPY ./ /mnt/locust

WORKDIR /mnt/locust/

EXPOSE 8089

ENTRYPOINT [ "locust", "-f", "/mnt/locust/locustfile.py" ]