# job story we are
# decrypting a pdf file
# upload pdfs based on data
# updating db
import sys
import time
import logging
from timeit import timeit
from PySync.Parallax import Process, Thread
flag=False

def pdf_decryption_algorithm():
    for _ in range(10000):
        for _ in range(10000):
            pass

class customer_exception_handler():
    def __init__(self, future):
        self.future = future
    def result(self):
        try:
            self.future.result()
        except Exception as ex:
            print(f"{ex}")
            return -1

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

@Process(disable=flag,custom_proxy_handler=customer_exception_handler)
def decrypt_pdf(i):
    pdf_decryption_algorithm()
    logging.info(f"pdf {i} decryption complete")
    return i


@Thread(1000,disable=flag,custom_proxy_handler=customer_exception_handler)
def upload_pdf_webservice(i):
    logging.info(f"pdf {i} webservice upload complete")
    time.sleep(1)
    return i


@Thread(1000,disable=flag,custom_proxy_handler=customer_exception_handler)
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
    work_count = 1000
    tasks = []


    for i in range(work_count):
        tasks.append(decrypt_pdf(i))
    for task in tasks:
        task.result()

    tasks = []
    for i in range(work_count):
        upload_pdf_webservice(i)
    for task in tasks:
        task.result()

    tasks = []
    for i in range(work_count):
        db_write_data(i)
    for task in tasks:
        task.result()

    end = time.time()
    logging.critical(f"Total time taken : {end - start}")