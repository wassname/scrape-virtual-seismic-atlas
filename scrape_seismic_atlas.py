
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 20:37:13 2014

This script will download files from http://see-atlas.leeds.ac.uk:808, then append
 a url name and caption to them. This is designed to run on linux and requires 
 a few unique modules such as gdshortener and also imagemagik installed and in the path.
 
A few option are set in the file, base url, lim url, high res?, and draft?. 
Images and info is scraped from the main site and images are downloaded to the 
current directory, only if they do not alread exist.

Captions are appended to image using calls to imagemagik on the command line. This is because PIL wasn't worked as desired.

@author: wassname [located_at] wassname (dot) org
"""


#==============================================================================
# options
#==============================================================================
#the base URL we'll append the the 'limb' URL we'll find in the 'next' buttons
base_url = r'http://see-atlas.leeds.ac.uk:8080'
limb_url = r'/search/advancedSearch.jsp?rpp=50&Ns=P_LastModified%7c1&N=6394'
high_res=True
draft=False


#==============================================================================
# Main program
#==============================================================================
if high_res:
    inc=1
else:
    inc=2


#target=r'http://see-atlas.leeds.ac.uk:8080/search/advancedSearch.jsp?rpp=50&Ns=P_LastModified%7c1&N=6394' # adv search with 50 results per page
#exampleimage=r'http://see-atlas.leeds.ac.uk:8080/docbaseContent?objectId=09000064800112fe'

#make the required import
import bs4
import requests
import re
import gdshortener
from PIL import Image
import os
#create a session object that'll allow us to track the cookies across the session and raise
# too much suspicion
s = requests.session()
 

 
#a list to hold all the image URLs we'll find
image_links = []

 
# a few booleans to help our loop out
done = False

print "Scraping site:",base_url
#keep looping until we're 'done' which means that our 'next' button is leading us in circles
while not done:
    #combine base and limb URLs to create a full URL we can use
    url = base_url + limb_url
    #make the GET requests to the full URL we've just built
    r = s.get(url) 
    #create a BeautifulSoup Object that we can parse for data
    soup = bs4.BeautifulSoup(r.content)
    
    entity_divs=soup.findAll(attrs={'class': 'entity'})
    # first grab all the images on the page
    img_divs=soup.findAll(attrs={'class': 'result-thumbnail'})
    for entity_div in entity_divs:
        img_div=entity_div.findAll(attrs={'class': 'result-thumbnail'})[0]
        img_dic=img_div.a.attrs
        img_dic['id']=img_dic['href'].split('=')[1]
        img_dic['abstract']=re.sub(r'\s\s+',r'\n',entity_div.text) # here is the description to overlay on
        image_links.append(img_dic)
        print 'found:', img_dic['id'], img_dic['title'][:50] # max 50 chars in title
        
    #now see if we can find the next button
    next_found = False
    nxt_elems=soup.findAll(text='Next',attrs={'class':'paginate'})
    if nxt_elems:
        limb_url=nxt_elems[-1].attrs['href']
        print "Searching next page:", limb_url
        if draft: break
    else:
         done=True
    
print "Finished scaping, qeueing {} image downloads".format(len(image_links))

    
def wget(url,file_name=None):
    # not working
    '''http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python'''

    try:
        r = s.get(url) 
    except: # in case of "Max retries exceeded with url"
        s = requests.session()
        r = s.get(url) 
    try:
        image_name= r.raw.getheaders()['content-disposition'].split('=')[1]
    except:
        image_name='im.jpg'
    if file_name==None:
        file_name=image_name
    else:
        file_name=file_name+'.'+image_name.split('.')[1]
        
    f = open(file_name, 'wb')
    try:
        file_size = int(r.raw.getheaders()['content-length'])
        print "Downloading: %s (%s MB)" % (file_name,file_size*9.53674e-7)
    except:
        print "Downloading: %s" % (file_name)
    f.write(requests.get(url).content)    
    f.close()
    return file_name

def increase_last_char(c,inc=1):
    '''This increases the last charector on a string by 1, e.g. 09000064800112fc-> 09000064800112fd or 54 -> 55'''
    c=c[:-1]+chr(ord(c[-1])+inc)
    return c

   

def safe_filename(s):
    """"This will make a filename safe and nice. So remove invalid chars, as well as spaced for linux"""
    remove="""\\/:;*?"<>|%,#$!+{}[]'@`=&^"""
    replace=' ()'
    for c in remove:
        s=s.replace(c,'')
    for c in replace:
        s=s.replace(c,'_')
    s=s.lower()
    return s
    

# now download images,then write a caption under them
#  i have to iterate the last number or digit by 1! to get high res and 2 for low res!
# high res http://see-atlas.leeds.ac.uk:8080/docbaseContent?asAttachment=false&objectId=090000648001b0d3&version=CURRENT&vs=1
# lowres   http://see-atlas.leeds.ac.uk:8080/docbaseContent?asAttachment=false&objectId=090000648001b0d4&version=CURRENT&vs=1
# let us queue the downloads

if draft: image_links=image_links[:5]
sg = gdshortener.ISGDShortener()

for image_link in image_links:
    image_link2=increase_last_char(image_link['id'],inc=inc) # this increases the last charector by 1
    url=base_url+r'/docbaseContent?asAttachment=false&objectId={}&version=CURRENT&vs=1'.format(image_link2)
    file_name = safe_filename(image_link['title'])
    
    # check if its already there
    if os.path.isfile(file_name+'.jpg'):
        print "File already exists", file_name+'.jpg'
        continue

    print "Download %s as %s" % (url, file_name)
    file_name=wget(url,file_name=file_name) # download image


    # write caption under image
    # first register tinyurl
    tnyurl=sg.shorten(url = base_url+image_link['href'])[0].replace('http://','')

    print "Drawing on image"
    

    # lets format the caption, we have to worry about escaping, and line wrapping
    import textwrap
    lwidth=140
    b=[]
    for line in image_link['abstract'].split('\n'):  # split it by existing line breaks to preserve them
        b=b+textwrap.wrap(line,width=lwidth) # wrap lines that are longer than width
    caption='link:'+tnyurl+'\n'+'\n'.join(b) # add it all together
    caption=caption.replace(':\n',':').replace('"','') # some formating and escaping
    
    b=textwrap.wrap(image_link['abstract'].strip().replace(u'\xa0', u' ').replace(':\n',':').replace('\n',',\t'),width=lwidth) # wrap lines that are longer than width
    caption='link:'+tnyurl+',\n'+'\n'.join(b) # add it all together
    caption=caption.replace('"','').expandtabs().decode('ascii',"ignore").encode('ascii','ignore') # some formating and escaping
    
    # now write it using imagemagic
    # a 3rd way? http://stackoverflow.com/questions/4106200/overlaying-an-images-filename-using-imagemagick-or-similar
    try:
        img = Image.open(file_name)
    except:
        print "Could not open image", file_name
        continue
    width, height = img.size

    try:
        os.system(' '.join(['montage','-label', '"{}"'.format(caption),'"{}"'.format(file_name),'-pointsize', '{}'.format(int(width/lwidth*2)) ,'-geometry','+0+0','-background','White','"{}"'.format(file_name)]))
    except:
        print "Could not add caption to image", file_name, ' '.join(['montage','-label', '"{}"'.format(caption),'"{}"'.format(file_name),'-pointsize', '{}'.format(int(width/lwidth*2)) ,'-geometry','+0+0','-background','White','"{}"'.format(file_name)])
        continue
    
    