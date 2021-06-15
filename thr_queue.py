''' thread interop '''
from threading import Thread
from queue import Queue
from random import randint
from time import sleep

MASTER_SLEEP = 0

def master_thread(thread_name,main_queue):
    ''' master thread '''
    global MASTER_SLEEP
    while True:
        MASTER_SLEEP = randint(0, 4)
        qsleep = MASTER_SLEEP
        queue.put(qsleep)
        print(f'MAIN THREAD {thread_name} SETS {MASTER_SLEEP} VALUE\n')
        sleep(6)

def slave_thread(num,main_queue):
    ''' slave thread '''
    while True:
        if MASTER_SLEEP>0:
            slp = 1 / randint(1, 10)
            qlocal = bool(queue.qsize()!=0)
            if qlocal:
                qlocal = queue.get()
                print(f'Thread #{num} wheenks and sleep {MASTER_SLEEP}+{slp:.4f} sec. QUEUE: {qlocal}\n')
                queue.task_done
            sleep(MASTER_SLEEP + slp)   
        else:
            print(f'Thread #{num} in zero throttling\n')
            sleep(1)

queue = Queue()

for num in range(3):
    t = Thread(target=slave_thread, args=(num,queue))
    t.start()

m = Thread(target=master_thread, args=('MASTER',queue))
m.start()
