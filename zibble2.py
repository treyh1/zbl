import glob
import operator
import re
import json
import os
import io
from bs4 import BeautifulSoup

# This opens the input file and creates a BS object for the headers. 

def open_file(file):
    with open((file), encoding='utf-8') as input_data:
        global soup
        soup = BeautifulSoup(input_data)
        return soup

def parse_headers(soup):
    global header_divs
    header_divs = []

    for header_div in soup.find_all('div', class_='noteHeading'):
        header_divs.append(header_div)
    
    return header_divs

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

def run_script():
    for each_file in sorted(glob.glob('**/*.html', recursive=True)):
        name = os.path.splitext(each_file)[0]
        open_file(each_file)
        parse_headers(soup)
        parse_bodies(soup)
        extracted_heads = extract_headers(header_divs)
        extracted_bodies = extract_body(body_divs)
        heads_and_bodies = merge_heads_with_bodies(extracted_heads, extracted_bodies)
        dict_writer(heads_and_bodies, name)


run_script()






