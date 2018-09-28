import argparse

def print_evernote():
	print ("You have selected the evernote option.")

def print_text():
	print ("You have selected the text option.")

# Read the second entry in the command line argument (the script name is the first).

parser = argparse.ArgumentParser()

parser.add_argument('--evernote', action='store_true')

args = parser.parse_args()

if (args.evernote):
	print_evernote()

if (args.evernote is False):
	print_text()