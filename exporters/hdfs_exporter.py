import time
import random
from prometheus_client import start_http_server, Gauge, Counter

hdfs_disk_used_percent = Gauge('hdfs_disk_used_percent', 'HDFS disk usage percentage')
hdfs_disk_total_bytes = Gauge('hdfs_disk_total_bytes', 'Total HDFS disk space in bytes')
hdfs_disk_used_bytes = Gauge('hdfs_disk_used_bytes', 'Used HDFS disk space in bytes')
hdfs_datanode_up = Gauge('hdfs_datanode_up', 'HDFS DataNode up (1) or down (0)')
hdfs_blocks_total = Gauge('hdfs_blocks_total', 'Total HDFS blocks')
hdfs_blocks_under_replicated = Gauge('hdfs_blocks_under_replicated', 'Under-replicated HDFS blocks')
hdfs_files_total = Gauge('hdfs_files_total', 'Total files in HDFS')
hdfs_corrupt_blocks = Gauge('hdfs_corrupt_blocks', 'Corrupt HDFS blocks')

def simulate_metrics():
    t = time.time()

    total_bytes = 10 * 1024 * 1024 * 1024 * 1024  # 10 TB
    
    # Disk slowly fills up; simulate spike every ~6 minutes
    base_usage = 55.0 + (t % 600) / 600 * 10
    if int(t / 360) % 6 == 0 and int(t) % 360 < 60:
        base_usage = random.uniform(82, 91)  # High spike for alert
    
    hdfs_disk_total_bytes.set(total_bytes)
    hdfs_disk_used_bytes.set(total_bytes * base_usage / 100)
    hdfs_disk_used_percent.set(base_usage)
    
    # DataNode failure every ~7 minutes for 45 seconds
    if int(t / 420) % 7 == 0 and int(t) % 420 < 45:
        hdfs_datanode_up.set(0)
    else:
        hdfs_datanode_up.set(1)

    hdfs_blocks_total.set(random.randint(50000, 60000))
    
    # Under-replicated blocks spike when disk is high
    if base_usage > 80:
        hdfs_blocks_under_replicated.set(random.randint(150, 500))
    else:
        hdfs_blocks_under_replicated.set(random.randint(0, 20))
    
    hdfs_files_total.set(random.randint(10000, 15000))
    hdfs_corrupt_blocks.set(random.choices([0, 0, random.randint(1, 3)], weights=[8, 1, 1])[0])

if __name__ == '__main__':
    start_http_server(8003)
    print("HDFS exporter running on :8003")
    while True:
        simulate_metrics()
        time.sleep(15)
