from flask import Flask, request, send_from_directory
import json
import requests
import cv2
import numpy
from redis import Redis
import struct

app = Flask(__name__)
redis_client = Redis()

KEY_PREFIX = 'items:'
VECTOR_PREFIX = 'vector:'


@app.route('/items', methods=['POST'])
def create_item():
    vector = image_url_to_vector(request.json['imageUrl'])
    key = KEY_PREFIX + request.json['sku']

    if redis_client.exists(key):
        return f'{request.json["sku"]} already exists', 400

    redis_client.execute_command('HSET', key, 'sku', request.json['sku'], 'imageUrl', request.json['imageUrl'])
    redis_client.execute_command('RG.VEC_ADD', KEY_PREFIX + VECTOR_PREFIX + request.json['sku'], vector)

    return ''


IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224


def image_url_to_vector(image_url):
    image_bytes = bytearray(requests.get(image_url, stream=True).raw.read())
    image = cv2.imdecode(numpy.asarray(image_bytes, dtype='uint8'), cv2.IMREAD_COLOR)
    resized = (cv2.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT)) / 128) - 1
    resized_bytes = numpy.asarray(resized, dtype=numpy.float32).tobytes()

    load_model()

    raw = redis_client.execute_command(
        'AI.DAGRUN', '|>',
        'AI.TENSORSET', MODEL_INPUT, 'FLOAT', '1', IMAGE_WIDTH, IMAGE_HEIGHT, '3', 'BLOB', resized_bytes, '|>',
        'AI.MODELRUN', MODEL_KEY, 'INPUTS', MODEL_INPUT, 'OUTPUTS', MODEL_OUTPUT, '|>',
        'AI.TENSORGET', MODEL_OUTPUT, 'VALUES'
    )[2]

    return b''.join([struct.pack('f', float(a)) for a in raw])


MODEL_KEY = 'efficient'
MODEL_INPUT = 'x'
MODEL_OUTPUT = 'Identity'


def load_model():
    if redis_client.execute_command('TYPE', MODEL_KEY) == b'AI__MODEL':
        return

    redis_client.execute_command('AI.MODELSET', MODEL_KEY, 'TF', 'CPU', 'INPUTS', MODEL_INPUT,
                                 'OUTPUTS', MODEL_OUTPUT, 'BLOB', open('EfficientNetB0.pb', 'rb').read())


def get_request_similar_skus():
    vector = image_url_to_vector(request.args['imageUrl'])
    result = []
    for sku in redis_client.execute_command('RG.VEC_SIM', '5', vector)[0]:
        result.append({
            'sku': sku[0].decode()[len(KEY_PREFIX) + len(VECTOR_PREFIX):],
            'score': float(sku[1])
        })

    return result


@app.route('/similar-skus', methods=['GET'])
def get_similar_skus():
    return json.dumps({
        'similarSkus': get_request_similar_skus()
    })


@app.route('/similar-items', methods=['GET'])
def get_similar_items():
    items = get_request_similar_skus()
    for item in items:
        item['imageUrl'] = redis_client.hget(KEY_PREFIX + item['sku'], 'imageUrl').decode()

    return json.dumps({
        'similarItems': items
    })


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('./public/dist', path)
