# syntax=docker/dockerfile:1

FROM python:3.13-slim
RUN apt-get update && apt-get install -y python3-pip

ARG ARG_HERE
ENV ARG_HERE=$ARG_HERE

RUN pip3 install pipenv

COPY . .

RUN pipenv sync

# Expose the port (if needed for the service)
EXPOSE 8000

ENTRYPOINT ["pipenv", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
