=======================================
BookwormUtility - Whomp them every time
=======================================

BookwormUtility (BU) works with the old (and good) game `Bookworm Adventures <http://store.steampowered.com/app/3470/>`_
It uses simple image recognition to extract the current game from the screen
and then simulates whichever game mode you are in (main game, or any of
the mini-games) to maximize score etc.

It does not collect any internal game data through hooks etc. so it still has
to work to figure out possibilities.

Demo:
=====

All the work was worth the sweet sweet revenge of "Whomped!" and
"Annihilated!" etc. every time. You can basically win the game without
losing once.

.. youtube:: tbd

Background and Feedback:
========================

Basically the game beat me up and this is my revenge.

This is one of the first projects I ever developed and so.... you really
probably shouldn't go look at the code. I'm too afraid to look. I'm just
sharing this for yuks and in case anyone can make use of some parts of it.

Installation:
=============

Installation is ridiculous. I don't recommend it. Requires:

- Py3 (not Py2)
- windows (just because of the window grabbing technique)
- `PyWin32 <http://sourceforge.net/projects/pywin32/files/?source=navbar>`_ (for access to the screen)
- `OpenCV 1.0 <http://opencv.org/downloads.html>`_ (yes, 1.0) (with the /bin folder added to path)
- `ctypes-opencv <https://code.google.com/p/ctypes-opencv/>`_ (for Py3 access to OpenCV)
- make sure to set your environments TCL path to your Py3 TCL directory.
- probably there is more that I can't remember

License:
========

MIT. See LICENSE
