import glob
import operator
import re
import json
from bs4 import BeautifulSoup

# This opens the input file and creates a BS object for the headers. 

def parse_headers():
    for filename in sorted(glob.glob('**/*.html', recursive=True)):
        try:
            with open((filename), encoding='utf-8') as input_file:
                global header_divs
                soup = BeautifulSoup(input_file)
                header_divs = soup.find_all('div', class_='noteHeading')
                return header_divs
                
        except IOError:
            print ('Unable to open file')

# This opens the input file and creates a BS object for the bodies. 

def parse_bodies():
    for filename in sorted(glob.glob('**/*.html', recursive=True)):
        try:
            with open((filename), encoding='utf-8') as input_file:
                global body_divs
                soup = BeautifulSoup(input_file)
                body_divs = soup.find_all('div', class_='noteText')
                return body_divs
                
        except IOError:
            print ('Unable to open file')


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

def dict_writer(dict_list):
	with open('output.txt', 'w') as f:
		for dict in dict_list:
			content = json.dumps(dict.get("content"))
			loc_no = json.dumps(dict.get("location_number"))
			page_no = json.dumps(dict.get("page_number"))
			f.write("\n")
			f.write(content + " " + "(" + page_no + ", " + loc_no + ")" +"\n")
			f.write("\n")

parse_headers()

parse_bodies()

extracted_heads = extract_headers(header_divs)

extracted_bodies = extract_body(body_divs)

heads_and_bodies = merge_heads_with_bodies(extracted_heads, extracted_bodies)

dict_writer(heads_and_bodies)






