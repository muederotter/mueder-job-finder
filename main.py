import logging

from app.model.model import Model
from app.view.view import View
from app.controller.controller import Controller
from app.logger import *
from app.config import DB_PATH

def main():
    
    # Set up logging
    setup_logger(logging.DEBUG)
    logger.info("Starting the tool")

    model = Model(DB_PATH)
    view = View()
    controller = Controller(model, view)

if __name__ == "__main__":
    main()
