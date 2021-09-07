# Senate Committee Video Scraper

## About

Surprisingly, there is not a central repository for past Senate Hearings across all committees. There are tables on each website for each individual
committee, but not one that contains all the hearings. This project intends to change that. By collecting links to all the videos for various hearings, 
it should make it easier to search for a given hearing vs navigating a given comittees website. 

Within `senateVideos`, there is a CSV file for each major Senate committee, along with `MasterFile.csv` which is a combination of all those other files.


## Requirements

A `requirments.txt` file is linked in the repository. While more then 3 packages are listed, the main 3 packages
to work with the scraper are:

* Beautiful Soup
* Pandas
* Requests

To run the scraper, the main method to get set up is to run `MergeSenateVideoFiles.py` which will run all the scrapers for the committees and then merge them into
a master CSV file.