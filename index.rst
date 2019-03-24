.. github-bot-tutorial documentation master file, created by
   sphinx-quickstart on Sat Apr  7 10:39:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

How to Build a GitHub Bot
=========================

GitHub provides a great platform for collaborating. You can take it to the next
level by creating custom GitHub bots. By delegating some of the chores to a bot,
you get to spend more time developing your project and collaborating with others.

Learn how to automate your workflow by building a personal GitHub assistant for
your own project. We'll use a framework called `octomachinery
<https://octomachinery.dev>`_ to write a GitHub bot that does the following:

  - :ref:`Greet the person who created an issue in your project <greet_author>`.

  - :ref:`Say thanks when a pull request has been closed <say_thanks>`.

  - :ref:`Apply a label to issues or pull requests <label_prs>`.

  - :ref:`Gives a thumbs up reaction to comments you made <react_to_comments>`.
    (becoming your own personal cheer squad).

The best part is, you get to do all of the above using Python 3.7 as the
framework heavily relies on some of its features!

This tutorial is heavily based on `Build-a-GitHub-Bot Workshop
<https://youtu.be/ZwvjtCjimiw>`_ by `Mariatta Wijaya
<https://www.patreon.com/Mariatta>`_ which she first presented at
`PyCon US 2018 <https://us.pycon.org/2018/schedule/presentation/41/>`_.
Yet, current version uses a bit more higher level approaches to abstract
some implementation details away from programmers and help them focus on
the business logic part.

Code of Conduct
===============

Be open, considerate, and respectful.

License
=======

`The original tutorial <https://github-bot-tutorial.readthedocs.io>`_
has been written by `Mariatta Wijaya <https://twitter.com/mariatta>`_,
is licensed under `CC-BY-SA 4.0
<https://creativecommons.org/licenses/by-sa/4.0/>`_ and adopted to use
`octomachinery <https://octomachinery.dev>`_ framework as a basis for
exercises by `Sviatoslav Sydorenko <https://keybase.io/webknjaz>`_.

Agenda
======


.. toctree::
   :titlesonly:


   preparation
   why-github-bots
   resources
   octomachinery-cmd-line
   octomachinery-for-github-apps
   octomachinery-with-checks-api
   whats-next
   hall-of-fame
   git-basics
