# Для скачивания альбомов и файлов с нижеуказанных хостингов

## Поддерживает

- Bunkrr (bs4);
- CyberDrop (bs4 + api).

Для расширения достаточно добавить краулер в соответствующий пакет и указать его в модуле
factory.

## Запуск

Требуется [Python 3.11](https://www.python.org/), а для управления зависимостями
используется [poetry](https://python-poetry.org/).

Установка зависимостей:

```bash
poetry install  # из директории приложения
```

Запуск:

```bash
poetry run python -m simple_downloader [url] -p [save path]  # указание пути является опциональным
```

## Мысли на потом

- Конечно перенести на aiohttp;
- Дополнительный прогресс бар? (сейчас совсем неясно сколько ждать до завершения процесса, надо хотя
  бы представлять сколько файлов уже получено и сколько еще необходимо);
- Постоянные ReadTimeout при попытке отправить запрос на "bunkr.site", при этом сам ресурс прекрасно
  работает (?).

