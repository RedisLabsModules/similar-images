
import argparse
import cv2
import redis
import time
import sys
import os
import numpy

try:
    import urllib.parse
except ImportError:
    import urllib.parse as urlparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='Input file (leave empty to use webcam)', nargs='?', type=str, default=None)
    parser.add_argument('-u', '--url', help='Redis URL', type=str, default='redis://localhost:6379')
    parser.add_argument('--fmt', help='Frame storage format', type=str, default='.jpg')
    args = parser.parse_args()

    # Set up Redis connection
    url = urllib.parse.urlparse(args.url)
    conn = redis.Redis(host=url.hostname, port=url.port)
    if not conn.ping():
        raise Exception('Redis unavailable')
    print('Connected to Redis')
    sys.stdout.flush()

    print('Verify model is lodead')
    sys.stdout.flush()
    model_type = conn.execute_command('type', 'efficient')
    if model_type != b'AI__MODEL':
        print('Loading model EfficientNetB0.pb')
        sys.stdout.flush()
        model = open('EfficientNetB0.pb', 'rb').read()
        conn.execute_command('AI.MODELSET', 'efficient', 'TF', 'CPU', 'INPUTS', 'x', 'OUTPUTS', 'Identity', 'BLOB', model)

    print('Loading file ', args.infile)
    sys.stdout.flush()

    img = cv2.imread(args.infile)
    newImg = (cv2.resize(img, (224, 224)) / 128) - 1
    l = numpy.asarray(newImg, dtype=numpy.float32)

    conn.execute_command('AI.TENSORSET', 'x', 'FLOAT', 1, 224, 224, 3, 'BLOB', l.tobytes())
    conn.execute_command('AI.MODELRUN', 'efficient', 'INPUTS', 'x', 'OUTPUTS', 'Identity')
    vector = conn.execute_command('AI.TENSORGET', 'Identity', 'VALUES')