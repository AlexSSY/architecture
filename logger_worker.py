import logging
import event


_logger = logging.getLogger('system')
_logger.setLevel(logging.INFO)


file_handler = logging.FileHandler('log.txt', mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)


if not _logger.handlers:
    _logger.addHandler(file_handler)


@event.subscribe('log')
async def log(data):
    msg = data['msg']
    _logger.info(msg)
