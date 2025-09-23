import logging
import colorlog

# Функция для настройки цветного логгера
def setup_logger(session, log_file):
    logger = logging.getLogger(session)
    logger.setLevel(logging.INFO)

    # Удаление старых обработчиков (если есть)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Создание формата для логов с вертикальной чертой
    log_format = "%(asctime)s | [%(levelname)s] | [%(threadName)s] | %(name)s | %(filename)s.%(funcName)s(%(lineno)d) | %(message)s"

    # Создание обработчика для вывода в файл
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    # Создание цветного обработчика для вывода в консоль
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        log_format,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        }
    ))
    logger.addHandler(console_handler)

    return logger
