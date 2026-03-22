# ChatGPTDialogs Extraction Flow

Коротко: репозиторий строится вокруг сохранения открытого ChatGPT HTML, извлечения JSON и регрессионных тестов на публичных fixture-файлах.

## Основной поток

1. Сохранить открытую страницу ChatGPT:

```bash
make capture-browser
```

2. Сохранить страницу и сразу получить JSON:

```bash
make capture-browser-extract
```

3. Открыть viewer для локальных JSON:

```bash
make serve-viewer
```

4. Прогнать регрессии экстрактора:

```bash
make test
```

## Основные файлы

- `scripts/capture_chatgpt_tab.sh`: macOS-скрипт захвата активной вкладки браузера
- `scripts/browser_eval.js`: JXA-мост для выполнения JavaScript в браузере
- `extract_chatgpt_html.py`: преобразует сохраненный HTML в JSON
- `tests/fixtures/html/`: публичные HTML-файлы для тестов
- `tests/fixtures/json/`: golden JSON для тестов
- `tests/fixtures/regressions/`: точечные regression-кейсы

## Каталоги данных

- `import/`: локальные HTML-файлы, созданные во время работы
- `import_json/`: локальные JSON-файлы, созданные во время работы
- `tests/fixtures/`: checked-in тестовый корпус

## Примечания

- Для работы на macOS нужны Automation permissions для управления браузером
- Поддерживаются `Safari`, `Google Chrome`, `Brave Browser`, `Chromium`
- Если ChatGPT не прогрузил весь диалог, увеличьте `MAX_SCROLLS` и `SCROLL_PAUSE`
- Если меняется DOM ChatGPT, сначала обновляй экстрактор, затем фиксируй новые fixtures и только после этого обновляй golden JSON
