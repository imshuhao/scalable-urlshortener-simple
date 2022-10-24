from multiprocessing import Process
import random, string, subprocess, time

def run(num):
    for i in range(num):
        request=f"http://localhost:8080/000000000000000000000000000000000000000000000"
        # print(request)
        subprocess.call(["curl", "-X", "GET", request], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    num_process = 8
    num_connection = 4000
    process_pool = []
    for i in range(num_process):
        process_pool.append(Process(target=run, args=(num_connection//num_process,)))
    start = time.time()
    for i in range(num_process):
        process_pool[i].start()
    for i in range(num_process):
        process_pool[i].join()
    end = time.time()
    print(f"time: {end - start}")