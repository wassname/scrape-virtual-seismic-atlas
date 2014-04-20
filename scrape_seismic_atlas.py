
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 20:37:13 2014

@author: wassname
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

#print the list of image links
#print image_links


    
def wget(url,file_name=None):
    # not working
    '''http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python'''

    r = s.get(url) 
    if not file_name: file_name = r.raw.getheaders()['content-disposition'].split('=')[1]
    f = open(file_name, 'wb')
    #file_size = int(r.raw.getheaders()['content-length'])
    print "Downloading: %s" % (file_name)
    f.write(requests.get(url).content)    
    f.close()

def increase_last_char(c,inc=1):
    '''This increases the last charector on a string by 1, e.g. 09000064800112fc-> 09000064800112fd or 54 -> 55'''
    c=c[:-1]+chr(ord(c[-1])+inc)
    return c

#for image_link in image_links:
#    image_link2=increase_last_char(image_link['id'],inc=2) # this increases the last charector by 1
#    url=base_url+r'/docbaseContent?asAttachment=false&objectId={}&version=CURRENT&vs=1'.format(image_link2)
#    wget_with_progress_bar(url)
    
print "Finished scaping, qeueing {} image downloads".format(len(image_links))
    

   

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
    

# now download images, i have to iterate the last number or digit by 1! to get high res and 2 for low res!
# high res http://see-atlas.leeds.ac.uk:8080/docbaseContent?asAttachment=false&objectId=090000648001b0d3&version=CURRENT&vs=1
# lowres   http://see-atlas.leeds.ac.uk:8080/docbaseContent?asAttachment=false&objectId=090000648001b0d4&version=CURRENT&vs=1
# let us queue the downloads

if draft: image_links=image_links[:5]
#import tinyurl
import gdshortener
sg = gdshortener.ISGDShortener()
import Image
import ImageFont, ImageDraw
for image_link in image_links[46:]:
    image_link2=increase_last_char(image_link['id'],inc=inc) # this increases the last charector by 1
    url=base_url+r'/docbaseContent?asAttachment=false&objectId={}&version=CURRENT&vs=1'.format(image_link2)
    file_name = safe_filename(image_link['title'])+'.jpg'
    print "Download %s as %s" % (url, file_name)
    wget(url,file_name=file_name)

    # now do I also want to write on them?
    # the bastract is to long so just a tinyurl
    # first register tinyurl
    
    tnyurl=sg.shorten(url = base_url+image_link['href'])[0].replace('http://','')
    # http://stackoverflow.com/questions/245447/how-do-i-draw-text-at-an-angle-using-pythons-pil
    # now draw it on the image

    print "Drawing on image"
    
    # use python to draw an image, but it is overlayed and I cannot get the size right
#    im=Image.open(file_name)
#    
#    try:
#        f = ImageFont.truetype("usr/share/fonts/truetype/droid/DroidSansMono.ttf",15)
#        #"/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
#    except:
#        f = ImageFont.load_default()
#    
#    txt=Image.new('L', (130,int(15*1.3)),color=255)
#    d = ImageDraw.Draw(txt)
#    d.text( (0, 0), tnyurl,  font=f, fill=0)
#    #txt=txt.rotate(17.5,  expand=1)
#    im.paste( txt, (0,0))
#    im.save(file_name)

    # lets format the caption, we have to worry about escaping, and line wrapping
    import textwrap
    lwidth=140
    b=[]
    for line in image_link['abstract'].split('\n'):  # split it by existing line breaks to preserve them
        b=b+textwrap.wrap(line,width=lwidth) # wrap lines that are longer than width
    caption='link:'+tnyurl+'\n'+'\n'.join(b) # add it all together
    caption=caption.replace(':\n',':').replace('"','') # some formating and escaping
    
    b=textwrap.wrap(image_link['abstract'].strip().replace(u'\xa0', u' ').replace(':\n',':').replace('\n',',\t'),width=lwidth) # wrap lines that are longer than width
    caption='link:'+tnyurl+',\t'+'\n'.join(b) # add it all together
    caption=caption.replace('"','').expandtabs().decode('ascii',"ignore").encode('ascii','ignore') # some formating and escaping
    
    # now add a caption using imagemagik
    from subprocess import call 
    import subprocess
    #call(['convert', file_name   ,'-background','white',"label:{}".format(caption),'-gravity','Center','-append',file_name])
    
    # a 3rd way? http://stackoverflow.com/questions/4106200/overlaying-an-images-filename-using-imagemagick-or-similar
    #width=subprocess.check_output('img={}'.format(file_name)).strip() # set gilename in bash
    width=int(subprocess.check_output(['identify','-format','%W','"{}"'.format(file_name)]).strip())
    #call(['convert',
    #'-background white',
    #'-gravity center',
    #'-fill black',
    #'-size ${width}x100',
    #'caption:"{}"'.format(caption),
    #'"{}"'.format(file_name),
    #'+swap',
    #'-gravity south',
    #'-pointsize 24',
    #'-composite',
    #'"with-caption-{}" '.format(file_name)])
    #
    #call(['convert',
    #'"${img}"',
    #'-fill black',
    #'-undercolor',
    #'"#0008"',
    #'-pointsize 24',
    #'-gravity south',
    #'-annotate +0+5 "{}" '.format(caption),
    #'"with-annotate-${img}" '])
    
    # 3rd try is the charm, this actually uses fontsize yay
    call(['montage','-label', '"{}"'.format(caption),'-pointsize', '{}'.format(width/lwidth*4) ,'{}'.format(file_name),'-geometry +0+0 -background Gold','"with-montage-{}"'.format(file_name)])
    
    