#!/usr/pkg/bin/python3.10

# Copyright (c) 2022 Ryo ONODERA <ryo@tetera.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Generate tiltles list from URLs and download movies with the title from TVer.jp
#
# Install:
# devel/py-requests
# net/yt-dlp
# security/py-cryptodome
# multimedia/ffmpeg5


import requests
import json
import time
import datetime
import urllib
import subprocess
import sys
import argparse
import pathlib


ytdlPath = 'yt-dlp'
maxFilenameLength = 84

tverVideoBase = 'https://tver.jp/episodes/'
tverApiServer = 'https://platform-api.tver.jp'

tverAccessTokensURL = tverApiServer + '/v2/api/platform_users/browser/create'
tverSearchURL = tverApiServer + '/service/api/v1/callSearch'

def getTverTokens():
  response = requests.post(tverAccessTokensURL, data='device_type=pc',
                           headers={'Content-Type': 'application/x-www-form-urlencoded'})

  return response.json()['result']


def getTverSearchResults(query):
  print("query:" + query)
  encodedQuery = urllib.parse.quote(query)
  accessTokens = getTverTokens()
  platformUid = accessTokens['platform_uid']
  platformToken = accessTokens['platform_token']
  searchURL = tverSearchURL + '?platform_uid=' + platformUid + \
              '&platform_token=' + platformToken + \
              '&require_data=later&keyword=' + encodedQuery

  response = requests.get(searchURL, headers={'x-tver-platform-type': 'web'})
  try:
    results = response.json()['result']['contents']
  except KeyError:
    time.sleep(5)
    response = requests.get(searchURL, headers={'x-tver-platform-type': 'web'})
    results = response.json()['result']['contents']

  return results


def getTverVideoURLs(query):
  URLs = []
  results = getTverSearchResults(query)
  for result in results:
    if query in result['content']['seriesTitle']:
      URLs.append(tverVideoBase + result['content']['id'])

  return URLs


def getVideoTitle(URL):
  episodeId = pathlib.PurePath(urllib.parse.urlparse(URL).path).name
  infoURL = 'https://statics.tver.jp/content/episode/' + episodeId + '.json'

  response = requests.get(infoURL)
  if response.status_code == requests.codes.ok:
    json = response.json()
    rawTitle = json['share']['text']
    title = rawTitle.replace('\n#TVer', '')

    return title
  else:
    return 'ERROR'


def writeTverTitles(URLsFilename, targetFilename):
  titles = []
  URL = []
  with open(URLsFilename, 'r') as file:
    URLs = file.read().splitlines()

  for URL in URLs:
    titles.append(getVideoTitle(URL))

  with open(targetFilename, 'w', encoding='utf-8', newline='\n') as tf:
    tf.write('\n'.join(titles) + '\n')

def getCommandResponse(command):
  return subprocess.Popen(command, stdout=subprocess.PIPE,
    shell=True).communicate()


def getCommandRetVal(command):
  return subprocess.Popen(command, stdout=None,
    shell=True).wait()


def downloadTverVideo(URL):
  command = ytdlPath + ' --get-filename ' + URL
  filenameBytes = getCommandResponse(command)[0].strip()
  trimmedFilenameBytes = filenameBytes[0:232]
  filenameShort = trimmedFilenameBytes.decode(encoding='utf-8', errors='ignore').replace('.mp4', '') + '.mp4'
  command = ytdlPath + ' --no-progress -o "' + filenameShort + '" --concurrent-fragments 3 ' + URL
  ret = getCommandRetVal(command)
  if ret == 0:
    return

  return

def downloadTverVideos(titleFilename):
  title = []
  with open(titleFilename, 'r') as file:
    titles = file.read().splitlines()
  for title in titles:
    print(title)
    URLs = getTverVideoURLs(title)
    for URL in URLs:
      print(URL)
      downloadTverVideo(URL)

if __name__ == '__main__':
  argParser = argparse.ArgumentParser(description='Get movie titles and download movies with the titles from TVer.jp')

  argParser.add_argument('--gentitle', help='Generate titles from URLs in GENTITLE file', action='store')
  argParser.add_argument('title_filename', help='Input titles file generated by --genfile option, in --gentitle case, this means output target filename', action='store')

  args = argParser.parse_args()

  if args.gentitle != None:
    writeTverTitles(args.gentitle, args.title_filename)
  else:
    downloadTverVideos(args.title_filename)
