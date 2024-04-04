# job story we are
# decrypting a pdf file
# upload pdfs based on data
# updating db
import asyncio
import sys
import time
import logging
from timeit import timeit

# from PySync.AsyncFusion import AsyncThread
from PySync.AsyncFusion_2 import AsyncProcess, AsyncCooroutine, AsyncThread
from PySync.Parallax import Process, Thread


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

@AsyncProcess(10)
def decrypt_pdf(i):
    # pdf_decryption_algorithm()
    time.sleep(1)
    logging.info(f"pdf {i} decryption complete")
    return i

@AsyncCooroutine()
async def upload_pdf_webservice(i):
    logging.info(f"pdf {i} webservice upload complete")
    await  asyncio.sleep(1)
    return i


@AsyncThread(10)
def db_write_data(i):
    logging.info(f"db {i} write complete")
    time.sleep(1)
    return i

@Process(10)
def call_in_process(work):
    tasks = []
    for i in work:
        tasks.append(decrypt_pdf(i)\
                .then(upload_pdf_webservice)\
                .then(db_write_data))
    for task in tasks:
        task.result()
    return i

def split(lst,n):
    return [lst[i:i + len(lst)//n] for i in range(0, len(lst), len(lst)//n)]

if __name__ == "__main__":
    # print("decrypt_pdf time taken: " , timeit("decrypt_pdf(1)", globals=globals(),number=1))
    # print("upload_pdf_webservice time taken: ",timeit("upload_pdf_webservice(1)", globals=globals(), number=1))
    # print("db_write_data time taken: ",timeit("db_write_data(1)", globals=globals(), number=1))

    # decrypt_pdf time taken:  1.0056909999984782
    # upload_pdf_webservice time taken:  1.0050583749980433
    # db_write_data time taken:  1.002689165998163
    start = time.time()

    tasks = []
    total_work = 10
    splitacross = 1

    work = [i for i in range(total_work)]
    total_work = split(work,splitacross)

    for part_work in total_work:
        tasks.append(call_in_process(part_work))

    for task in tasks:
        task.result()

    end = time.time()
    logging.critical(f"Total time taken : {end - start}")