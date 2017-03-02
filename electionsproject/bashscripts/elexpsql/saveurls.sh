#!/bin/bash

## SET VARIABLES

URL_DOMAIN=http://127.0.0.1:8000

URL_PATH=/api/v1/resultlive/?format=json

## filters
PARTY_FILTER=party
## others here...

## abstract this?
DEM_URL="${URL_DOMAIN}${URL_PATH}&${PARTY_FILTER}=Dem"
GOP_URL="${URL_DOMAIN}${URL_PATH}&${PARTY_FILTER}=GOP"

if [[ MCCELECTIONSENV = local ]] ;  
	then
		## local path
		FULL_SAVE_PATH=/home/ubuntu/mccelections/electionsproject/static/resultlive
    else
    	## non-local path
		FULL_SAVE_PATH=/<YOUR>/<PATH>/mccelections/electionsproject/static/resultlive
fi


## array of URLs: need to figure out how to instantiate and add to this
# URLS=[]

## construct URls and add each to URLS array

## COMMANDS TO EXECUTE

## makes, if needed, and changes into save dir
# mkdir -p $FULL_SAVE_PATH
cd $FULL_SAVE_PATH

## option 1: listing each; eventually replace this with the loop
curl -O $GOP_URL
curl -O $DEM_URL

## option 2: loop through array of URLS
# for url in URLS
# do
# 	curl -O $url
# done

## option 3: I'd have to (dynamically, I presume) write all the specific URLs to a file
# wget -i /path/to/list.txt

## based on initial tests, this seems unnecessary
# FILES=$FULL_SAVE_PATH/*

# for file in $FILES
# do
# 	## rename files to remove index.html prefix
# done
