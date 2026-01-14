"""
Module to handle the logging
"""
import logging
import logging.handlers
logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    "Logs/novo-new-be.log", maxBytes=(1048576*5), backupCount=7
)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())


suppress_loggers = [
    "pymongo",
    "motor",
    "kafka", "kafka.consumer",
    "boto", "botocore",
    "ocrmypdf",
    "PIL",
    "passlib",
    "python_multipart"
]

for name in suppress_loggers:
    lib_logger = logging.getLogger(name)
    lib_logger.propagate = False
    lib_logger.setLevel(logging.WARNING)