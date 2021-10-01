from Device import Arknights
import json
import time
import cv2
import os


port = 22823
a = Arknights(port, launch=False)

with open('coords.json') as f:
    coords = json.load(f)
crop = [0, 100, 10, 100]

def do_stage(stage):
    v=True
    try:
        a.compare_to('.cache/'+stage+'.jpg', 100, 1, crop=crop, verbose=v, timeout=60)
    except:
        a.bluestacks_tap(50,50,4)
        a.compare_to('.cache/'+stage+'.jpg', 100, 1, crop=crop, verbose=v, timeout=60)
    a.bluestacks_tap_rect(*coords['combat_start'])
    a.wait_for_changes(0, 2, verbose=v)
    a.bluestacks_tap_rect(*coords['mission_start'])
    time.sleep(20)
    a.wait_for_changes(100, 8, verbose=v)
    # arbitrary tap
    a.bluestacks_tap(50,50,4)
    time.sleep(3)
    
i = 1
stage='orirock'
x1, x2, y1, y2 = crop
cropped = a.screenshot('.cache/'+stage+'.jpg')[a.y*y1//100:a.y*y2//100, a.x*x1//100:a.x*x2//100]
cv2.imwrite('.cache/'+stage+'.jpg', cropped)

while True:
    do_stage(stage)
    print('run', i)
    i += 1
