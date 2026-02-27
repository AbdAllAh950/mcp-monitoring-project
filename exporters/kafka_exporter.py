import time
import random
import math
from prometheus_client import start_http_server, Gauge, Counter

# Kafka Metrics
kafka_consumer_lag = Gauge('kafka_consumer_lag', 'Consumer lag per topic and group',
                           ['topic', 'consumer_group'])
kafka_broker_up = Gauge('kafka_broker_up', 'Kafka broker is up (1) or down (0)')
kafka_messages_in = Counter('kafka_messages_in_total', 'Total messages in per topic', ['topic'])
kafka_messages_out = Counter('kafka_messages_out_total', 'Total messages out per topic', ['topic'])
kafka_under_replicated = Gauge('kafka_under_replicated_partitions', 'Under-replicated partitions')
kafka_active_controller = Gauge('kafka_active_controller', 'Active controller count')

topics = ['transactions', 'events', 'logs', 'metrics']
consumer_groups = ['analytics-group', 'ml-pipeline', 'reporting']

def simulate_metrics():
    t = time.time()
    broker_up = True

    # Randomly simulate a broker failure every ~5 minutes for 30 seconds
    if int(t / 30) % 10 == 0 and int(t) % 30 < 15:
        broker_up = False

    kafka_broker_up.set(1 if broker_up else 0)
    kafka_active_controller.set(1 if broker_up else 0)

    for topic in topics:
        msgs = random.randint(50, 500)
        kafka_messages_in.labels(topic=topic).inc(msgs)
        kafka_messages_out.labels(topic=topic).inc(msgs - random.randint(0, 50))

        for group in consumer_groups:
            # Normal lag: 0-2000; spike every ~3 minutes to simulate anomaly
            base_lag = random.randint(100, 2000)
            if int(t / 180) % 3 == 0 and topic == 'transactions':
                base_lag = random.randint(8000, 20000)  # Spike for demo
            kafka_consumer_lag.labels(topic=topic, consumer_group=group).set(base_lag)

    # Random under-replication
    kafka_under_replicated.set(random.choices([0, 0, 0, random.randint(1, 5)], weights=[7, 1, 1, 1])[0])

if __name__ == '__main__':
    start_http_server(8001)
    print("Kafka exporter running on :8001")
    while True:
        simulate_metrics()
        time.sleep(15)
