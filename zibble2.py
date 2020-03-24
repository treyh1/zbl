import hashlib
import binascii
import glob
import operator
import re
import json
import os
import io
import sys
import argparse
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plot
from bs4 import BeautifulSoup
from evernote.api.client import EvernoteClient
from evernote.edam.type import ttypes
from operator import itemgetter

# This is all stuff that I will use further down in the script with the "run with evernote" option. 

parser = argparse.ArgumentParser()

parser.add_argument('--evernote', action='store_true')

parser.add_argument('--folder', dest="input_folder")

# Commenting this out because of the "Cooking Bug". Parent Notebook will now be hard-coded to equal the GUID of the Reading Notebook.

# parser.add_argument('--nbook', dest="target_notebook")

args = parser.parse_args()

# production auth_token

my_token = "S=s59:U=631887:E=17633b2baf8:C=16edc018b18:P=81:A=treyhoward123:V=2:H=822a572c24f95a9ef3d750c351ea1e77"

# production notestore url

my_store_URL = "https://www.evernote.com/shard/s59/notestore"

# This opens the input file and creates a BS object for the headers. 

class EDAMUserException(RuntimeError):
    def __init__(self, UserException):
        Errors.EDAMUserException = UserException

class EDAMNotFoundException(RuntimeError):
    def __init__(self, EDAMNotFoundException):
        Errors.EDAMNotFoundException = EDAMNotFoundException

def open_file(directory, file):

    # change the directory from the script's cwd to the directory specified in the run_script function and passed to open_file.

    os.chdir(directory)

    with open((file), encoding='utf-8') as input_data:
        global soup
        soup = BeautifulSoup(input_data)
        return soup

# Get all of the divs in the kindle output file which belong to headers.

def parse_headers(soup):
    global header_divs
    header_divs = []

    for header_div in soup.find_all(class_='noteHeading'):
        header_divs.append(header_div)
    
    return header_divs

# Get all of the divs in the kindle output file which belong to bodies. 

def parse_bodies(soup):
    global body_divs
    body_divs = []

    for body_div in soup.find_all('div', class_='noteText'):
        body_divs.append(body_div)
    
    return body_divs

# This function builds a list of dictionaries containing the header information for each note. 

def extract_headers(divs):
    
    global header_dict_list

    header_dict_list = []
    
    for id,div in enumerate(divs):
        header_dict = {}
        if div.find("span", class_="highlight_yellow"):
            header_dict['type'] = 'highlight'
        else:
            header_dict['type'] = 'note'

        header_dict['id'] = id
        
        def extract_header_stuff(div):

            div_text = div.get_text()
            page_search = re.search(r'Page\s(\d+)(\s)', div_text)
            loc_search = re.search(r'Location\s(\d+)', div_text)
            if page_search:
                page_no = page_search.group(1)
                header_dict['page_number'] = int(page_no)
            if loc_search:
                loc_no = loc_search.group(1)
                header_dict['location_number'] = int(loc_no)
                
        extract_header_stuff(div)

        #count_headers(div)
        
        header_dict_list.append(header_dict)

    return header_dict_list

# This function builds a list of dictionaries containing the body (actual note or highlight) for each note. 

def extract_body(divs):

    global body_dict_list
   
    body_dict_list = []

    for id, div in enumerate(divs):
        body_dict = {}
        
        body_dict['id'] = id
        
        def extract_content(div):

            div_text = div.get_text()

            clean_div_text = div_text.replace("&", "and")

            body_dict['content'] = clean_div_text

        extract_content(div)
        
        body_dict_list.append(body_dict)

    return body_dict_list
    
# This function will merge each head dictionary with its corresponding body dictionary, based on the id provided in the functions above. 

def merge_heads_with_bodies(header_dict_list, body_dict_list):

    sorting_key = operator.itemgetter('id')

    global headers

    headers = sorted(header_dict_list, key=sorting_key)

    bodies = sorted(body_dict_list, key=sorting_key)

    for head, body in zip(headers, bodies):
        head.update(body)

    return headers

# This function takes the contents of each dictionary in the list and writes them to a file. 

def dict_writer(dict_list, filename):
    with open('%s.txt' % filename, 'w') as f:
        for extract in dict_list:
            content = extract.get("content")
            loc_no = str(extract.get("location_number"))
            page_no = str(extract.get("page_number"))
            f.write("\n")
            f.write(content + " " + "(" + page_no + ", " + loc_no + ")" +"\n")
            f.write("\n")

# This function is only used in the run_with_evernote script.

