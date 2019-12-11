import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subprocess import call
import os

# This class watches the "watched" folder and waits for any folder that is added to the 

class Watcher:
    def __init__(self):

# Watch the sub-directory "input". This assumes that the script is being run in a parent "kndl" folder. 

        self.dir = os.path.abspath('input/')
        self.observer = Observer()
 
    def run(self):
        event_handler = Handler()

# Do not use the recursive option here. If you do, the watcher might start detecting events in the input/archive folder.

        self.observer.schedule(event_handler, self.dir)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")
 
        self.observer.join()

#The handler receives an event from the watcher and runs zibble2.py

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
 
# When a new file comes into the watched directory. 

        elif event.event_type == 'created':

            # Print that a file has been received.

            print("Received new zbl input file - %s." % event.src_path)

# Then run the ZBL command. The watched folder is the directory where new HTML files will arrive. Define the commadn first. 

            command = "python2.7 zibble2.py --evernote --folder input/"

# Run it as an external process. 

            call([command], shell=True)

# run path split to break this directory apart. 

            input_parts = os.path.split(event.src_path)

# The second part is the filename.

            file_name = input_parts[1]

# Move the file from the event source path to the input/archive directory.      

            os.rename(event.src_path, "input/archive/%s" % file_name)

if __name__ == '__main__':
    w = Watcher()
    w.run()