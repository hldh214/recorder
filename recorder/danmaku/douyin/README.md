## Douyin

### ws-server

Act as a websocket server, receive danmaku from a js-overridden douyin web page.
And then send the danmaku to MongoDB.

```js
// backup old one (if exists)
db.douyin_danmaku.renameCollection('douyin_danmaku_bak')

// create collection
db.createCollection('douyin_danmaku')

// add index
db.douyin_danmaku.createIndex({"msg_id": 1}, {unique: true})
```