def makeNote(authToken, noteStore, noteTitle, list_of_dicts):

    client = EvernoteClient(token=authToken, sandbox=False)

    noteStore = client.get_note_store()

    Errors = client.get_user_store()

    # This is the GUID for the "Reading" notebook in my Evernote account. I am hardcoding this because of a bug with the --nbook option that I have not been able to diagnose.

    Reading_guid = "ea612952-d3a5-4a39-862b-01190ba02e47"

    # open the image and take its md5_hash

    image = open('%s.png' % noteTitle, 'rb').read()
    md5 = hashlib.md5()
    md5.update(image)
    image_hash = md5.hexdigest()

    # Assign the image content, length, and hash to a Data object.

    data = ttypes.Data()
    data.size = len(image)
    data.bodyHash = image_hash
    data.body = image

    # Create a new resource to hold the image.

    resource = ttypes.Resource()
    resource.mime = 'image/png'
    resource.data = data

    # Create a resource list in which to put the resource created above.

    resource_list = []
    resource_list.append(resource)

    # Create note object

    readingNote = ttypes.Note()
    readingNote.title = noteTitle
    readingNote.notebookGuid = Reading_guid
    readingNote.resources = resource_list

    # Start filling in the note content, including a reference to the image that we added to the resources list above.

    nBody = '<?xml version="1.0" encoding="UTF-8"?>'
    nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    nBody += '<en-note>'
    nBody += '<pre>'

    for kindle_dict in list_of_dicts:

        #Check to see if the dictionary is a note. If it is, make it blue.

        if kindle_dict['type'] = 'note':
            row = str(kindle_dict.get("content")) + " " + "(" + str(kindle_dict.get("page_number")) + ", " + str(kindle_dict.get("location_number")) + ")" +"\n"
            nBody += '<p>'
            nBody += '<span style="--darkmode-color: rgb(206, 215, 255); --lightmode-color: rgb(4, 51, 255);" class="VXs25">'row'</span>'
            nBody += '</p>'
        else:
            row = str(kindle_dict.get("content")) + " " + "(" + str(kindle_dict.get("page_number")) + ", " + str(kindle_dict.get("location_number")) + ")" +"\n"
            nBody += '<p>'
            nBody += row
            nBody += '</p>'

    nBody += '<en-media type="image/png" hash="%s"/>' % image_hash

    nBody += '</pre>'
    nBody += '</en-note>'

    # Create the note object.

    readingNote.content = nBody

    ## Attempt to create note in Evernote account

    try:
        note = noteStore.createNote(authToken, readingNote)
        return note

    except EDAMUserException as edue:
        print ("EDAMUserException:", edue)
        return None

    except EDAMNotFoundException as ednfe:
        ## Parent Notebook GUID doesn't correspond to an actual notebook
        print ("EDAMNotFoundException: Invalid parent notebook GUID", ednfe)
        return None

def run_script():

    script = sys.argv[0]

    directory = args.input_folder

    for f in [f for f in os.listdir(directory) if f.endswith(".html")]:
        name = os.path.splitext(f)[0]
        open_file(directory, f)
        parse_headers(soup)
        parse_bodies(soup)
        extracted_heads = extract_headers(header_divs)
        extracted_bodies = extract_body(body_divs)
        heads_and_bodies = merge_heads_with_bodies(extracted_heads, extracted_bodies)
        dict_writer(heads_and_bodies, name)

# The script only calls this function when the --evernote option is supplied.

def run_with_evernote():

    script = sys.argv[0]

    directory = args.input_folder

    # parent_notebook = args.target_notebook

    for f in [f for f in os.listdir(directory) if f.endswith(".html")]:
        name = os.path.splitext(f)[0]
        open_file(directory, f)
        parse_headers(soup)
        parse_bodies(soup)
        extracted_heads = extract_headers(header_divs)
        extracted_bodies = extract_body(body_divs)
        heads_and_bodies = merge_heads_with_bodies(extracted_heads, extracted_bodies)
        make_ventile_view(heads_and_bodies, name)
        makeNote(my_token, my_store_URL, name, heads_and_bodies)

# This function generates the ventile_view bar graph using the product of merge_heads_with_bodies above. The input is the dict_list and the name of the note, 
# which comes from the file name. 

def make_ventile_view(dict_list, name):
    
    # The dict_list is the output of the merge_heads_with_bodies function, and needs to be called after this. 

    sorted_dicts = sorted(dict_list, key=itemgetter('location_number'), reverse=True)
    
    # grab the last dictionary from the sorted dictionary list. 

    last_dict = sorted_dicts[0]

    total_length = last_dict['location_number']

    # Divide the book length by 20. 

    ventile_length = total_length / 20

    # Round this number down.

    def round_down(n):
        return math.floor(n)

    rounded_ventile_length = round_down(ventile_length)

    # Create a dictionary for the end position of each ventile. 
    # This will be merged with the start positions later to create a dataframe of start and end positions for each ventile.

    end_positions = {}

    # the values for 1 through 19 are assigned dynamically based on the last_location of the preceding key-value in the dictionary. 

    for x in range (1,20):
        end_positions[x] = x * rounded_ventile_length
        
    # Manually enter the end_position of the last ventile as the total length of the book. 
        
    end_positions[20] = total_length

    # Create a dictionary for the start positions

    start_positions = {}

    # Starting position of the first ventile will always be 1. 

    start_positions[1] = 1

    # For ventiles 2-20, the start position will be the end position of the preceding ventile + 1. 

    for x in range (2,21):
        start_positions[x] = (end_positions[x-1] + 1)
        
    # Merge the start_positions and end_positions together to make the "ventile_frame"
    # This will contain the starting and ending positions for each ventile, and the count of notes for each one across the whole book. 

    ventile_frame = pd.DataFrame({'start':pd.Series(start_positions),'end':pd.Series(end_positions)})

    # make a 0-value note_count column in the ventile_frame
    
    ventile_frame["note_count"] = 0
    
    for single_dict in dict_list:
        location_number = single_dict['location_number']
        ventile_frame["note_count"][(ventile_frame["start"] <= location_number) & (ventile_frame["end"] >= location_number)] += 1

    # Create the actual ventile view as a png. 

    ventile_frame.plot(kind='bar', y="note_count", legend=None)
    plot.savefig('%s.png' % name) 

if (args.evernote):
    run_with_evernote()

if (args.evernote is False):
    run_script()
