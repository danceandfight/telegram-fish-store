# Бот-магазин для Telegram

Бот умеет показывать товары в продаже, их описания, добавлять (или убирать) эти товары в корзину, суммируя их количество и цену и запрашивать имейл для выставления счета.
Пример бота-магазина для [продажи рыбы](https://t.me/fishfishfishbot)

## Как установить

**Важно!** Предварительно должен быть установлен python версии не выше 3.9.x.

Скачайте код:
```sh
git clone git@github.com:danceandfight/fish-store-bot.git
```

Перейдите в каталог проекта:
```sh
cd fish-store-bot
```
Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии. 

В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`

Установите зависимости в виртуальное окружение:
```sh
pip install -r requirements.txt
```

Зарегестрируйте нового бота с помощью `@BotFather` в телеграме. Вам потребуется его токен, который выдаст `@BotFather` после регистрации.

Зарегестрируйтесь и создайте новую базу данных [Redis](https://redis.io). Вам потребуются `host`, `port` и `password`.

Создайте аккаунт в сервисе [ElasticPath](elasticpath.com), получите из него CLIENT_ID, CLIENT_SECRET и токен.

Создайте файл `.env` в каталоге `fish-store-bot/` и положите туда код такого вида, заменив токены на свои:
```sh
TELEGRAM_BOT_TOKEN=1234546789:ASFGRrogjRHrtweog-bRTHrhwmniireeoWW
REDIS_HOST='redis-18012.c293.eu-central-1-1.ec2.cloud.redislabs.com'
REDIS_PORT=18012
REDIS_PASSWORD='zMdDfsw243t0gkrsdmw32s0m03cmsamV'
CLIENT_ID=88f8wdcd3283f484nc429ncvt500rfhufhuw38392m
CLIENT_SECRET=6d7dfwn843mxyg5h,1234546789tnf3mccfhew
ELASTICPATH_TOKEN=ff8h8f38cng5mhecn4gm943xqh4w9t4q3pqhmrhx
```

## Как пользоваться

Создайте в Elasticpath товары в разделе `PRODUCT EXPERIENCE MANAGER`, затем Product book с ценами товаров, иерархию и каталог. В каталоге должны отобразится товары в статусе `Live`. 

Запустите telegram бота:

```sh
python fish_bot.py
```
Начните беседу, вызвав комманду `/start`

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).