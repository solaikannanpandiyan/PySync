import concurrent.futures


def target_function(y):
    return y * y

def nested_worker_function(x):
    # This is the function executed by the nested ProcessPoolExecutor

    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = executor.submit(target_function, x)
        result = future.result()
        return result

def worker_function():
    # This is the function executed by the outer ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(nested_worker_function, i) for i in range(1, 6)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        return results

def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = executor.submit(worker_function)
        result = future.result()
        print("Final Result:", result)

if __name__ == "__main__":
    main()
