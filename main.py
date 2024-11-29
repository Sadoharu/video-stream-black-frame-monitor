import sys
import os
import asyncio
import cv2
import numpy as np
from aiogram import Bot
import time
import logging
import configparser
import threading
import io  # Для підтримки кодування в логуванні


def print_banner():
    banner = """
####################################################################################
#   _____ _______ _____  ______          __  __ ______ ____  _____   _____ ______  #
#  / ____|__   __|  __ \|  ____|   /\   |  \/  |  ____/ __ \|  __ \ / ____|  ____| #
# | (___    | |  | |__) | |__     /  \  | \  / | |__ | |  | | |__) | |  __| |__    #
#  \___ \   | |  |  _  /|  __|   / /\ \ | |\/| |  __|| |  | |  _  /| | |_ |  __|   #
#  ____) |  | |  | | \ \| |____ / ____ \| |  | | |   | |__| | | \ \| |__| | |____  #
# |_____/  _|_|  |_|  \_\______/_/    \_\_|  |_|_|    \____/|_|  \_\\\_____|______| #
# | |     | |                                                                      #
# | | __ _| |__                                                                    #
# | |/ _` | '_ \                                                                   #
# | | (_| | |_) |                                                                  #
# |_|\__,_|_.__/                                                                   #
#                                                                    made by dozai #
####################################################################################                      
"""
    logging.info(banner)

def main():
    # Визначаємо шлях до файлу конфігурації
    base_dir = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config.ini')
    
    # Шлях до ffmpeg.exe
    ffmpeg_path = os.path.join(base_dir, 'ffmpeg.exe')

    # Налаштування логування з підтримкою UTF-8
    stdout_handler = logging.StreamHandler(stream=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(base_dir, "script.log"), encoding='utf-8'),
            stdout_handler
        ]
    )
    logging.info("=== Початок роботи скрипта ===")
    print_banner()
    # Зчитування конфігураційного файлу з вказанням кодування
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')

    try:
        # Зчитуємо глобальні налаштування
        api_key = config['TELEGRAM']['api_key']
        chat_id = int(config['TELEGRAM']['chat_id'])
        reply_to_message_id = int(config['TELEGRAM']['reply_to_message_id'])
        message_cooldown = int(config['TELEGRAM'].get('message_cooldown', 30))

        # Ініціалізація Telegram-бота
        bot = Bot(token=api_key)

        # Створення списку потоків та черг
        threads = []
        message_tasks = []

        # Отримуємо всі секції, що починаються з 'STREAM'
        stream_sections = [section for section in config.sections() if section.startswith('STREAM')]
        if not stream_sections:
            logging.error("Не знайдено жодного потоку в конфігураційному файлі.")
            return

        # Створюємо подію для зупинки всіх потоків
        stop_event = threading.Event()

        # Отримуємо поточний цикл подій
        loop = asyncio.get_event_loop()

        # Для кожного потоку створюємо окремий потік та чергу
        for section in stream_sections:
            stream_url = config[section]['url']
            stream_name = config[section]['name']
            black_pixel_threshold = float(config[section]['black_pixel_threshold'])
            black_pixel_intensity_threshold = int(config[section].get('black_pixel_intensity_threshold', 20))
            consecutive_frame_threshold = int(config[section].get('consecutive_frame_threshold', 50))

            logging.info(f"Ініціалізація потоку: {stream_name}, URL: {stream_url}")

            # Створюємо асинхронну чергу для повідомлень
            message_queue = asyncio.Queue()

            # Запускаємо потік обробки відео
            thread = threading.Thread(target=process_video, args=(
                stream_url, stream_name, black_pixel_threshold,
                black_pixel_intensity_threshold, consecutive_frame_threshold,
                message_queue, loop, stop_event
            ))
            thread.start()
            threads.append(thread)

            # Запускаємо асинхронну задачу для відправки повідомлень
            message_task = loop.create_task(send_messages_per_stream(
                bot, chat_id, reply_to_message_id, message_queue, message_cooldown, stop_event, stream_name
            ))
            message_tasks.append(message_task)

        # Запускаємо цикл подій
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logging.info("Отримано сигнал завершення. Зупиняємо...")
            stop_event.set()
            for thread in threads:
                thread.join()
            for task in message_tasks:
                task.cancel()
                try:
                    loop.run_until_complete(task)
                except asyncio.CancelledError:
                    pass
        finally:
            loop.run_until_complete(bot.session.close())
            loop.stop()
            logging.info("=== Завершення роботи скрипта ===")
    except Exception as e:
        logging.error(f"Помилка при зчитуванні конфігураційного файлу: {e}")
        return
        

