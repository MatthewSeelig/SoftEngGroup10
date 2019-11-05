import json
import re
import cmd
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import date
import os
from os.path import isfile, join, splitext
import string

""" Application to generate track recommendations from Spotify based that days news.
Extract terms from news source. Use those terms to get recommended tracks from Spotify (track of the day, alternative (i.e. opposite to terms gathered), etc."""

# Manually-defined exceptions
# Base class
class Error(Exception):
   """Base class for other exceptions"""
   pass

# Location value exception
class LocationValueError(Error):
   """Raised when location is set as anything other than an English-speaking country"""
   pass

def getArticles(location, articleAmt):

       # Stopwords and Punctuation
       stop = stopwords.words('english') + list(string.punctuation)

       # Build HTTP GET REQ
       url = 'https://newsapi.org/v2/top-headlines?country=' +  location
       headers = {
              "x-api-key": "f90d4db90b584cecbe463c68e3ec6fee",
       }

       #GET Response
       response = requests.get(url, headers=headers)
       print(response.status_code, response.reason)

       # Save response as JSON
       json_data = json.loads(response.text)

       # Build keywords from first 5 articles
       # Filter out title and desc from each article, tokenize desc and get keywords
       # Store title, desc and keywords in JSON format
       articles = {}
       for i in range(0, articleAmt):
              headline = str(json_data['articles'][i]['title'])
              description = str(json_data['articles'][i]['description'])

              if (headline.lower() == '' or headline.lower() == 'none') or (description.lower() == '' or description.lower() == 'none'):
                     continue
              
              # Tokenize headline and description
              tokenizedHeadline = word_tokenize(headline.lower())
              tokenizedDesc = word_tokenize(description.lower())
              tokenizedWords = tokenizedHeadline + tokenizedDesc

              # Unique words from tokenizedWords not in stop
              keywords = list(set([ word for word in tokenizedWords if not word in stop ]))

              articles[i] = {
                     'headline': headline,
                     'description': description,
                     'keywords': keywords
              }

       return articles

if __name__ == "__main__":
       # Download stopwords from NLTK and get stopwords + punctuation
       nltk.download('stopwords', quiet=True)
       nltk.download('punkt', quiet=True)
       
       directory = "articles"

       location = "gb"
       articleAmt = 5
       menu = {}
       menu['1']="Set location (default = gb)" 
       menu['2']="Set the amount of articles (default = 5)"
       menu['3']="Get Today's articles (Title, desc, keywords)"
       menu['4']="Show previously fetched articles"
       menu['5']="Exit"

       while True: 
              options=menu.keys()
              print("\n")
              for entry in options: 
                     print(entry, menu[entry])
       
              selection = input("Please Select: ") 
              
              if selection =='1': 
                     print("Please enter your location (Must be an english-speaking country ISO_3166-1)")
                     try: 
                            location = input("loc: ")
                            if location != "gb" and location != "us" and location != "ca" and location != "nz" and location != "au":
                                   raise LocationValueError
                     except LocationValueError:
                            print("\nProvided location is incorrect:", location, "\n\n")

              elif selection == '2': 
                     print ("Please enter the amount of articles you want to pull")
                     articleAmt = int(input("amount: "))

              elif selection == '3':
                     print ("\nGetting articles...\n")
                     articles = getArticles(location, articleAmt)
                     print(json.dumps(articles, indent=2))

                     # Make dir if not exist and save JSON to file
                     fileName = directory + "/" + date.today().strftime("%m-%d-%y") + ".json"
                     if not os.path.exists(directory):
                            os.makedirs(directory)
                     with open(fileName, 'w') as outfile:
                            json.dump(articles, outfile, indent=2)

              elif selection == '4':
                     #Gets filenames from articles directory
                     files = [os.path.splitext(f)[0] for f in os.listdir(directory) if isfile(join(directory, f))]
                     if not files:
                            print("\nThere are no previously fetched articles...")
                            print("Try fetching an article first!\n\n")
                            continue

                     submenu = {}
                     for i in range(0, len(files)):
                            submenu[i+1]= files[i]
                     
                     while True: 
                            options=submenu.keys()
                            for entry in options: 
                                   print(entry, submenu[entry])
                     
                            dateSelection = int(input("Please select a date: "))
                            fileName = directory + "/" + files[dateSelection - 1] + ".json"

                            print("\nYou have chosen to print articles from " + files[dateSelection - 1])
                            with open(fileName) as json_file:
                                   data = json.load(json_file)
                            print(json.dumps(data, indent=2))
                            break
                            

              elif selection == '5': 
                     break
              else: 
                     print("\nUnknown Option Selected!\n\n")
