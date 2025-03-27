# corekeeper_midi_to_instrument
A python script that will parse any midi file that you give it and generate an autohotkey script that can then be played in-game to play said song.

This is a work in project, very barebones version of what it will become in the future. Currently, You will have to have python installed, pip install the library I'm using to parse the midi files, and also download autohotkey. After all of that is complete, go into the midi_extraction_file.py and change the file_name = "your_song_name_here.mid". It will create an ahk file. Double click this file, go into corekeeper, pull up your instrument, and type ~. If you press esc then the autohotkey script will abort. 

All of this will change in the future, and I will add many more features into this script, including the hard coded hotkeys. Example midis and ahk files can also be found in the repository. 

Current feature wishlist:
 - separate instruments into separate midi files / give the user the option to select which instrument channels they want to include
 - process notes that are outside of the corekeeper's instrument note range, rather than just ignoring them
 - create a GUI for ease of use in the future, maybe through a godot .exe project

If you have any feedback or feature ideas for this project, message me through discord @legat45 or message me through the corekeeper official discord.

This github read.me and repo will become much better in the future, I just wanted to put this up for people who found it interesting / my friends.