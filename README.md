# mau-rss

Auto-generated RSS feeds hosted on GitHub Pages.

## Overview

This repository is a test project to generate RSS feeds for websites
that do not provide native RSS or Atom support.

The system works by:

1.  Fetching the HTML of a target webpage.
2.  Extracting article links based on simple matching rules.
3.  Generating a valid RSS XML file for each configured website.
4.  Publishing those feeds automatically via GitHub Pages.
5.  Updating both the feeds and the homepage automatically using GitHub
    Actions.

All feed files are generated under:

/feeds/<feed-id>.xml

They are publicly accessible at:

https://mauvera94.github.io/mau-rss/feeds/<feed-id>.xml

------------------------------------------------------------------------

## How It Works

### Configuration-Driven Feeds

All feeds are defined inside:

feeds.json

Each entry in the `feeds` array creates a separate RSS feed file.

Example:

{ “feeds”: \[ { “id”: “brian-all-recipes”, “title”: “Brian Lagerstrom —
All Recipes (Unofficial RSS)”, “source_url”:
“https://www.brianlagerstrom.com/recipes?category=All%20Recipes”,
“match_url_contains”: “brianlagerstrom.com/recipes/”, “max_items”: 50 }
\] }

### Fields Explained

-   id  
    Unique slug used as the output filename.  
    Generates: feeds/<id>.xml

-   title  
    The RSS feed title shown in RSS readers.

-   source_url  
    The webpage being monitored.

-   match_url_contains  
    A substring that must appear in a link URL to be included in the
    feed.  
    This helps filter out navigation links and unrelated URLs.

-   max_items  
    Maximum number of items included in the feed.

------------------------------------------------------------------------

## Adding a New Feed

To add a new website:

1.  Open feeds.json.
2.  Add a new object inside the feeds array.
3.  Commit the changes to the main branch.

Example:

{ “id”: “soyparrillero-recetas”, “title”: “Soy Parrillero — Recetas
(Unofficial RSS)”, “source_url”:
“https://soyparrillero.mx/blogs/recetas”, “match_url_contains”:
“soyparrillero.mx/blogs/recetas/”, “max_items”: 50 }

Once committed:

-   GitHub Actions runs automatically.
-   A new RSS file is generated.
-   The homepage (index.html) updates automatically.
-   The new feed becomes available at:

https://mauvera94.github.io/mau-rss/feeds/soyparrillero-recetas.xml

No additional code changes are required.

------------------------------------------------------------------------

## Automation

The workflow is defined in:

.github/workflows/build-feed.yml

It:

-   Runs on a schedule (hourly).
-   Can also be triggered manually.
-   Generates all feeds defined in feeds.json.
-   Updates index.html.
-   Commits changes back to the repository.

------------------------------------------------------------------------

## Homepage

The main page:

https://mauvera94.github.io/mau-rss/

is auto-generated during each workflow run. It lists all configured
feeds and updates automatically whenever a new feed is added.

------------------------------------------------------------------------

## Notes

-   This project is intended for websites without native RSS support.
-   It uses simple URL pattern matching to extract article links.
-   Some websites may require adjustment to the match_url_contains value
    if their structure changes.

------------------------------------------------------------------------

## Attribution

The feed generation logic, workflow configuration, and documentation in
this repository were created with assistance from ChatGPT.

