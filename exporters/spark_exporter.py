import time
import random
from prometheus_client import start_http_server, Gauge, Counter

spark_active_tasks = Gauge('spark_active_tasks', 'Number of active Spark tasks')
spark_completed_tasks = Counter('spark_completed_tasks_total', 'Total completed tasks')
spark_failed_jobs = Counter('spark_job_failed_total', 'Total failed Spark jobs')
spark_memory_used = Gauge('spark_executor_memory_used_bytes', 'Memory used by executors')
spark_memory_total = Gauge('spark_executor_memory_total_bytes', 'Total executor memory')
spark_executor_count = Gauge('spark_executor_count', 'Number of active executors')
spark_stages_active = Gauge('spark_stages_active', 'Active stages')

def simulate_metrics():
    t = time.time()
    
    # Simulate job failure every ~4 minutes
    if int(t / 240) % 4 == 0 and int(t) % 240 < 30:
        spark_failed_jobs.inc(1)
        spark_active_tasks.set(0)
        spark_stages_active.set(0)
    else:
        active = random.randint(2, 10)
        spark_active_tasks.set(active)
        spark_completed_tasks.inc(random.randint(5, 20))
        spark_stages_active.set(random.randint(1, 4))

    spark_executor_count.set(random.randint(2, 8))
    
    # Memory usage: normal 50-70%, spike to 90%+ every ~5 min
    total_mem = 8 * 1024 * 1024 * 1024  # 8 GB
    if int(t / 300) % 5 == 0:
        used_mem = total_mem * random.uniform(0.88, 0.97)  # High spike
    else:
        used_mem = total_mem * random.uniform(0.4, 0.75)
    spark_memory_total.set(total_mem)
    spark_memory_used.set(used_mem)

if __name__ == '__main__':
    start_http_server(8002)
    print("Spark exporter running on :8002")
    while True:
        simulate_metrics()
        time.sleep(15)
