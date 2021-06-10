#!/usr/bin/env python
import os
import subprocess
import socket
import time
import json

def filter_memcg_check():
   kswapd_info = dict()
   my_env = os.environ
   my_env["COLUMNS"]='200'
   
   subp = subprocess.Popen("top -d 2 -b -n 1 | grep memcg_docker | awk '{print $1, $12,$11}'",shell=True,stdout=subprocess.PIPE,env=my_env)

   subp.wait()
   top_data = subp.communicate()[0]
   kswapd_x = top_data.split("\n")

   #remove the last NULL item
   kswapd_x = kswapd_x[:-1]
   #print kswapd_x
   for kswapd_y in kswapd_x:
       kswapd_z = kswapd_y.split(" ")
       minutes, seconds = kswapd_z[2].split(":")
       total_secs = float(minutes)*60+float(seconds)
       info_key = kswapd_z[1].replace('[', "").replace(']',"")
       kswapd_info[(info_key, kswapd_z[0])] = total_secs * 60

   topoutput = os.popen("top -d 2 -b -n 1 | grep kswapd | awk '{print $1,$12,$11}'")
   top_data = topoutput.read()
   kswapd_x = top_data.split("\n")
   #print kswapd_x
   #remove the last NULL item
   kswapd_x=kswapd_x[:-1]
   #print kswapd_x
   for kswapd_y in kswapd_x:
       kswapd_z = kswapd_y.split(" ")
       minutes,seconds = kswapd_z[2].split(":")
       total_secs = float(minutes) * 60 + float(seconds)
       info_key = kswapd_z[1].replace('[', "").replace(']',"")
       kswapd_info[(info_key, kswapd_z[0])] = total_secs * 60

   return kswapd_info

if __name__ == "__main__":
    endpoint = socket.gethostname().split('.')[0]
    timestamp = int(time.time())
    upload_data = []
    memcg_info = filter_memcg_check()
    for key, val in memcg_info.items():
        dic_model =  {
        'endpoint': endpoint,
        'metric': 'kswapd.cpu.seconds.delta',
        'tags': 'thread=%s, pid=%s' % (key[0],key[1]),
        'timestamp': timestamp,
        'step': 60,
        'value': val,
        'counterType': 'COUNTER'
        }
        upload_data.append(dic_model)
    upload_data.append(dic_model)
    data = json.dumps(upload_data)
    print data

