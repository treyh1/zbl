import glob
import operator
import re
import json
import os
import io
import sys
import argparse
from bs4 import BeautifulSoup
from evernote.api.client import EvernoteClient
from evernote.edam.type import ttypes

# This is all stuff that I will use further down in the script with the "run with evernote" option. 

parser = argparse.ArgumentParser()

parser.add_argument('--evernote', action='store_true')

parser.add_argument('--folder', dest="input_folder")

parser.add_argument('--nbook', dest="target_notebook")

args = parser.parse_args()

# production auth_token

my_token = "S=s59:U=631887:E=16e8977558b:C=16731c62728:P=81:A=treyhoward123:V=2:H=b0222222f593d83cd512b8febc68b69f"

# production notestore url

my_store_URL = "https://www.evernote.com/shard/s59/notestore"

# This opens the input file and creates a BS object for the headers. 

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

    for header_div in soup.find_all('div', class_='noteHeading'):
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

            body_dict['content'] = div_text

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

def makeNote(authToken, noteStore, noteTitle, list_of_dicts, parentNotebook):

    client = EvernoteClient(token=authToken, sandbox=False)

    noteStore = client.get_note_store()

    Errors = client.get_user_store()

    nBody = '<?xml version="1.0" encoding="UTF-8"?>'
    nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    nBody += '<en-note>'
    nBody += '<pre>'

    for dict in list_of_dicts:
        row = str(dict.get("content")) + " " + "(" + str(dict.get("page_number")) + ", " + str(dict.get("location_number")) + ")" +"\n"
        nBody += '<p>'
        nBody += row
        nBody += '</p>'

    nBody += '</pre>'
    nBody += '</en-note>'

    ## Create note object

    readingNote = ttypes.Note()
    readingNote.title = noteTitle
    readingNote.content = nBody

    # Added this code because I couldn't get the stuff on lines 196-97 working. 

    # readingNote.notebookGuid = parentNotebook

    # A new attempt to allow the user to match notebooks based on a name provided above. If this works, I will delete 187-191. 

    account_notebooks = noteStore.listNotebooks()

    for notebook in account_notebooks:
        try:
            notebook.name == parentNotebook
            readingNote.notebookGuid = notebook.guid
        except:
            print ("Notebook not found")

    ## parentNotebook is optional; if omitted, default notebook is used

    ## This bit of code below is not working, but was copied verbatim from the Evernote create note example.

    ##if parentNotebook and hasattr(parentNotebook, 'guid'):
        ##readingNote.notebookGuid = parentNotebook.guid

    ## Attempt to create note in Evernote account

    try:
        note = noteStore.createNote(authToken, readingNote)
        return note

    except Errors.EDAMUserException as edue:
        print ("EDAMUserException:", edue)
        return None

    except Errors.EDAMNotFoundException as ednfe:
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

    parent_notebook = args.target_notebook

    for f in [f for f in os.listdir(directory) if f.endswith(".html")]:
        name = os.path.splitext(f)[0]
        open_file(directory, f)
        parse_headers(soup)
        parse_bodies(soup)
        extracted_heads = extract_headers(header_divs)
        extracted_bodies = extract_body(body_divs)
        heads_and_bodies = merge_heads_with_bodies(extracted_heads, extracted_bodies)
        makeNote(my_token, my_store_URL, name, heads_and_bodies, parent_notebook)

if (args.evernote):
    run_with_evernote()

if (args.evernote is False):
    run_script()






