# job story we are
# decrypting a pdf file
# upload pdfs based on data
# updating db
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from timeit import timeit

from PySync.Parallax import Process, Thread

class customer_exception_handler():
    def __init__(self, future):
        self.future = future
    def result(self):
        try:
            self.future.result()
        except Exception as ex:
            print(f"{ex}")
            return -1

def pdf_decryption_algorithm():
    for _ in range(10000):
        for _ in range(10000):
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
    logging.info(f"pdf {i} webservice upload complete")
    time.sleep(1)
    return i

def db_write_data(i):
    logging.info(f"db {i} write complete")
    time.sleep(1)
    return i


if __name__ == "__main__":
    # print("decrypt_pdf time taken: " , timeit("decrypt_pdf(1)", globals=globals(),number=1))
    # print("upload_pdf_webservice time taken: ",timeit("upload_pdf_webservice(1)", globals=globals(), number=1))
    # print("db_write_data time taken: ",timeit("db_write_data(1)", globals=globals(), number=1))

    # decrypt_pdf time taken:  1.0056909999984782
    # upload_pdf_webservice time taken:  1.0050583749980433
    # db_write_data time taken:  1.002689165998163
    start = time.time()

    tasks = []
    with ProcessPoolExecutor(10) as th:
        for i in range(10):
            tasks.append(th.submit(decrypt_pdf,i))
        for task in tasks:
            try:
                task.result()
            except Exception as ex:
                print(f"{ex}")


    tasks = []
    with ThreadPoolExecutor(10) as th:
        for i in range(10):
            tasks.append(th.submit(upload_pdf_webservice,i))
        for task in tasks:
            try:
                task.result()
            except Exception as ex:
                print(f"{ex}")


    tasks = []
    with ThreadPoolExecutor(10) as th:
        for i in range(10):
            tasks.append(th.submit(db_write_data,i))
        for task in tasks:
            try:
                task.result()
            except Exception as ex:
                print(f"{ex}")

    end = time.time()
    logging.critical(f"Total time taken : {end-start}")

