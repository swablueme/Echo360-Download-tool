import requests
import os.path
import json
import re
#import cookielib

#URL for echo
baseurl="https://echo360.org.au"

#list of subject names with which to name folders
subjectname=[]
#each section format follows the format /session/subjectID/syllabus where subjectID is a long string of letters and numbers
sectionurl= []
#cookies are required to make this script work but they never seem to expire once you've recorded them
#cookies begin with PLAY_SESSION=
available_cookie = []




#disable logging warnings so I can have Fiddler4 open when I run the script
requests.packages.urllib3.disable_warnings()

for idx, subject in enumerate(subjectname):
    print("%s in progress..." % subject)
    #header dict
    h={}
    #headers to add
    h['User-Agent']="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit \
    /537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    h['Host']="echo360.org.au"
    h['Cookie']= available_cookie[idx]
    
    
    #contains the list of lecture urls
    lecturelist=[]
    #contains a list of lecture dates to hopefully avoid downloading dupe lectures
    #it doesn't actually work because the second comp10001 lecture has an incremented date
    #and checking for this would probably break other subjects or miss advanced lectures
    nodupes_pls=[]

    #opens section url to obtain the json containing the video files
    s=requests.Session()
    s.headers.update(h)
    v=s.get('%s%s' % (baseurl,sectionurl[idx]), verify=False)
    #print(s.cookies)
    #break
    #open resulting json
    val = v.json()
    for i in range(len(val["data"])):
        datefor = val["data"][i]['lesson']['startTimeUTC']
        #make a nice looking date
        datefor = re.split("(?<=-[0-9]{2})T(?=[0-9]{2}:)", datefor)

        #add the url for lecture downloading to a list after checking if the date has already been downloaded
        if datefor[0] not in nodupes_pls:
            try:
                video = val["data"][i]['lesson']['video']['media']['media']['current']['primaryFiles'][1]['s3Url']
                nodupes_pls.append(datefor[0])
                lecturelist.append(video)
            except KeyError:
                pass

    #check if the subject folder exists if not make one
    if not os.path.exists('%s' % subject):
        os.mkdir('%s' % subject)

    #function downloads lectures and saves them in the folder of the subject name
    for i, lecture in enumerate(lecturelist):        
        if not os.path.exists(os.path.join('%s' % subject, nodupes_pls[i]+".mp4")):
            print("Downloading the lecture for %s"% nodupes_pls[i])
            h['Cookie']=""
            h['Accept']="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
            h['Accept-Encoding']="gzip,deflate,br"
            h['Accept-Language']="en-AU,en;q=0.9"
            h['Host']="content.echo360.org.au"
			
	    #deals with the cloudflair keypair nuisance
            for cookie in s.cookies:
                h['Cookie']+=cookie.name+'='+cookie.value+";"
            s.headers.update(h)
			
            v=s.get('%s' % lecturelist[i], verify=False, stream=True)

            with open(os.path.join('%s' % subject, nodupes_pls[i]+".mp4"),"wb") as nodupes_pls[i]:
				#avoids python eating up allllll the RAM
                for chunk in v.iter_content(chunk_size=1024):
                    if chunk:   
                        nodupes_pls[i].write(chunk)
        else:
            print("%s lecture file already exists so skipping!"% nodupes_pls[i])

