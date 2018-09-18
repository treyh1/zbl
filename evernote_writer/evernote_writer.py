from evernote.api.client import EvernoteClient
from evernote.edam.type import ttypes

extract_list = [{"page_number":"120", "location_number":"6000", "content":"it's perfection was not lost on him."}, {"page_number":"145", "location_number":"10001", "content":"they rode on"}, {"page_number":"666", "location_number":"666000", "content":"For the earth is round like an egg, and all good things found within it"}]

my_token = "S=s1:U=94b3d:E=16b9b6772e4:C=16443b644c0:P=1cd:A=en-devtoken:V=2:H=749ed6e17600799426750a410c301b14"

my_store_URL = "https://sandbox.evernote.com/shard/s1/notestore"

my_title = "Blood Meridian2"

def makeNote(authToken, noteStore, noteTitle, list_of_dicts):

	client = EvernoteClient(token=authToken)

	noteStore = client.get_note_store()

	Errors = client.get_user_store()

	nBody = '<?xml version="1.0" encoding="UTF-8"?>'
	nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
	nBody += '<en-note>'
	nBody += '<pre>'

	for dict in list_of_dicts:
		nBody += '<ul>'
		ul = str(dict.get("content")) + " " + "(" + str(dict.get("page_number")) + ", " + str(dict.get("location_number")) + ")" +"\n"
		nBody += ul
		nBody += '</ul>'

	nBody += '</pre>'
	nBody += '</en-note>'

	## Create note

	readingNote = ttypes.Note()
	readingNote.title = noteTitle
	readingNote.content = nBody

	try:
		note = noteStore.createNote(authToken, readingNote)
		return note

	except Errors.EDAMUserException as edue:
		print ("EDAMUserException:", edue)
		return None

makeNote(my_token, my_store_URL , my_title, extract_list)