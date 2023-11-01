AP parser
========================

This is a temporary workaround pending a new election rig. This script grabs available results from AP's API, downloads it as an XML, parses it, and outputs a cleaned json for our elex-rig to grab the data from.

The raw folder contains timestamped and latest XML. 

The data folder contains timestamped parsed JSON data and a `latest.json` that will always contain the most recent version.

A simpler method would be to parse the result as json to begin with. An AP API key is required for this.

