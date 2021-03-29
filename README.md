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
1. build [RedisAI](https://github.com/RedisAI/RedisAI), [VecSim](https://github.com/RedisGears/VecSim) ([RedisGears](https://github.com/RedisGears/RedisGears) is included in VecSim)
2. ```redis-server --loadmodule ./redisai.so --loadmodule ./redisgears.so Plugin ./vector_similarity.so```
