scrape-virtual-seismic-atlas
============================

Created on Sat Apr 19 20:37:13 2014

This script will download images from the virtual seismic atlas (http://see-atlas.leeds.ac.uk:8080), 
then add a url and caption. This is designed to run on linux and requires
 the python module gdshortener and also the library imagemagick installed
  and in the system path.
 
How it works? Images and info are scraped from the main site then and images are downloaded to the 
current directory, but only if they do not alread exist. Shortened urls are registered and 
captions are appended to the image using calls to imagemagick on the command line. (This is because PIL wasn't working as desired.)

This is pre-alpha so beware. You may need to run it a few times to make sure all images are downloaded.

To run: python scrape_seismic_atlas.py

@author: wassname (located_at) wassname (dot) org
