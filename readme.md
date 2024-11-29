
# Video Stream Black Frame Monitor


Video Stream Black Frame Monitor — це інструмент для моніторингу відеопотоків у реальному часі. Додаток дозволяє аналізувати відеопотоки на предмет чорних кадрів та надсилати сповіщення через Telegram, якщо умови порушуються.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Features

- **Аналіз відеопотоків:** Виявлення кадрів із високою концентрацією чорних пікселів.
- **Телеграм-сповіщення:** Інтеграція з Telegram Bot API для сповіщень.
- **Мультипотокова підтримка:** Підтримка аналізу кількох потоків одночасно.
- **Гнучке налаштування:** Користувачі можуть налаштовувати параметри аналізу, такі як пороги чорних пікселів та кількість кадрів.
- **Автоматичне перепідключення:** Додаток автоматично перепідключається до потоку у разі збоїв.

## Requirements

- **Python 3.7+**

### Python Libraries

- `aiogram`
- `opencv-python`
- `numpy`

## Installation

1. **Клонуйте репозиторій:**

    ```bash
    git clone https://github.com/Sadoharu/video-stream-black-frame-monitor.git
    cd video-stream-black-frame-monitor
    ```

2. **Створіть віртуальне середовище (опціонально):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
    ```

3. **Встановіть залежності:**

    ```bash
    pip install -r requirements.txt
    ```


## Configuration

Створіть файл `config.ini` у кореневій директорії. Нижче наведено приклад:

```ini
[TELEGRAM]
api_key = YOUR_TELEGRAM_BOT_API_KEY
chat_id = YOUR_TELEGRAM_CHAT_ID
reply_to_message_id = YOUR_REPLY_MESSAGE_ID
message_cooldown = 30  # Інтервал у секундах між повідомленнями

[STREAM1]
url = rtsp://example.com/stream1
name = Front Door Camera
black_pixel_threshold = 0.5
black_pixel_intensity_threshold = 20
consecutive_frame_threshold = 50

[STREAM2]
url = rtsp://example.com/stream2
name = Backyard Camera
black_pixel_threshold = 0.4
black_pixel_intensity_threshold = 15
consecutive_frame_threshold = 40
```

**Пояснення:**

- **[TELEGRAM]:**
  - `api_key`: Токен вашого Telegram-бота.
  - `chat_id`: ID чату або користувача, куди надсилаються повідомлення.
  - `reply_to_message_id`: ID повідомлення, на яке буде відповідь.
  - `message_cooldown`: Інтервал між сповіщеннями.

- **[STREAM1], [STREAM2]:**
  - `url`: URL відеопотоку.
  - `name`: Назва потоку.
  - `black_pixel_threshold`: Відсоток чорних пікселів, що викликає сповіщення.
  - `black_pixel_intensity_threshold`: Поріг яскравості для чорних пікселів.
  - `consecutive_frame_threshold`: Мінімальна кількість підряд кадрів із пороговим рівнем чорних пікселів.

## Usage

Запустіть скрипт:

```bash
python streamforge.py
```

Після запуску додаток почне моніторинг потоків, зазначених у `config.ini`.

## Logging

Усі події записуються у файл `script.log`. Він містить інформаційні повідомлення, попередження та помилки.

**Приклад логів:**

```
2024-11-29 12:00:00 - INFO - === Початок роботи скрипта ===
2024-11-29 12:00:0 - INFO -
####################################################################################
#   _____ _______ _____  ______          __  __ ______ ____  _____   _____ ______  #
#  / ____|__   __|  __ \|  ____|   /\   |  \/  |  ____/ __ \|  __ \ / ____|  ____| #
# | (___    | |  | |__) | |__     /  \  | \  / | |__ | |  | | |__) | |  __| |__    #
#  \___ \   | |  |  _  /|  __|   / /\ \ | |\/| |  __|| |  | |  _  /| | |_ |  __|   #
#  ____) |  | |  | | \ \| |____ / ____ \| |  | | |   | |__| | | \ \| |__| | |____  #
# |_____/  _|_|  |_|  \_\______/_/    \_\_|  |_|_|    \____/|_|  \_\\_____|______| #
# | |     | |                                                                      #
# | | __ _| |__                                                                    #
# | |/ _` | '_ \                                                                   #
# | | (_| | |_) |                                                                  #
# |_|\__,_|_.__/                                                                   #
#                                                                     made by dozai#
####################################################################################
2024-11-29 12:00:05 - INFO - Ініціалізація потоку: Front Door Camera, URL: rtsp://example.com/stream1
2024-11-29 12:00:06 - INFO - [Front Door Camera] Відеопотік успішно відкрито
```

## Contributing

Якщо ви хочете внести свій вклад у проект:

1. Форкніть репозиторій.
2. Створіть нову гілку:

    ```bash
    git checkout -b feature/NewFeature
    ```

3. Зробіть зміни та коміт:

    ```bash
    git commit -m "Додано нову функцію"
    ```

4. Запуште вашу гілку:

    ```bash
    git push origin feature/NewFeature
    ```

5. Створіть Pull Request.

## License

Цей проект ліцензовано за [MIT License](LICENSE).

## Author

**dozai**

- GitHub: [github.com/Sadoharu](https://github.com/Sadoharu)

---
