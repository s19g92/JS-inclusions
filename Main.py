#! /usr/bin/env python

import csv
import urllib2
import requests
import json
from bs4 import BeautifulSoup
from pprint import pprint
from collections import defaultdict


protocol = "http://"
base_wayback_uri = "https://archive.org/wayback/available?url="
stats = {}

#---------------- Fuction to read the CSV file with top sites ----------------
def csvreader():
    with open('top-1m.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            #Specify the number of sites to get data from           
            if line_count < 10000:
                print("Working on : " + row[1])
                getresponse(protocol + row[1],2018)
                years(row[1])
                line_count += 1

#---------------- Fuction to get HTTP response of the website ----------------
def getresponse(site,yr):
    try:
        response = requests.get(site)
        parse(response,yr)
    except: 
        print("Failed on : " + site)

#-------------- Fuction to get Parse the response for scripts  ---------------        
def parse(response,yr):
    soup = BeautifulSoup(response.text, "html.parser") 
    for script in soup.find_all("script"):
        if script:
            url = script.get("src")
            #Check if the url is not None
            if url:
                #Filter out url so that only external url are included
                if url.startswith(('http', 'ftp', 'www')):
                    if yr < 2018:
                        url = url.split("_/")[1]
                    if yr not in stats:
                        stats[yr] = {}
                    if url in stats:
                        stats[yr][url] += 1
                    else:
                        stats[yr][url] = 1
                            
                        
#------------ Fuction to get Wayback machine URL for past years  ------------- 
def years(site):
    #Get the url's for the given site for all the years mentioned in the range.
    for i in range(2015,2018,1):
        request_url = base_wayback_uri + site + "&timestamp=" + str(i) + "0202000000" 
        try:
            response = requests.get(request_url)
            url = json.loads(response.text)["archived_snapshots"]["closest"]["url"]
            url = url.replace("/http://" ,"im_/http://")
            getresponse(url,i) 
        except: 
            print("Failed on : " + request_url)
  
                        
def main():
    csvreader()
    
    #Store the stats in csv file according to the year
    for yr, st in stats.items():
        with open('Stats_'+str(yr)+'.csv', 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in stats[yr].items():
                writer.writerow([key, value])
   
    pprint(stats)
            
if __name__ == "__main__":
    main()