Make your GitHub bot activity feedback more colorful
====================================================

Previously, we've used things which can be directly created in the
GitHub UI by regular users. But what if we need more? What if our
robot has complex multistage flows with rich result set?
In such case, we need to use `Checks API`_ — it's a way to built your
bot's activity outcomes right into GitHub's UI. You can add some
markdown-formatted content, upload a set of pictures, add annotations
right to your PRs' diff views and even put a few completely custom
buttons on your App's Checks page empowering users to trigger some
actions which your application would process. And, of course, it
facilitates separate indication of the processing state and check
outcome.

In this section, we'll extend the application that we've built earlier.

Work-in-progress indicator
''''''''''''''''''''''''''

Sometimes, when you work on Pull Request, you want to block it from
being merged accidentally.

Let's build a status check which will indicate that the PR is WIP and
will help to block it from being merged accidentally.

Add the following PR event handler:

.. literalinclude:: resources/github-bot/github_bot/__main__.py
   :language: python
   :lines: 70-76,84

This one is pretty easy, you're already familiar with this structure:
it's an event handler for PR openning and editing.

Let's extend it with some useful logic now.

This is where Checks API interaction begins. Every GitHub App's got a
Checks Suite attached to it. It's visible on the Checks page to where
you can get using either Checks tab in PRs or click a commit status
from the commit indicator on the branch page with commits list.

First thing we need to do is to create a Check Run which is an entity
representing a single task of validating something having a separate
subpage and status indicator in the GitHub UI.

Once we grab its ID we'll be able to use that in order to update
progress, status and details of this check task as more of its code gets
executed.

Here we add two GitHub API calls: one creates a check run with the
*queued* initial status and the other updates that status to
*in_progress*.

.. warning::

    Please don't use emoji in the ``check_run_name`` (corresponding to
    Check Run) of the payload when working with Checks API. At least not
    until the `GitHub protected branches bug`_ gets solved

.. literalinclude:: resources/github-bot/github_bot/__main__.py
   :language: python
   :lines: 3

.. literalinclude:: resources/github-bot/github_bot/__main__.py
   :language: python
   :lines: 77-83,85-107
   :dedent: 4

.. warning::

    Using this API requires setting a special marker with `antiope`
    codename in order to flag GitHub that you *really* want to access
    this preview api version. If you miss that, attempting to use this
    API will result in an error response from the GitHub platform.

Now, let's check the PR title and figure out whether it looks WIP or
not:

.. literalinclude:: resources/github-bot/github_bot/__main__.py
   :language: python
   :lines: 109-117
   :dedent: 4

The last thing left is sending this information to GitHub.
Let's include some illustrative data to the Checks page. For this, we'll
use Markdown markup and some emojis 👩‍🔬.

Add this snippet in the end of our ``on_pr_check_wip`` event handler:

.. literalinclude:: resources/github-bot/github_bot/__main__.py
   :language: python
   :lines: 119-161,173-174
   :dedent: 4

That's it! You can now commit, push and deploy your app to Heroku. Then,
go create a PR in you test repo, try out adding WIP into its title and
removing it. See what happens, visit Checks page...

Action buttons
''''''''''''''

Manual editing of PR title is nice but let's have more fun and add a
button to the Checks page!

Extend the ``data`` argument of the last API call like this:

.. literalinclude:: resources/github-bot/github_bot/__main__.py
   :language: python
   :lines: 162-172
   :dedent: 12

Now, your Checks page will have `WIP it!` or `UnWIP it!` button
available on the UI.

Clicking that button causes another event in GitHub. So now we have to
write another handler to properly process and react to it.

Add this code to achieve what we need:

.. literalinclude:: resources/github-bot/github_bot/__main__.py
   :language: python
   :lines: 177-216

We will also need to import regex library, add it in the top of our
module.

.. literalinclude:: resources/github-bot/github_bot/__main__.py
   :language: python
   :lines: 5

So this basically edits PR title depending on which of two buttons have
been clicked.

Redeploy your updated code to Heroku and have some fun with it!

.. _`Checks API`: https://developer.github.com/apps/quickstart-guides/creating-ci-tests-with-the-checks-api/
.. _`GitHub protected branches bug`: https://github.community/t5/GitHub-API-Development-and/BUG-Branch-protection-settings-break-for-checks-with-emojis-%EF%B8%8F/m-p/20951/highlight/true#M1225
