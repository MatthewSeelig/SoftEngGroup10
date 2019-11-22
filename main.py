'''
Errors found:
403 Client Error: Forbidden for url
this happened becuase of the scope used when getting token
'''

import json
import sys
import re
import cmd
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import date
from os import makedirs, listdir
from os.path import isfile, join, splitext, exists
import string
import spotipy
import spotipy.util as util
import random
from random import randint
from random import seed

""" Application to generate track recommendations from Spotify based that days news.
Extract terms from news source. Use those terms to get recommended tracks from Spotify (track of the day, alternative (i.e. opposite to terms gathered), etc."""
## test id userId = '2146txyccmklgq5mvxgrawrzy'


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
              print(headline)
              description = str(json_data['articles'][i]['description'])
              print(description)
              ##if (headline.lower() == '' or headline.lower() == 'none') or (description.lower() == '' or description.lower() == 'none'):
              ##      continue
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

## ---- Keyword Functions ---- ##

## Gets all the keywords from a file

def getKeywordsFromFile(data):
   keywords = []
   for x in data:
      for y in data[x]['keywords']:
         keywords.append(y)
   return keywords

## Randomly chooses a keyword from all the keywords within the provided list of keywords

def getRandomKeyword(keywords):
   randomWordPostion = randint(0,(len(keywords)-1))
   randomWord = keywords[randomWordPostion]
   return randomWord

## This function takes in a word and searchs for a song on spotify

def searchForTrack(sp, keywords):
   currentWord = getRandomKeyword(keywords)
   results = sp.search(q=currentWord,limit=1, type='track')
   for x in results:
      if len(results[x]['items']) == 0:
         trackId = searchForTrack(sp, keywords)
         return trackId
      else:
         for y in results[x]['items']:
            return y['id']

## ---- Playlist Functions ---- ##

## Create playlist based on selected news
      
def createNewsPlaylist(userId, data, numberOfSongs, date):
   token = util.prompt_for_user_token(userId,scope='user-follow-read user-library-read user-read-private user-top-read playlist-modify-private playlist-modify-public playlist-read-collaborative user-modify-playback-state user-read-private user-library-modify user-follow-modify user-read-recently-played streaming user-read-currently-playing ',client_id='2ba5126fc467461c96850999a59925e0',client_secret='463773f5bf7b4e60b581d3d316abdde3',redirect_uri='http://google.com/')
   sp = spotipy.Spotify(auth=token)
   newsPlaylistTrackIds = []
   keywords = getKeywordsFromFile(data)
   for x in range(numberOfSongs):
      currentTrackId = searchForTrack(sp, keywords)
      newsPlaylistTrackIds.append(currentTrackId)
   print(newsPlaylistTrackIds)
   createPlaylistToken = util.prompt_for_user_token(userId, scope='playlist-modify-private playlist-modify-public',client_id='2ba5126fc467461c96850999a59925e0',client_secret='463773f5bf7b4e60b581d3d316abdde3',redirect_uri='http://google.com/')
   createPlaylist = spotipy.Spotify(auth=createPlaylistToken)
   playlistDescription = 'A playlist of songs based on the news on ' + date + '.'
   playlists = createPlaylist.user_playlist_create(userId, date, public=False,description=playlistDescription)
   newsPlaylist = sp.user_playlist_add_tracks(userId, playlists['id'], newsPlaylistTrackIds)

## ---- Main Software Loop ---- ##

if __name__ == "__main__":
       # Download stopwords from NLTK and get stopwords + punctuation
       nltk.download('stopwords', quiet=True)
       nltk.download('punkt', quiet=True)
       seed(1)
       
       directory = "articles"

       location = "gb"
       articleAmt = 5
       menu = {}
       menu['1']="Set location (default = gb)" 
       menu['2']="Set the amount of articles (default = 5)"
       menu['3']="Get Today's articles (Title, desc, keywords)"
       menu['4']="Show previously fetched articles"
       menu['5']="Create Playlist"
       menu['6']="Exit"

       menuCreatePlaylist = {}
       menuCreatePlaylist['1']="Create suggested playlist"
       menuCreatePlaylist['2']="Create playlist based on keywords from the news -- in dev --"
       menuCreatePlaylist['3']="Exit"

       userId = sys.argv[1]
       
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
                     if not exists(directory):
                            makedirs(directory)
                     with open(fileName, 'w') as outfile:
                            json.dump(articles, outfile, indent=2)

              elif selection == '4':
                     #Gets filenames from articles directory
					 #Sprint 3 1.3 & 4
					 #Previous days
                     files = [splitext(f)[0] for f in listdir(directory) if isfile(join(directory, f))]
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
                            print("\nWould you like to create a playlist from the keywords in these articles?")
                            print("\n1: Yes")
                            print("\n2: No")
                            userInput = input("\nPlease select: ")
                            if userInput == '1':
                               print('Please wait while we create your playlist...')
                               createNewsPlaylist(userId,data,25,files[dateSelection - 1])
                            break

              elif selection == '5':
                  userChoice=menuCreatePlaylist.keys()
                  print('\n')
                  for entry in userChoice:
                    print(entry, menuCreatePlaylist[entry])
                  userSelection = input('Please select: ')
                  if userSelection == '1':
                     ## Create suggested playlist
                     print('Please wait while we create your playlist...')
                     createSuggestedPlaylist(25, userId)
                  elif userSelection == '2':
                     ## Create news playlist
                     createNewsPlaylist(userId, data, 25, files[dateSelection - 1])
                  else:
                     print('\nUnknown option selected!\n\n')
              elif selection == '6': 
                     break
              else: 
                     print("\nUnknown Option Selected!\n\n")
