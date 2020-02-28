import hashlib
import binascii
from evernote.api.client import EvernoteClient
from evernote.edam.type import ttypes

# production auth_token

my_token = "S=s59:U=631887:E=17633b2baf8:C=16edc018b18:P=81:A=treyhoward123:V=2:H=822a572c24f95a9ef3d750c351ea1e77"

# production notestore url

my_store_URL = "https://www.evernote.com/shard/s59/notestore"

def makeNote(authToken, noteStore):

    client = EvernoteClient(token=authToken, sandbox=False)

    noteStore = client.get_note_store()

    Errors = client.get_user_store()

    # This is the GUID for the "Reading" notebook in my Evernote account. I am hardcoding this because of a bug with the --nbook option that I have not been able to diagnose.

    Reading_guid = "ea612952-d3a5-4a39-862b-01190ba02e47"

    # Right now the image reference is hard-coded. I won't be able to do that in production (it will have to match the note title)

    # open the image and take its md5_hash

    image = open('kill_devil_hills.jpg', 'rb').read()
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
    resource.mime = 'image/jpg'
    resource.data = data

    # Create a resource list in which to put the resource created above.

    resource_list = []
    resource_list.append(resource)

    readingNote = ttypes.Note()
    readingNote.title = 'Kill Devil Hills'
    readingNote.notebookGuid = Reading_guid
    readingNote.resources = resource_list

    nBody = '<?xml version="1.0" encoding="UTF-8"?>'
    nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    nBody += '<en-note>'
    nBody += '<pre>'
    nBody += '<p>'
    nBody += 'A picture of the beach in Kill Devil Hills in winter.'
    nBody += '<en-media type="image/jpg" hash="%s"/>' % image_hash
    nBody += '</p>'
    nBody += '</pre>'
    nBody += '</en-note>'

    ## Create note object

    readingNote.content = nBody

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

makeNote(my_token, my_store_URL)