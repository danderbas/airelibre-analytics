FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml Makefile ./

ENV PIP_ROOT_USER_ACTION=ignore

RUN make install

COPY . .

# for the streamlit dashboard
EXPOSE 8501
