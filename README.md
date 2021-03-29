# similar-images

## API

### Create an item
POST /items
```json
{
  "imageUrl": "https://picsum.photos/1000.jpg",
  "sku": "SKU"
}
```

### Search similar items
GET /similar-items
```?imageUrl=https://picsum.photos/1000.jpg```

## Run

Web Client:
```bash
cd public
npm i
npm run build 
```

Server:
```bash
pip3 install -r requirments.txt
export FLASK_APP=server.py
flask run
```

Redis:
1. build [RedisAI](https://github.com/RedisAI/RedisAI)
    1. clone the repository
    2. run `make`
    3. copy `./src/redisai.so`
2. build [RedisGears](https://github.com/RedisAI/RedisGears)
    1. clone the repository
    2. run `make`
    3. copy `./src/redisgears.so`
3. build [VecSim](https://github.com/RedisGears/VecSim)
    1. clone the repository
    2. open `./src/vector_similarity.c`
    3. change `#define VEC_SIZE` (line 20) value to `1280`
    4. change `#define VEC_HOLDER_SIZE` (line 22) value to `100 * 1024`
    5. run `make`
    6. copy `./src/vector_similarity.so`
4. run ```redis-server --loadmodule ./redisai.so --loadmodule ./redisgears.so Plugin ./vector_similarity.so```
