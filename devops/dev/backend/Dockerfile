FROM python:3.12-slim

# When installing libraries for either arm or amd
# Put packages in respective architecture under devops/libraries
# ARG ARCHITECTURE

RUN apt update && apt -y upgrade

RUN mkdir /custom_admin_backend
WORKDIR /custom_admin_backend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /custom_admin_backend/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./src /custom_admin_backend/src/
COPY ./keys /custom_admin_backend/keys/
COPY ./docker.env /custom_admin_backend/docker.env
RUN chmod +x /custom_admin_backend/src/run_dev.sh

