This program is used to add tags to files and folders on Dropbox, based on keywords found in the filenames.
Tags are searchable on the browser version of Dropbox and can be combined in one search using comma separators.

There are three categories of python scripts, one of which is used for running on personal folders, another which tags individual files and folders, and a third which tags all files and subfolders found within a matching folder.

Keywords and output tags can be edited in the top section. Multiple keywords can be included in an array.
Tags will be converted to all lower case and cannot contain any spaces.

To run a script, navigate to the relevant folder in your terminal and enter for example: 'py team_folder_tagging.py'.
The script will skip adding tags if they already exist on the match, and will report the number of new tags once it has finished running.
