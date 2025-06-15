# syntax=docker/socerfile:1

FROM python:3.13-slim
RUN apt-get update && apt-get install -y python3-pip

ARG ARG_HERE
ENV ARG_HERE=$ARG_HERE

RUN pip3 install pipenv && pipenv sync

COPY ./ ./

# Expose the port (if needed for the service)
EXPOSE 1234

ENTRYPOINT ["pipenv", "run", "python", "main.py"]
CMD ["$ARG_HERE"]