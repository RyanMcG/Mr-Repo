========
Mr. Repo
========
-------------------------------
A simple repo management system
-------------------------------

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
mostly Git repositories that I want to be available on multiple computers. I use
Dropbox to sync lots of files between my computers, but not the repo folder for
several reasons. However, I still want to manage what I have in my repo folders
across my computers. So, I'll be syncing the ``.mr_repo.yml`` file with Dropbox
and letting *Mr. Repo* do the rest of the work.

Running Mr. Repo / Installation
-------------------------------

Mr. Repo is available via pip. ::

    pip install Mr-Repo

To install Mr. Repo from source: ::

    git clone git://github.com/RyanMcG/Mr-Repo.git
    cd Mr-Repo
    python setup.py install

If you want to run Mr. Repo from source you need to manually get the
dependencies first. ::

    # Assuming you are already in the Mr-Repo directory
    pip install -r requirements.txt
    pip install -r dev-requirements.txt # Optional
    ./mr

Usage
-----

Run the ``init`` command to get to set up the two files by automatically
interpreting subdirectories. ::

    mr_repo init [--clean]

The ``--clean`` option causes the ``init`` command create blank tracking files and to not automatically interpret subdirectories.

Once you have the files setup you can add and remove repos by their directory
names with the add and remove commands. ::

    mr_repo add <repo/direcotry name>
    # Or to remove a repo
    mr_repo rm <repo/direcotry name>

You can also automatically reinterpret the current directory with the ``update``
command. ::

    mr_repo update

That's all the boring stuff. The part of *Mr. Repo* that's actually useful is
its ability to pull repos you've added from other places, but aren't available
in your current directory.

To determine what repos you have just use the ``list`` command. By default the
list command outputs a list of currently available repos. Using the ``-a`` flag
also displays information about unavailable repos (i.e. repos that are not
currently set up in the CWD). As you might expect the ``-n`` flag can be used to
display repos that are not currently available. ::

    mr_repo list [-a | --all] [-n | --not-available]

Once you know what repos are or are not currently available you can
``get``/``unget`` them. ::

    mr_repo get <not currently available repo name>
    mr_repo unget [-f | --force] <currently available repo name>

The ``unget`` command removes the repo if all changes have been fully committed
and also updates the ``.this_repo`` file. In the case where a there are uncommitted
changes an error is thrown and the command fails. If the user wants to remove it
anyways then the user can add the ``-f`` flag to force the removal.

TO DO
~~~~~

*   Update this file.
*   Add depth parameter to ``update`` to enable configuration of max depth.
*   Add ``--force`` option to ``update``. Forces update of configuration instead
    of ignoring existing.
*   Change ``--current-only`` to ``--controlled``. This option should only
    update (add to ``.this_repo``) repositories already referenced in
    ``.mr_repo.yml``.
*   Print debugging/process information when ``--verbose`` option is present.
*   Support adding/removing/getting/ungetting multiple repositories at once.
*   Create a MrRepoRepo wrapper class for use in MrRepo instead of calling
    git.Repo directly
    *   Support the following formats: Git (done), Hg, MrRepo, Folder
