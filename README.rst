========
Mr. Repo
========

-----------------------------------------
A simple repo management system
-----------------------------------------

:Author: Ryan McGowan
:Email: ryan@ryanmcg.com

Introduction
------------

Mr. Repo is a repo management script written in python. It's very simple.
Basically, it turns whatever directory *Mr. Repo* is initialized into a
configurable repository of Git repositories. It creates two files to keep track
of its state.

 *  A YAML file (``.mr_repo.yml``) which keeps extended information on
    repositories that may appear in the directory
 *  Another file, (``.this_repo``) file keeps track of what repositories are
    currently available in the directory

...but why?
~~~~~~~~~~~

I have have a repo folder on several of my computers. This folder contains
mostly Git repositories that I want to be avaialble on multiple computers. I use
Dropbox to sync lots of files between my computers, but not the repo folder for
several reasons. However, I still want to manage what I have in my repo folders
across my computers. So, I'll be syncing the ``.mr_repo.yml`` file with Dropbox
and letting *Mr. Repo* do the rest of the work.

Usage
-----

Run the ``init`` command to get to set up the two files by automatically
interpreting subdirectories. ::

    python mr_repo.py init [--clean]

The ``--clean`` option causes the ``init`` command create blank tracking files and to not automatically interpret subdirectories.

Once you have the files setup you can add and remove repos by their directory
names with the add and remove commands. ::

    python mr_repo.py add <repo/direcotry name>
    # Or to remove a repo
    python mr_repo.py rm <repo/direcotry name>

You can also automatically reinterpret the current directory with the ``update``
command. ::

    python mr_repo.py update

That's all the boring stuff. The part of *Mr. Repo* that's actually useful is
its ability to pull repos you've added from other places, but aren't available
in your current directory.

To determine what repos you have just use the ``list`` command. By default the
list command outputs a list of currently available repos. Using the ``-a`` flag
also displays information about unavailable repos (i.e. repos that are not
currently set up in the CWD). As you might expect the ``-n`` flag can be used to
display repos that are not currently available. ::

    python mr_repo.py list [-a | --all] [-n | --not-available]

Once you know what repos are or are not currently available you can
``get``/``unget`` them. ::

    python mr_repo.py get <not currently available repo name>
    python mr_repo.py unget [-f | --force] <currently available repo name>

The ``unget`` command removes the repo if all changes have been fully committed
and also updates the ``.this_repo`` file. In the case where a there are uncomitted
changes an error is thrown and the command fails. If the user wants to remove it
anyways then the user can add the ``-f`` flag to force the removal.
