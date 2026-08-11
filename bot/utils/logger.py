import logging

info_handler = logging.FileHandler("bot.log")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

error_handler = logging.FileHandler("errors.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
))

logging.basicConfig(
    level=logging.INFO,
    handlers=[info_handler, error_handler,logging.StreamHandler()]
)