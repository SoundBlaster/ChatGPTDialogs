# ChatGPTDialogs Extraction Flow

Коротко: этот репозиторий отвечает за преобразование сохраненного ChatGPT HTML в нормализованный JSON и за регрессионные тесты на публичных fixture-файлах.

## Основной поток

1. Преобразовать сохраненную HTML-страницу в JSON:

```bash
python3 extract_chatgpt_html.py path/to/dialog.html -o path/to/dialog.json
```

2. Пакетно обработать локальные HTML-файлы из `import/`:

```bash
make extract-all
```

3. Прогнать регрессии экстрактора:

```bash
make test
```

4. Обнаружить общие префиксы и сгенерировать metadata для связей между диалогами:

```bash
make detect-lineage
```

Эта команда создает `import_json/lineage.json` с информацией о том, какие JSON-файлы являются продолжениями или ветвями друг друга. Используется для построения деревьев разговоров в ContextBuilder.

5. При необходимости сохранить открытую страницу из браузера в локальные runtime-каталоги:

```bash
make capture-browser
make capture-browser-extract
```

6. Открыть полученные JSON в репозитории `ContextBuilder`, указав ему директорию `import_json/` или другую директорию с совместимыми JSON-файлами.

## JSON-контракт

Экстрактор пишет файлы со стабильной верхнеуровневой формой:

- `title`
- `source_file`
- `message_count`
- `messages`

Каждое сообщение должно содержать:

- `role`
- `content`

Дополнительно могут присутствовать:

- `turn_id`
- `message_id`
- `source`

Именно этот файловый контракт должен читать `ContextBuilder`.

## Основные файлы

- `extract_chatgpt_html.py`: преобразует сохраненный HTML в JSON
- `tests/fixtures/html/`: публичные HTML-файлы для тестов
- `tests/fixtures/json/`: golden JSON для тестов
- `tests/fixtures/regressions/`: точечные regression-кейсы
- `scripts/capture_chatgpt_tab.sh`: локальный macOS-скрипт захвата активной вкладки браузера
- `scripts/browser_eval.js`: JXA-мост для выполнения JavaScript в браузере
- `scripts/detect_lineage.py`: обнаруживает общие prefixes и генерирует ContextBuilder-совместимые связи между диалогами

## Каталоги данных

- `import/`: локальные HTML-файлы, созданные во время работы
- `import_json/`: локальные JSON-файлы, созданные во время работы
- `tests/fixtures/`: checked-in тестовый корпус

## Примечания

- Для работы browser capture на macOS нужны Automation permissions для управления браузером
- Поддерживаются `Safari`, `Google Chrome`, `Brave Browser`, `Chromium`
- Если ChatGPT не прогрузил весь диалог, увеличьте `MAX_SCROLLS` и `SCROLL_PAUSE`
- Если меняется DOM ChatGPT, сначала обновляй экстрактор, затем фиксируй новые fixtures и только после этого обновляй golden JSON
