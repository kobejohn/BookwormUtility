=======================================
BookwormUtility - Whomp them every time
=======================================

.. image:: https://github.com/kobejohn/BookwormUtility/raw/master/docs/title_screen.png
   :width: 400 px

BookwormUtility (BU) works with the old (and good) game
`Bookworm Adventures <http://store.steampowered.com/app/3470/>`_.
It uses simple image recognition to extract the current game from the screen
and then simulates whichever game mode you are in (main game, or any of
the mini-games) to maximize score etc.

It doesn't just lookup words, it also identifies the status (unusable, plague,
diamond, ruby, etc.) and maximizes the score based on all factors.

It does not collect any internal game data through hooks etc. so it still has
to work to figure out possibilities.

Demo:
=====

All the work was worth the sweet sweet revenge of "Whomped!" and
"Annihilated!" etc. every time. You can basically win the game without
losing once.

Here is the post-game boss arena attempted with no potions. Almost made it.
If you use potions, it's ridiculously easy.

.. image:: https://github.com/kobejohn/BookwormUtility/raw/master/docs/battle.png
   :target: http://youtu.be/Y6AzpKn7jTc

Here is the mini-game Word Master. If I remember correctly, it can also handle
the other mini-games.

.. image:: https://github.com/kobejohn/BookwormUtility/raw/master/docs/word_master.png
   :target: http://youtu.be/YI7ZEUeZG98

Background and Feedback:
========================

Basically the game beat me up and this is my revenge.

This is one of the first projects I ever developed and so.... you really
probably shouldn't go look at the code. I'm too afraid to look. I'm just
sharing this for yuks and in case anyone can make use of some parts of it.

Setup and Run:
==============

Get this repository

- [git for windows](https://git-scm.com/download/win) (add git commands to your path if it asks)
- Open git-bash or powershell or whatever you want to use and confirm you can get some output from the command `git`
- Go the directory where you want to put the repo. Probably something like `cd C:\Users\<your-account>`
- `git clone https://github.com/kobejohn/BookwormUtility.git` (clones the repository to your computer)
- `ls BookwormUtility` (check if you got the code etc. in the new directory)

Get python and dependencies

- [miniconda windows 64 bit](https://conda.io/miniconda.html) (this lets you manage python well on your PC - add conda commands to your path if it asks)
- Open git-bash or powershell or whatever you want to use and confirm you can get some output from the command `conda`
- We will just use the default python environment so you do not need to do anything like `conda env create ...` that you might see in the miniconda walkthrough.
- `pip install pywin32` (this lets us get screen grabs in windows. it has a common python installer so we use `pip`)
- `conda install opencv` (this lets us analyze screen grabs. it is more complicated to install so we use `conda`)

Run it (good luck)

- Run Bookworm Adventures in windowed mode
- `cd <wherever>\BookwormUtility`
- `python bookworm_utility.py`
- whenever there is a word grid or a mini-game screen, click the appropriate button to get an analysis
- confirm it is working by looking at the output in your terminal - you should see the correct tiles and statuses (smashed, locked, etc.)


License:
========

MIT. See LICENSE
