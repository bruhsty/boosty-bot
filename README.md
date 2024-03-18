# Boosty bot

**Boosty bot** – это телеграмм-бот, позволяющий авторам на boosty создавать телеграмм каналы,
для подписчиков определенного уровня.

## Сборка и запуск

Первым делом для сборки проекта склонируйте репозиторий

```shell
git clone git@github.com:911enjoyers/boosty-bot.git
cd boosty-bot
```

### Docker compose

Для развертывания через docker-compose создайте файл `config/config.yaml`
со следующим содержимым

```yaml
env: prod

bot:
  token: "ЗДЕСЬ ВАШ ТОКЕН"
  updates: webhoook
  webhook:
    url: "ЗЕДСЬ ВАШ WEBHOOK URL"
    secret_token: 'СЕКРЕТНОЕ ЗНАЧЕНИЕ ДЛЯ ВЕБХУКА (ОПЦИОНАЛЬНО)'
    max_connections: 40
    host: localhost
    port: 8080

  polling:
    timeout: 10

smtp:
  host: "ВАШ SMTP ХОСТ"
  port: 465
  username: "АДРЕС ПОЧТЫ"
  password: "ПАРОЛЬ ОТ ПОЧТЫ"
  use_tls: true

boosty:
  refresh_token: 'REFRESH ТОКЕН BOOSTY'
  access_token: 'ACCESS ТОКЕН BOOSTY'
```

После этого вы можете запустить бота с помощью

```shell
docker-compose up -d
```

### Poetry

Установите зависимости.

```shell
poetry install
```

Создайте `config.yaml` с тем же содержимым и запустите бота.

```shell
poetry run python -m bruhsty --config config.yaml
```
