#!/bin/bash
# wait-for-kafka.sh

set -e

host="$1"
shift
cmd="$@"

until kcat -b "$host" -L >/dev/null 2>&1; do
  >&2 echo "Kafka is unavailable - sleeping"
  sleep 5
done

>&2 echo "Kafka is up - executing command"
exec $cmd