#!/Users/myuser/anaconda/bin/python3
import urllib3
import urllib
import sys
import re
import os.path
import subprocess
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import requests
urllib3.disable_warnings()
if len(sys.argv) > 1:
  url=sys.argv[1]
else:
  print('You did not set an url')
  sys.exit()
website = urllib3.PoolManager()
proto = url.split('/')[0]
hostname = url.split('/')[2]

def download_no_hostname(myl2,iterator):
  totalfilesdled = 0
  if len(myl2) < 2:
    return(totalfilesdled)
  for url in myl2:
    filename = url.split('/')[-1]
    url = proto + '//' + hostname + url
    r = website.request('GET', url, preload_content=False)
    ro = requests.get(url)
    totalfilesdled = totalfilesdled + 1
    print("Downloading: " + filename + " Bytes: " + str(len(ro.content)) + " File #" + str(totalfilesdled) + " / " + str(iterator))
    file_size_dl=0
    chunk_size=16*1024
    if filename.endswith(".pdf"):
      print("filename ok")
    else:
      print("filename NOT ok")
      filename = filename.split('.pdf')[0]
    with open(filename, 'wb') as out:
        while True:
            data = r.read(chunk_size)
            if not data:
                break
            file_size_dl += len(data)
            out.write(data)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / len(ro.content))
            status = status + chr(8)*(len(status)+1)
            print("downloading " + filename + status + " File #" + str(totalfilesdled) + " / " + str(iterator) + " " + status)
    out.close()
    r.release_conn()
    print("DOWNLOADED " + filename + " File #" + str(totalfilesdled) + " / " + str(iterator))
    with open(hostname, 'r') as finsuivi:
      datasuivi=finsuivi.read().splitlines(True)
    with open(hostname, 'w') as fout:
      fout.writelines(datasuivi[1:])
  return(totalfilesdled)

def classic_download(myl3,totalfilesdled,iterator):
  for url2 in myl3:
    r2 = website.request('GET', url2, preload_content=False)
    filename2 = url2.split('/')[-1]
    ro2 = requests.get(url2)
    totalfilesdled = totalfilesdled + 1
    print("Downloading: " + filename2 + " Bytes: " + str(len(ro2.content)) + " File #" + str(totalfilesdled) + " / " + str(iterator))
    file_size_dl = 0
    chunk_size=16*1024
    if filename2.endswith(".pdf"):
      print("filename ok")
    else:
      print("filename NOT ok")
      filename2 = filename2.split('.pdf')[0]
      filename2 = filename2 + ".pdf"
    with open(filename2, 'wb') as out2:
        while True:
            data2 = r2.read(chunk_size)
            if not data2:
                break
            file_size_dl += len(data2)
            out2.write(data2)
            status2 = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / len(ro2.content))
            status2 = status2 + chr(8)*(len(status2)+1)
            print("downloading " + filename2 + " " + status2 + " File #" + str(totalfilesdled) + " / " + str(iterator) + " " + status2)
    out2.close()
    r2.release_conn()
    print("DOWNLOADED " + filename2 + " File #" + str(totalfilesdled) + " / " + str(iterator))
    with open(hostname, 'r') as finsuivi:
      datasuivi=finsuivi.read().splitlines(True)
    with open(hostname, 'w') as fout:
      fout.writelines(datasuivi[1:])

def url_preprocess(myl):
  print('WE DO URL PREPROCESS')
  myl2 = [s for s in myl if re.search('^(?!http|\.)', s)]
  myl3 = [s for s in myl if re.search('^http', s)]
  return(myl2,myl3)

def continue_on_errors(hostname):
  print('WE CONTINUE ON ERRORS')
  with open(hostname) as f:
    lines = f.read().splitlines()
  print(len(lines))
  myl2,myl3=url_preprocess(lines)
  print("there is still " + str(len(myl2 + myl3)) + " files remaining to download")
  iterator=len(myl2 + myl3)
  totalfilesdled=download_no_hostname(myl2,iterator)
  classic_download(myl3,totalfilesdled,iterator)
  sys.exit()

if os.path.isfile(hostname):
  conti = input("seems a previous download already exists, do you want to continue ?? (Yes / No) ")
  if conti =="Yes" or conti == "Y" or conti == "y" or conti == "yes" :
    print("OK SO WE DO NEXT STEP")
    continue_on_errors(hostname)
  else:
    print("OK GOODBYE")
    sys.exit()
else:
  retry=open(hostname,"w")

#retry.write("downloading of " + url + " is initialized")
response = website.request('GET', url)
soup = BeautifulSoup(response.data, "lxml")
myl = []
##GETTING ALL LINKS, ONLY THE HREF PART
for link in soup.find_all('a'):
    myl.append(link.get('href'))

print("PARSING DONE")
myl = list(filter(None.__ne__, myl))
myl = sorted(myl, key=str.lower)
myl = [s for s in myl if "pdf" in s]

myl2,myl3=url_preprocess(myl)

for item in myl2:
  retry.write("%s\n" % item)
for item in myl3:
  retry.write("%s\n" % item)

totalfilesfound = len(myl)
totalfilesdled = 0
print('there is ' + str(len(myl)) + ' files to download')
##DEBUG
#print(*myl3, sep='\n')
#print(*myl2, sep='\n')
totalfilesdled=download_no_hostname(myl2,totalfilesfound)
classic_download(myl3,totalfilesdled,totalfilesfound)

retry.close
