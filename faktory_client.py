import faktory
import time
import logging
import pandas as pd

with faktory.connection() as client:
    logging.basicConfig(level=logging.INFO)
    file = "input/input.txt"
    # cut original big csv into chunks
    intermediate_files = []
    with pd.read_csv(file, chunksize=100, sep=',', encoding= 'unicode_escape') as reader:
        count = 0
        for chunk in reader:
            intermediate_name = "intermediate/intermediate_" + str(count) + ".csv"
            intermediate_files.append(intermediate_name)
            chunk.to_csv(intermediate_name)
            count += 1

    # register a separate job in the queue for each chunk
    for i in range(len(intermediate_files)):
        filename = intermediate_files[i]
        
        client.queue('parse_job', args=[filename,i])

        # queue a new file every 30 seconds
        time.sleep(30)