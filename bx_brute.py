import os
from itertools import repeat
from threading import Thread
from threading import Event
import time

from datetime import datetime
def log_str(logfile_name, string_to_log):
    with open(logfile_name, 'a') as f:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f.write(dt_string+': '+string_to_log+'\n')

logfile_name = 'LOG_milking.log'

def t_job(t_id, T_off_ev):
    for _ in repeat(0):
        failsafe_file_closing_flag = 1
        
        log_str(logfile_name, f'{t_id} Initiate priv-key generation \ verification')
        for k in range(0, 100):
            for i in range(0, 5_000): 
                os.system(f"./bx-linux-x64-qrcode_3_2 seed | ./bx-linux-x64-qrcode_3_2 ec-new >> privkeys_{t_id}.txt")
                
            with open('failsafe_MILK.txt', 'r') as f:
                failsafe_file_closing_flag = int(next(f))
                if failsafe_file_closing_flag:
                    log_str(logfile_name, f'{t_id} Finishing by failsafe')
                    break

                if T_off_ev.is_set():
                    log_str(logfile_name, f'{t_id} Finishing by event')
                    break
            
        os.system(f"./brainflayer/brainflayer -v -b ./040823BF.blf -i privkeys_{t_id}.txt -t priv -x")
        os.system(f"rm privkeys_{t_id}.txt")
        log_str(logfile_name, f'{t_id} ........ priv-key generation \ verification... DONE') 
        
        if T_off_ev.is_set() or failsafe_file_closing_flag:
            break
    
t_num = 4

t = [0] * t_num
T_off_ev = Event()
T_off_ev.clear()
with open('failsafe_MILK.txt', 'w') as f:
    f.write('%d' % 0)
    
for i in range(t_num):
    t[i] = Thread(target = t_job, args=(i, T_off_ev ))
    t[i].start()
    time.sleep(10)
    
cmd = ''
while cmd != 'exit':
    cmd = input("Enter exit to finish...")

print('Main stopping threads')
T_off_ev.set()

for i in range(t_num):
    t[i].join()
