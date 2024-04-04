# job story we are
# step 1: decrypting a pdf file
# step 2: upload pdfs through webservice
# step 3: updating db

import sys
import time
import logging
from timeit import timeit


def pdf_decryption_algorithm():
    for _ in range(1000_0):
        for _ in range(1000_0):
            pass

def log_initialize():
    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler('example.log')
    file_handler.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
log_initialize()
# logging.disable(logging.ERROR)

def decrypt_pdf(i):
    pdf_decryption_algorithm()
    logging.info(f"pdf {i} decryption complete")
    return i

def upload_pdf_webservice(i):
    time.sleep(1)
    logging.info(f"pdf {i} webservice upload complete")
    return i

def db_write_data(i):
    time.sleep(1)
    logging.info(f"db {i} write complete")
    return i


if __name__ == "__main__":
    # print("decrypt_pdf time taken: " , timeit("decrypt_pdf(1)", globals=globals(),number=1))
    # print("upload_pdf_webservice time taken: ",timeit("upload_pdf_webservice(1)", globals=globals(), number=1))
    # print("db_write_data time taken: ",timeit("db_write_data(1)", globals=globals(), number=1))

    # decrypt_pdf time taken:  1.0056909999984782
    # upload_pdf_webservice time taken:  1.0050583749980433
    # db_write_data time taken:  1.002689165998163

    start = time.time()
    for i in range(10):
        decrypt_pdf(i)
    for i in range(10):
        upload_pdf_webservice(i)
    for i in range(10):
        db_write_data(i)
    end = time.time()
    logging.critical(f"Total time taken : {end-start}")