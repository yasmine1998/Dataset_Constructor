from selenium import webdriver
from googletrans import Translator
import time
import urllib.request
import os
import cv2
import io
import sys
import numpy
import requests as req
from PIL import Image
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager


def dhash(image, hashSize=8):
	
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hashSize + 1, hashSize))
	
    diff = resized[:, 1:] > resized[:, :-1]
	
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])
	
	
def download(sub,destDir,lang,hashes):
    try:
        os.mkdir(destDir)
    except FileExistsError:
        pass
    count = 0
    error = 0
    
    print(lang+": \n")
    for i in tqdm(range(len(sub))):
        src = sub[i].get_attribute('src')
        try:
            if src != None:
                src  = str(src)
                if "http" in src:
                    h = dhash(numpy.array(Image.open(io.BytesIO(req.get(src).content))))
                else:
                    h = dhash(numpy.array(Image.open(io.BytesIO(src))))
    
                if h not in hashes:
                    hashes.add(h)
                    count+=1
                    imagePath = os.path.join(destDir,'image'+str(count)+lang+'.jpg')
                    urllib.request.urlretrieve(src, imagePath)
                
                #image = cv2.imread(imagePath)
                #h = dhash(image)
                #p = hashes.get(h, [])
                #p.append(imagePath)
                #hashes[h] = p
	        
            else:
                continue
        except:
            continue
    
    #for (h, hashedPaths) in hashes.items():
        #if len(hashedPaths) > 1:
            #for p in hashedPaths[1:]:
                #os.remove(p)
            
            

def download_pin(browser,searchName,count,totalImgs,destDir,hashes):
    link = 'https://id.pinterest.com/search/pins/?q=%s&rs=typed'%(searchName)
    browser.get(link)
    cln = []
   
    while True:
       
        elem = browser.find_elements_by_tag_name('img')
        for k in elem:
            try:
                if '75x75_RS' in k.get_attribute('src'):
                    k = k.get_attribute('src').replace('75x75_RS','originals')
                else:
                    k = k.get_attribute('src').replace('236x','originals')
                
                try:
                    h = dhash(numpy.array(Image.open(io.BytesIO(req.get(k).content))))
                    if h not in hashes:
                        hashes.add(h)
                        cln.append(k)
                        named = k.split('/')[-1]
                        count += 1
                        print('%s/%s : %s'%(count,totalImgs, named))
                        
                except:
                    pass
                if count >= totalImgs:
                    break
            except:
                print("\nCheck Your Connection, Try Again !")
                browser.quit()
                exit()
        if count >= totalImgs:
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
        imgs = req.get(k).content
    
        imagePath = os.path.join(destDir+"image"+str(i)+".jpg")
    
        with open(imagePath,'wb+') as p:
            p.write(imgs)
            p.close()
                    


searchName = input('What are you looking for?')
totalImgs = int(input('How many images do you want?'))
destDir = sys.argv[1]+searchName+'/'
langs = ["en","ja","zh-CN","ko"] #,"ja","zh-CN","ko","de","pt","ro","vi"
count = 0
hashes = set({})

translator = Translator()
opts=webdriver.ChromeOptions()
opts.headless=True
browser = webdriver.Chrome(ChromeDriverManager().install() ,options=opts)

for lang in langs:
    
    browser.get("https://www.google.com/?hl="+lang)
    search = browser.find_element_by_name("q")
    translation = translator.translate(searchName, dest=lang)
    search.send_keys(str(translation.text), Keys.ENTER)
    
    translation = translator.translate("Images", dest=lang)
    elem = browser.find_element_by_link_text(str(translation.text))
    elem.get_attribute("href")
    elem.click()

    value = 0
    sub = []
    while len(sub) < totalImgs :
        browser.execute_script("scrollBy("+ str(value) +",+1000);")
        value += 50
        time.sleep(1)
        elem1 = browser.find_element_by_id("islmp")
        sub += elem1.find_elements_by_tag_name("img")
    if  len(sub) - totalImgs > 0 :
        sub = sub[:totalImgs - len(sub)]
    
    download(sub,destDir,lang,hashes)
    count = len(os.listdir(destDir))
    if count >= totalImgs:
        break
  
if count < totalImgs:
    download_pin(browser,searchName,count,totalImgs,destDir,hashes)    

