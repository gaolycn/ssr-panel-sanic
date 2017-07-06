#ssr-panel-sanic
A shadowsocksR panel written in [Sanic](https://github.com/channelcat/sanic).

## Download

Please visit [releases pages](https://github.com/gaolycn/ssr-panel-sanic/releases) to download ssr-panel-sanic.

## Requirements

* Python 3.6
* MySQL

## Supported shadowsocks Server

* [shadowsocksR](https://github.com/shadowsocksr/shadowsocksr)


## Install

### Step 1

```
git clone https://github.com/gaolycn/ssr-panel-sanic.git
```

### Step 2

```
cp config.py.default config.py
```

then edit config.py


### Step 3

Import the SQL file to your MySQL database.

### Step 4

Nginx Config example:


```
server {
    listen      80;
    server_name .example.com;
    charset     utf-8;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
    
```

### Step 5 Run

```
python run.py
```
