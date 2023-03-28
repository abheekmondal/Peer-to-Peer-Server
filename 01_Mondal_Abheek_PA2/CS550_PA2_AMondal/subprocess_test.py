import subprocess
import time
import random

def download_file(thread, index):
    start_time = time.time() # record start time
    thread.wait()
    end_time = time.time() # record end time
    with open(f"download_time_{index}.txt", "w") as f:
        f.write(str(end_time - start_time)) # write download time to file
    print(f"Thread {index} download complete.")

if __name__ == '__main__':
    files = ['32k.txt']
    n = 16
    threads = []
    start_time_all = time.time() # record start time for all threads
    with open("download_results.txt", "w") as f:
        for i in range(n):
            file = random.choice(files)
            time.sleep(0.05)
            if i < 2:
                choice = 2
            else:
                choice = random.randint(1, 2)
            thread = subprocess.Popen(args=['python', 'client.py', '--ip', '127.0.0.1', '--port', '8000', '-c', str(choice)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            thread.stdin.write(f"{file}\n".encode('utf-8'))
            thread.stdin.flush()
            threads.append(thread)
            
            # Record the chosen file and subprocess name to the download results file
            f.write(f"Process {i} downloaded file {file}\n")
    
        for i, thread in enumerate(threads):
            download_file(thread, i)
            
    end_time_all = time.time() # record end time for all threads
    total_time = end_time_all - start_time_all # calculate total time taken
    with open("total_download_time.txt", "w") as f:
        f.write(str(total_time)) # write total time to file
    
    print("All downloads complete.")
