intro.py
========

Splits Tom Robinson's free BBC Introducing Mixtape download into separate mp3 files.

How?
----

- Install prerequisites:

        sudo pip install pydub
        sudo apt-get install libav-tools

- Download an episode from http://www.bbc.co.uk/programmes/p02nrw4q/episodes/downloads
- Split it:

        ./intro.py <filename>

- Or, automatically download the latest podcast from the BBC website, and split it, in one step:

        ./intro.py --latest

Why?
----

- So when you hear an interesting one, you can check your mp3 player and see who it is.
- So when you hear a boring one, you can skip it.
