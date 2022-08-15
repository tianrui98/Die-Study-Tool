import logging

# import module
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
from datetime import datetime
# get named logger
logger = logging.getLogger(__name__)

# create handler
handler = TimedRotatingFileHandler(filename='log/activities.log', when='D', interval=1, backupCount=5, encoding='utf-8', delay=False)

# create formatter and add to handler
formatter = Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handler to named logger
logger.addHandler(handler)

# set the logger level
logger.setLevel(logging.DEBUG)

# version information
today = datetime.today().strftime("%Y%m%d")
logger.info(f"Version downloaded on {today}. Group branch.")