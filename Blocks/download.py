from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.request
import requests as req
from tqdm import tqdm
from PIL import Image
import os
import sys
import cv2
import io




searchName = input('What are you looking for?')
totalImgs = int(input('How many images do you want?'))
destDir = sys.argv[1]+searchName+'/'

opts=webdriver.ChromeOptions()
opts.headless=True
link = 'https://id.pinterest.com/search/pins/?q=%s&rs=typed'%(searchName)
browser = webdriver.Chrome(ChromeDriverManager().install() ,options=opts)
browser.get(link)

alink = []
cln = []
i = 1
while True:
    elem = browser.find_elements_by_tag_name('img')

    for k in elem:
        try:
            if '75x75_RS' in k.get_attribute('src'):
                k = k.get_attribute('src').replace('75x75_RS','originals')
            else:
                k = k.get_attribute('src').replace('236x','originals')

            
            try:
                Image.open(io.BytesIO(req.get(k).content))
                if k not in alink:
                    print("enter if")
                    alink.append(k)
                    cln.append(k)
                    named = k.split('/')[-1]
                    print('%s/%s : %s'%(i,totalImgs, named))

                    i+=1
            except:
                pass
            if len(cln) >= totalImgs:
                break

        except:
            print("\nCheck Your Connection, Try Again !")
            browser.quit()
            exit()
    print(len(cln))
    if len(cln) >= totalImgs:
        print('\n')
        break
    else:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    
try:
    os.mkdir(destDir)
except FileExistsError:
    pass
    
for i in range(len(cln)):
    k = cln[i]
    rename = k.split('/')[-1]
    imgs = req.get(k).content
    
    imagePath = os.path.join(destDir+rename)
    
    with open(imagePath,'wb+') as p:
        p.write(imgs)
        p.close()
                    

