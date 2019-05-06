# docker-redfin-scraper

To run scraper with outputs to logs:

```docker run --privileged -p 4000:4000 -d -it 15tuckerjo/docker-scraper```

To docker image with outputs to folder on host machine:

```docker run --privileged -p 4000:4000 -d -it -v $(pwd):PATH_TO_YOUR_FOLDER 15tuckerjo/docker-scraper```