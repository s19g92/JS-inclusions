#! /usr/bin/env python

import csv
import urllib2
import argparse
import requests
import json
from bs4 import BeautifulSoup
from pprint import pprint
from collections import defaultdict

#Constant Literals
PROTOCOL = "http://"
BASE_WAYBACK_URI = "https://archive.org/wayback/available?url="
TIMESTAMP =  "0202000000" 

#Optional Parameters
INPUT_FILE = ''
START_RANK = 1
NUMBER_OF_SITES = 10
START_YEAR = 2015
END_YEAR = 2017

#Data stores
STATS = {}
SITES = {}

#Initialized values
SUCCESS_PAGES = 0
FAILED_PAGES = 0
CURRENT_YEAR = 2018
SAVE_AFTER = 200


#---------------- Fuction to read the CSV file with top sites ----------------
def csvreader():
    with open(INPUT_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:          
            if line_count < 10000:
                SITES[int(row[0])] = row[1]
                line_count +=1
    print("Reading File Complete ...")            

#---------------- Fuction to get HTTP response of the website ----------------
def getresponse(site,yr):
    global SUCCESS_PAGES
    global FAILED_PAGES
    try:
        response = requests.get(site)
        SUCCESS_PAGES += 1
        parse(response,yr)
    except: 
        FAILED_PAGES += 1
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
                    
                    #Save data after SAVE_AFTER number of pages
                    if SUCCESS_PAGES % SAVE_AFTER == 0:
                        store()

                    #If its url from wayback machine remove wayback url
                    if yr < CURRENT_YEAR:
                        url = url.split("_/")[1]
                        
                    #Add the data in STATS.    
                    if yr not in STATS:
                        STATS[yr] = {}
                    if url in STATS:
                        STATS[yr][url] += 1
                    else:
                        STATS[yr][url] = 1
                                                   
#------------ Fuction to get Wayback machine URL for past years  ------------- 
def getwayback(site):
    #Get the url's for the given site for all the years mentioned in the range.
    for i in range(START_YEAR,END_YEAR+1,1):
        print("Requesting year : " + str(i))
        request_url = BASE_WAYBACK_URI + site + "&timestamp=" + str(i) + TIMESTAMP
        try:
            response = requests.get(request_url)
            url = json.loads(response.text)["archived_snapshots"]["closest"]["url"]
            if url:
                url = url.replace("/http://" ,"im_/http://")
                getresponse(url,i)
            else:
                print("No archive for year : " + str(i))
        except: 
            print("Failed on : " + request_url)
  
#---------------- Fuction to iterate through requested sites  ----------------                       
def iterator():
    
    #Read the sites from input csv file
    csvreader()
    
    #iterate through the sites
    global NUMBER_OF_SITES
    for i in range(0,NUMBER_OF_SITES,1):
        print(i)
        print('Working on : Rank ' + str(START_RANK+i) + ' - ' + SITES[START_RANK+i])
        getresponse(PROTOCOL + SITES[START_RANK+i], CURRENT_YEAR) 
        getwayback(SITES[START_RANK+i])        
    
    #Save data finally
    print("SUCCESS_PAGES : " + str(SUCCESS_PAGES))
    print("FAILED_PAGES  : " + str(FAILED_PAGES))
    store()

#--------------- Fuction to store the sites data in csv files  ---------------    
def store():
    #Store the STATS in csv file according to the year
    for yr, st in STATS.items():
        with open('STATS_'+str(yr)+'.csv', 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in STATS[yr].items():
                writer.writerow([key, value])       

#------------ Fuction to parse the optional parameters at start  -------------                
def argparser():
    
    global INPUT_FILE
    global START_RANK
    global NUMBER_OF_SITES
    global START_YEAR
    global END_YEAR    
    
    #Provide with optional inputs parameters.
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--INPUT_FILE', type = str, help='Input csv file in (rank, site) format.', default = "top-1m.csv")
    parser.add_argument('-r', '--START_RANK', type = int, help='Rank at which to start data gathering. Default is 1.', default = 1)
    parser.add_argument('-c', '--NUMBER_OF_SITES', type = int, help='Number of sites. Default is 10. MAX = 10,000' , default = 10)
    parser.add_argument('-sy', '--START_YEAR',  type = int, help='Starting year for wayback machine. Default is 2015.', default = 2015)
    parser.add_argument('-fy', '--END_YEAR', type = int, help='Final year for wayback machine. Default is 2017.', default = 2017)                    
    args = parser.parse_args()
    
    INPUT_FILE = args.INPUT_FILE
    START_RANK = args.START_RANK
    NUMBER_OF_SITES = args.NUMBER_OF_SITES
    START_YEAR = args.START_YEAR
    END_YEAR = args.END_YEAR
    
    print("You are running the script with arguments: ")
    for a in args.__dict__:
        print(str(a) + " : " + str(args.__dict__[a]))  
  
if __name__ == "__main__":
    argparser()
    iterator()