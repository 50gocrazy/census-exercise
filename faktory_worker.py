from faktory import Worker
import time
import logging
import pandas as pd
from scrape import process_row


def parse_job(filename, chunk_count):
    chunk = pd.read_csv(filename)
    new_df = chunk.apply(process_row, axis=1)

    output_filename = "output/output_" + str(chunk_count) + ".csv"
    new_df.to_csv(output_filename, header = True, mode="w")
    header = False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    w = Worker(queues=['default'], concurrency=1)
    w.register('parse_job', parse_job)
    w.run()