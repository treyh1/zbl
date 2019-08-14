import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import zibble2

# Define the handler class that receives files from the observer and actually executes commands on it. 

class HTML_Handler(PatternMatchingEventHandler):

# Watch for any new HTML files that are added to this folder. 

	patterns = ["*.html"]

	def process_htmls(self, event):

		# get the current working directory. it will be used in the command sent to zibble2.py

        cwd = os.getcwd()

		# We only care when new files come into the system (i.e., are created)

        event.event_type
            'created'

		# Not really sure what this does yet. 

		event.is_directory
			True

		# src_path attribute gives us the file name that we will feed into run_with_evernote.

		event.src_path
			path/to/observed/file

		# Excecute the ZBL command here. Note that I have not implemented the --file argument yet.  

		zibble2.run_with_evernote(event.src_path)

	def on_created(self, event):
		self.process_htmls(event)

# Schedule the observer that watches the folder, and passes new files to the HTML_Handler.

if __name__ == '__main__':

	# The folder that we are watching will be specified in the second argument when we start the kndl_watcher.

	args = sys.argv[1:]

	# Create a new instance of watchdog's Observer class. 

	observer = Observer()

	# Schedule the observer. 

	observer.schedule(HTML_Handler(), path=args[0] if args else '.')

	# Start the observer. Not sure exactly what this does.

	observer.start()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()

	observer.join()