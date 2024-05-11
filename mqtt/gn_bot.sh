#!/bin/bash

# Check if IP_ALOHA environment variable is set
if [ -z "${IP_ALOHA}" ]; then
    echo "Error: IP_ALOHA environment variable is not set."
    exit 1
fi

# Function to handle Ctrl+C signal
trap 'echo "Exiting..."; exit 0' SIGINT

# Continuous loop
while true; do
    # Generate 20 characters of random data
    RANDOM_DATA=$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 20)

    # Send MQTT message
    mosquitto_pub -h "${IP_ALOHA}" -t "test" -m "${RANDOM_DATA}"

    # Wait for a short period before sending the next message
    sleep 0.2
done
