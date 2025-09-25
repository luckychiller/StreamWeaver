# backend/consumer/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/consumer/requirements.txt .
RUN apt-get update && \
    apt-get install -y default-jre kcat && \
    pip install --no-cache-dir -r requirements.txt

ENV KAFKA_VERSION=3.6.1
ENV SCALA_VERSION=2.13

RUN apt-get install -y wget && \
    wget https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz && \
    tar -xzf kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz && \
    mv kafka_${SCALA_VERSION}-${KAFKA_VERSION} /opt/kafka && \
    rm kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz

ENV PATH="${PATH}:/opt/kafka/bin"

# Copy the wait-for-kafka script and make it executable
COPY ./scripts/wait-for-kafka.sh /usr/local/bin/wait-for-kafka.sh
RUN chmod +x /usr/local/bin/wait-for-kafka.sh

COPY . /app

ENV PYTHONPATH=/app

CMD ["python", "-m", "backend.consumer.consumer"]