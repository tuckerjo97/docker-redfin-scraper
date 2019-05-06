# docker-redfin-scraper

To run scraper with outputs to logs:
'''docker run --privileged -p 4000:4000 -d -it selenium_docker'''

To docker image with outputs to folder on host machine:
'''docker run --privileged -p 4000:4000 -d -it -v $(pwd):PATH_TO_YOUR_FOLDER selenium_docker'''