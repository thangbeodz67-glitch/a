import threading
import time
import random
import logging
import networkx as nx

# Ghi log ra file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[logging.FileHandler("os_simulation.log", mode='w', encoding='utf-8')]
)

class BankerAlgorithm:
    def __init__(self, num_processes, num_resources, available, max_demand):
        self.num_processes = num_processes
        self.num_resources = num_resources
        self.available = list(available)
        self.max = [list(r) for r in max_demand]
        self.allocation = [[0] * num_resources for _ in range(num_processes)]
        self.need = [list(r) for r in max_demand]
        self.lock = threading.Lock()

    def is_safe_state(self):
        work = list(self.available)
        finish = [False] * self.num_processes
        safe_sequence = []
        while len(safe_sequence) < self.num_processes:
            found = False
            for p in range(self.num_processes):
                if not finish[p]:
                    if all(self.need[p][r] <= work[r] for r in range(self.num_resources)):
                        for r in range(self.num_resources):
                            work[r] += self.allocation[p][r]
                        finish[p] = True
                        safe_sequence.append(p)
                        found = True
                        break
            if not found: return False, []
        return True, safe_sequence

    def request_resources(self, process_id, request):
        with self.lock:
            if any(request[r] > self.need[process_id][r] for r in range(self.num_resources)):
                return False, "Error: Vượt quá Max"
            if any(request[r] > self.available[r] for r in range(self.num_resources)):
                return False, "Wait: Tài nguyên chưa đủ, phải đợi"
            for r in range(self.num_resources):
                self.available[r] -= request[r]
                self.allocation[process_id][r] += request[r]
                self.need[process_id][r] -= request[r]
            is_safe, _ = self.is_safe_state()
            if is_safe: return True, "Approved: Cấp phát thành công"
            for r in range(self.num_resources):
                self.available[r] += request[r]
                self.allocation[process_id][r] -= request[r]
                self.need[process_id][r] += request[r]
            return False, "Denied: Không an toàn (Unsafe State)"

    def release_resources(self, process_id):
        with self.lock:
            released = list(self.allocation[process_id])
            for r in range(self.num_resources):
                self.available[r] += self.allocation[process_id][r]
                self.allocation[process_id][r] = 0
                self.need[process_id][r] = list(self.max[process_id])[r]
            return released

def process_worker(p_id, banker, detector):
    logging.info(f"START: Tiến trình P{p_id} bắt đầu.")
    request = [random.randint(0, banker.need[p_id][r]) for r in range(banker.num_resources)]
    if sum(request) == 0: request[0] = 1
    logging.info(f"REQUEST: P{p_id} yêu cầu {request}")
    success, message = banker.request_resources(p_id, request)
    logging.info(f"BANKER RESPONSE to P{p_id}: {message} | Còn lại: {banker.available}")
    
    detector.graph.clear()
    for p in range(banker.num_processes):
        for r in range(banker.num_resources):
            if banker.allocation[p][r] > 0: detector.graph.add_edge(f"R{r}", f"P{p}")
            if banker.need[p][r] > 0 and banker.allocation[p][r] == 0: detector.graph.add_edge(f"P{p}", f"R{r}")
    try:
        cycle = nx.find_cycle(detector.graph)
        logging.error(f"DEADLOCK DETECTED bởi RAG! Chu trình: {cycle}")
    except nx.NetworkXNoCycle:
        logging.info("RAG CHECK: Không có deadlock.")

    if success:
        time.sleep(1)
        released = banker.release_resources(p_id)
        logging.info(f"RELEASE: P{p_id} trả tài nguyên {released}")

class DeadlockDetectorRAG:
    def __init__(self, num_processes, num_resources):
        self.graph = nx.DiGraph()

if __name__ == "__main__":
    logging.info("=== BẮT ĐẦU GIẢ LẬP OS ===")
    banker = BankerAlgorithm(3, 3, [3, 3, 2], [[7, 5, 3], [3, 2, 2], [9, 0, 2]])
    detector = DeadlockDetectorRAG(3, 3)
    threads = []
    for i in range(3):
        t = threading.Thread(target=process_worker, args=(i, banker, detector))
        threads.append(t)
        t.start()
        time.sleep(0.2)
    for t in threads: t.join()
    logging.info("=== KẾT THÚC GIẢ LẬP ===")