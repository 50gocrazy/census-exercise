# Approach
I approached the assignment in Python (using the `pandas` and `BeautifulSoup` libraries), and used the `Faktory` background job server to operationalize the pipeline.

## Part 1: Parsing the required information for each row
I took a row-by-row approach to solving the problem.
First, I parsed each row into a `pandas` dataframe, and idenfied the carrier ID number (`DOT_NUMBER`). Then, I used the `BeautifulSoup` python package to scrape the requested information (`cargo carried` and `vehicle types`) from the DOT website.
Finally, I concatenated the results as to create a single row for each ID number. I decided to use a simple CSV structure given the time constraint of the exercise (3 hours), and the universality and ease of use of the format for prototyping.

## Part 2: Zooming out and orchestrating the pipeline
I used [`Faktory`](https://github.com/contribsys/faktory), an open-source, lightweight background job server processor. At a high level, Faktory consists of a `server`, a `client` and a `worker`. The
server runs the GUI and is the brain of the operation in terms of managing resources. The `client` queues jobs, which are executed by the `worker`. I chose to use Faktory because it has built-in retry
and job tracking capacities, is relatively lightweight to set up, and has a helpful GUI (and is free :) ). The retry capaccity is useful given that we know that the DOT website can be unreliable; if a
job fails, it will simply be queued to be retried later, hopefully when the website will be back up. In the `client`, I parse the original large CSV into smaller `intermediate` CSVs, so that the jobs can more easily
be decoupled into individual pieces of work (and could be paralellized using Faktory's built-in concurrency option), and to not take up a whole bunch of memory loading the huge original file each
time. Then, the `client` queues jobs on individual chunks for the `worker` to execute. 

After following the install steps, the Faktory GUI can be seen at `http://localhost:7420/`.

## Part 3: Improvements to make
I had only 3 hours to complete the assignment, and have left many things unfinished. In no particular order, here are examples of improvements that I would like to make, off the top of my head (in a
real scenario, I would also ask stakeholders for their inputs on this list):
- write tests! unit tests and integration tests. I can already spot a couple of data cleanliness issues (some of the added columns to each row have an empty entry instead of `FALSE` for example, and
  the columns are currently alphabetized but there is probably a more desired ordering)
- write more robust logging, at different levels (`INFO` for each job queued, more detailed `ERROR` messages)
- code style improvements: 
    - type hints for inputs and outputs
    - putting `scrape.py` into a `Scraper` class to  make the code more object-oriented, 
    - having a separate `CONSTANTS` files where the `CARGO_OPTIONS`, filenames, etc go
- deploy this pipeline into a cluster using e.g Kubernetes so that it does not run on someone's laptop

# Install Guide
## 1) Install requirements
### Installing Faktory:
on OSX, 
```
brew tap contribsys/faktory
brew install faktory
``` 
On other systems: [link](https://github.com/contribsys/faktory/wiki/Installation)
### Installing Python Dependencies
Recommended: create a Python virtual environment like so:
```
pyenv virtualenv 3.9.0 census-venv
pyenv activate census-venv
```
Installing dependencies:
```
pip install -r requirements.txt
```
## Run
You'll need 3 shell windows, located in the directory where you have cloned the project.
1) In one terminal, run `faktory`
2) In the second terminal, run `python faktory_client.py`
3) In the third terminal, run `run python faktory_worker.py`

Check the Faktory GUI: `http://localhost:7420/` . Output files will end up in the `output` directory. I left 1 file in the output as an example, as I did not have time to run the whole pipeline to completion.