def process_video(stream_url, stream_name, black_pixel_threshold, black_pixel_intensity_threshold, consecutive_frame_threshold, message_queue, loop, stop_event):
    cap = None
    consecutive_black_frames = 0  # Лічильник підряд кадрів, що відповідають умовам
    while not stop_event.is_set():
        if cap is None or not cap.isOpened():
            logging.info(f"[{stream_name}] Спроба відкрити відеопотік...")
            cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                logging.error(f"[{stream_name}] Не вдалося відкрити відеопотік. Повторна спроба через 10 секунд.")
                time.sleep(10)
                continue
            else:
                logging.info(f"[{stream_name}] Відеопотік успішно відкрито")

        ret, frame = cap.read()
        if not ret:
            logging.warning(f"[{stream_name}] Не вдалося зчитати кадр. Перепідключення через 10 секунд.")
            cap.release()
            cap = None
            time.sleep(10)
            continue

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Використовуємо новий поріг яскравості для визначення чорних пікселів
        black_pixels = np.sum(gray_frame <= black_pixel_intensity_threshold)
        total_pixels = gray_frame.size
        black_ratio = black_pixels / total_pixels

        logging.debug(f"[{stream_name}] Відсоток чорних пікселів: {black_ratio * 100:.2f}%")

        if black_ratio >= black_pixel_threshold:
            consecutive_black_frames += 1
            logging.debug(f"[{stream_name}] Підряд кадрів, що відповідають умовам: {consecutive_black_frames}")
            if consecutive_black_frames >= consecutive_frame_threshold:
                message_text = f"⚠️ [{stream_name}] Виявлено {consecutive_black_frames} підряд кадрів з більше ніж {black_ratio * 100:.0f}% чорних пікселів!"
                # Додаємо повідомлення в асинхронну чергу
                asyncio.run_coroutine_threadsafe(message_queue.put(message_text), loop)
                consecutive_black_frames = 0  # Скидаємо лічильник після надсилання повідомлення
        else:
            if consecutive_black_frames > 0:
                logging.debug(f"[{stream_name}] Послідовність перервана. Скидання лічильника.")
            consecutive_black_frames = 0

        # Перевірка прапора зупинки
        if stop_event.is_set():
            break

    if cap is not None:
        cap.release()
    logging.info(f"[{stream_name}] === Завершення роботи відеопотоку ===")

async def send_messages_per_stream(bot, chat_id, reply_to_message_id, message_queue, message_cooldown, stop_event, stream_name):
    last_message_time = 0
    while not stop_event.is_set():
        try:
            message_text = await asyncio.wait_for(message_queue.get(), timeout=1)
        except asyncio.TimeoutError:
            continue

        current_time = time.time()
        if current_time - last_message_time >= message_cooldown:
            try:
                await bot.send_message(chat_id=chat_id, text=message_text, reply_to_message_id=reply_to_message_id)
                logging.info(f"[{stream_name}] Повідомлення успішно відправлено в Telegram")
                last_message_time = current_time
            except Exception as e:
                logging.error(f"[{stream_name}] Не вдалося відправити повідомлення в Telegram: {e}")
        else:
            logging.debug(f"[{stream_name}] Часовий інтервал між повідомленнями ще не минув. Повідомлення не відправлено.")
            


if __name__ == '__main__':
    main()
