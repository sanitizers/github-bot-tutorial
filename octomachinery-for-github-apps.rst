Using octomachinery to respond to GitHub events
===============================================

In the previous example, we've been interacting with GitHub by
making requests to GitHub. And we've been doing that locally on
our own machine.

In this section we'll use what we know so far and start building
an actual bot.
We'll create a webserver that responds to GitHub webhook events.

Webhook events
--------------

When an event is triggered in GitHub, GitHub can notify you about the
event by sending you a POST HTTP request along with the payload.

Some example ``events`` are:

- issues: any time an issue is assigned, unassigned, labeled, unlabeled,
  opened, edited, closed, reopened, etc.

- pull_request: any time a pull request is opened, edited, closed,
  reopened, review requested, etc.

- status: any time there's status update.

- checks: any time there's check requested or its status update posted.

- installations: any time GitHub App is installed or removed from a repo
  or new update permissions are accepted by the user.

The complete list of events is listed `here
<https://developer.github.com/v3/activity/events/types/>`_.

Since GitHub needs to send you POST requests for the webhook, it can't
send them to your personal laptop. So we need to create a webservice
that's open on the Internet.

To the cloud! ☁

Create a new Heroku App
-----------------------

Login to your account on Heroku. You should land at
https://dashboard.heroku.com/apps.

Click "New" > `"Create a new app"
<https://dashboard.heroku.com/new-app?org=personal-apps>`_. Type in the
app name and click "Create app" button.
If you leave it empty, Heroku will assign a name for you.

On the app page, right-click on the "Open app" button and click "Copy
link address". We'll need this a bit later, in the next step.

`Create a new GitHub App`_
--------------------------

1. Go to `Profile Settings`_ > `Developer Settings`_ > `GitHub Apps`_ >
   `New GitHub App`_

2. Click `"New GitHub App" <https://github.com/settings/apps/new>`_.

3. Fill in 3 required fields:

   - Webhook URL (*paste the URL of the Heroku app you copied earlier*,
     it should look smth like
     ``https://your-heroku-app-name.herokuapp.com/``)

   - GitHub App name (this will be turned into an app slug)

   - Homepage URL (put some URL here, you might use the same as for
     webhooks and change it later)

4. Select the following permissions:

   - ``Checks``: ``Read & Write``

   - ``Issues``: ``Read & Write``

   - ``Pull requests``: ``Read & Write``

5. Go to "Subscribe to events" section and select:

   - ``Check run``

   - ``Check suite``

   - ``Issue comment``

   - ``Issues``

   - ``Label``

   - ``Pull request``

6. Keep ``Only on this account`` radio selected
   and hit "Create GitHub App"

7. Click "Generate a private key" in the bottom of the app page and
   download it onto your computer

8. Keep the app page open, you'll need it soon

Create two new repositories on GitHub
-------------------------------------

You'll need two repositories. The first one is to hold the codebase for
the bot, essentially a webservice application. This is where you will
actually push the source code. Going forward I will call this one the
``github-bot``.

The other repo, will mostly be empty for now. It will be the repo where
the GitHub App will be installed, and your bot will interact with this
repo. In real world, this will be the project that you're managing. I
will be using my personal repo, ``strange-relationship``.

You can create the repositories on GitHub, and then clone it to your
local machine.

Create a github-bot
-------------------

Let's get ready to write your own GitHub bot. To start, use your
favorite text editor or IDE. Go to the directory where your github-bot
is at (the root of the repository you've created earlier).

Inside that directory, create a `requirements.txt` file.
Add `octomachinery` to it.

requirements.txt::

   octomachinery

Now, let's create a `.env` file in the directory next to
`requirements.txt`. Add fill it in with the development env vars.
For simplicity, set `GITHUB_PRIVATE_KEY_PATH` var and run the bash
one-liner as shown in the example below. It turns a multiline private
key file contents into a properly escaped single-line string.

.. code::

    touch .env
    GITHUB_PRIVATE_KEY_PATH=~/Downloads/your-app-slug.2019-03-24.private-key.pem
    cat $GITHUB_PRIVATE_KEY_PATH | python3.7 -c 'import sys; inline_private_key=r"\n".join(map(str.strip, sys.stdin.readlines())); print(f"GITHUB_PRIVATE_KEY='"'"'{inline_private_key}'"'"'", end="")' >> .env

Now, copy-paste the *App ID* from the General App Settings page, which
is still open in your browser and put it into `.env` file as a value for
`GITHUB_APP_IDENTIFIER` variable. Also put there `DEBUG=true` and `ENV=dev`

``.env`` should look like this now::

    GITHUB_PRIVATE_KEY='-----BEGIN RSA PRIVATE KEY-----\n[..snip..]\n-----END RSA PRIVATE KEY-----'
    GITHUB_APP_IDENTIFIER=99999

    DEBUG=true
    ENV=dev

After that, create a ``.gitignore`` in the same folder, it should contain
``.env`` entry. You can use the following command to download appropriate
template::

    wget -O - https://www.gitignore.io/api/git%2Cdotenv%2Clinux%2Cpydev%2Cpython%2Cwindows%2Cpycharm%2Ball%2Cjupyternotebooks%2Cvim%2Cwebstorm%2Cemacs >> .gitignore

In the same directory, create another directory called ``github_bot``.
Inside this new directory, create ``__main__.py``.

Your ``github-bot/`` should now look as follows::

   /github-bot
   /github-bot/.env
   /github-bot/.gitignore
   /github-bot/requirements.txt
   /github-bot/github_bot/__main__.py

We'll start by creating a simple octomachinery app in ``__main__.py``.

Edit ``__main__.py`` as follows::

    from octomachinery.app.server.runner import run as run_app


    if __name__ == "__main__":
        run_app(
            name='PyCon-Bot-by-webknjaz',
            version='1.0.0',
            url='https://github.com/apps/pyyyyyycoooon-booooot111',
        )

Save the file. Your webserver is now ready. From the command line and at
the root of your project, enter the following::

   python3 -m github_bot

You should now see the following output::

    DEBUG:octomachinery.app.server.runner:================ App version: 1.0.0 =================
    DEBUG:asyncio:Using selector: EpollSelector
    DEBUG:octomachinery.app.server.machinery:The GitHub App env is set to `dev`
    INFO:octomachinery.app.server.machinery:Webhook secret is [NOT SET]: SIGNED WEBHOOKS WILL BE REJECTED
    INFO:octomachinery.app.server.machinery:Starting the following GitHub App:
    INFO:octomachinery.app.server.machinery:* app id: 21717
    INFO:octomachinery.app.server.machinery:* private key SHA-1 fingerprint: 7d:96:e8:e5:8f:07:b5:10:97:85:2a:f4:33:72:b7:08:a5:81:82:92
    INFO:octomachinery.app.server.machinery:* user agent: PyCon-Bot-by-webknjaz/1.0.0 (+https://github.com/apps/pyyyyyycoooon-booooot111)
    INFO:octomachinery.github.api.app_client:This GitHub App is installed into:
    INFO:octomachinery.github.api.app_client:* Installation id 491111 (installed to webknjaz)
    INFO:octomachinery.app.server.machinery:================= Serving on http://localhost:8080 ==================

.. warning::

    If you see some configuration error about invalid value of a setting,
    try checking env vars exported in your current terminal session.
    The dotenv library (``envparse``) used in the framework doesn't
    substitute those vars with values from ``.env`` file if they already
    exist in your env. You may need to ``unset`` them before proceeding.

Open your browser and point it to http://localhost:8080.  Alternatively,
you can open another terminal and type::

   curl -X GET localhost:8080

Whichever method you choose, you should see the output: "405: Method Not
Allowed". That's expected: since the GitHub Apps event receiver is only
supposed to process HTTP POST requests, other methods are not allowed.

Deploy to Heroku
----------------

Before we go further, let's first get that webservice deployed to Heroku.

At the root of your project, create a new file called ``Procfile``, (without any
extension). This file tells Heroku how it should run your app.

Inside ``Procfile``::

    web: python3 -m github_bot

This will tell Heroku to run a web dyno using the command ``python3 -m github_bot``.

Additionally, create ``runtime.txt`` file next to it containing::

    python-3.7.2

This ensures that Heroku will provide Python 3.7 for us.
Just as we need! 🎉

Your file structure should now look like the following::

   /github-bot
   /github-bot/.env
   /github-bot/.gitignore
   /github-bot/requirements.txt
   /github-bot/runtime.txt
   /github-bot/Procfile
   /github-bot/github_bot/__main__.py


Commit everything (except for ``.env`` file!) and push to GitHub.

Open Heroku app dashboard (it may still be open somewhere among your
browser tabs).

Go to the "Deploy" tab. Under "Deployment method", choose GitHub.
Connect your GitHub account if you haven't done that.

Under "Search for a repository to connect to", enter your project name,
e.g "github-bot". Press "Search". Once it found the right repo, press
"Connect".

Scroll down. Under Deploy a GitHub branch, choose "master", and click
"Deploy Branch". (Optionally, enable automatic deployments)

Watch the build log, and wait until it finished.

When you see "Your app was successfully deployed", click on the
"View" button.

You should see "405: Method Not Allowed" (just as it was locally).

Tip: Install Heroku toolbelt to see your logs. Once you have Heroku
toolbelt installed, you can read the logs by::

   heroku logs -a <app name>

Pro tip: Install `Timber.io Logging
<https://elements.heroku.com/addons/timber-logging>`_ addon or similar
to have a nicer view to more logs right in your browser.

Update the Config Variables in Heroku
'''''''''''''''''''''''''''''''''''''

Almost ready to actually start writing bots! Are you still on the Heroku
dashboard? We are not done there just yet :)

Go to the **Settings** tab.

Click on the **Reveal Config Vars** button. Add three config variables
here.

The first one called **GITHUB_APP_IDENTIFIER**. Copy it from ``.env``
file you've created earlier.

The next one is called **GITHUB_PRIVATE_KEY**. Copy it directly from the
private key file you've downloaded earlier. No conversion is needed this
time.

Finally, set **HOST** to ``0.0.0.0``, ``DEBUG=false`` and ``ENV=prod``.

Your first GitHub bot!
----------------------

Ok NOW everything is finally ready. Let's start with something simple. Let's have
a bot that **responds to every newly created issue in your project**. For example,
whenever someone creates an issue, the bot will automatically say something like:
"Thanks for the report, @user. I will look into this ASAP!"

Go to the ``__main__.py`` file, in your ``github_bot`` codebase.

The first change the part where we did is to add the following imports::

    from octomachinery.app.routing import process_event_actions
    from octomachinery.app.routing.decorators import process_webhook_payload
    from octomachinery.app.runtime.context import RUNTIME_CONTEXT

Add the following coroutine (above **if __name__ == "__main__":**)::

    @process_event_actions('issues', {'opened'})
    @process_webhook_payload
    async def on_issue_opened(
            *,
            action, issue, repository, sender, installation,
            assignee=None, changes=None,
    ):
        """Whenever an issue is opened, greet the author and say thanks."""
        github_api = RUNTIME_CONTEXT.app_installation_client

This is where we are essentially subscribing to the GitHub ``issues``
event, and specifically to the "opened" issues event.

``@process_webhook_payload`` decorator automagically "unpacks" the event
payload fields into the function arguments.

``github_api`` is a GitHub API client wrapper, which we've used in the
previous section to make API calls to GitHub. Here, we get it from the
contextvar proxy context, offered by octomachinery under the hood. This
client is authorized against the installation bound to the current
incoming event.

.. _greet_author:

Leave a comment whenever an issue is opened
'''''''''''''''''''''''''''''''''''''''''''

Back to the task at hand. We want to *leave a comment whenever someone opened an
issue*. Now that we're subscribed to the event, all we have to do now is to
actually create the comment.

We've done this in the previous section on the command line. You will recall
the code is something like the following::

    await github_api.post(url, data={"body": message})

Let's think about the ``url`` in this case. Previously, you might have constructed
the url manually as follows::

    url = f"/repos/mariatta/strange-relationship/issues/{issue_number}/comments"

When we receive the webhook event however, the issue comment url is actually
supplied in the payload.

Take a look at GitHub's issue event payload `example (scroll it a bit)
<https://developer.github.com/v3/activity/events/types/#issuesevent>`_.

It's a big JSON object. The portion we're interested in is::

   {
     "action": "opened",
     "issue": {
       "url": ...,
       "comments_url": "https://api.github.com/repos/baxterthehacker/public-repo/issues/2/comments",
       "events_url": "...",
       "html_url": "...",
     ...
   }

Notice that ``["issue"]["comments_url"]`` is actually the URL for posting comments to
this particular issue. With this knowledge, your url is now::

   comments_api_url = issue["comments_url"]

The next piece we want to figure out is what should the comment message be. For
this exercise, we want to greet the author, and say something like "Thanks @author!".

Take a look again at the issue event payload::

   {
     "action": "opened",
     "issue": {
       "url": "...",
        ...
       "user": {
         "login": "baxterthehacker",
         "id": ...,
     ...
   }

Did you spot it? The author's username can be accessed by ``issue["user"]["login"]``.

So now your comment message should be::

   author = issue["user"]["login"]
   message = (
       f"Thanks for the report @{author}! "
       "I will look into it ASAP! (I'm a bot 🤖)."
   )


Piece all of that together, and actually make the API call to GitHub to create the
comment::

    @process_event_actions('issues', {'opened'})
    @process_webhook_payload
    async def on_issue_opened(
            *,
            action, issue, repository, sender, installation,
            assignee=None, changes=None,
    ):
        """Whenever an issue is opened, greet the author and say thanks."""

        github_api = RUNTIME_CONTEXT.app_installation_client
        comments_api_url = issue["comments_url"]
        author = issue["user"]["login"]

        message = (
            f"Thanks for the report @{author}! "
            "I will look into it ASAP! (I'm a bot 🤖)."
        )
        await github_api.post(comments_api_url, data={"body": message})


Your entire **__main__.py** should look like the following::

    from octomachinery.app.routing import process_event_actions
    from octomachinery.app.routing.decorators import process_webhook_payload
    from octomachinery.app.runtime.context import RUNTIME_CONTEXT
    from octomachinery.app.server.runner import run as run_app


    @process_event_actions('issues', {'opened'})
    @process_webhook_payload
    async def on_issue_opened(
            *,
            action, issue, repository, sender, installation,
            assignee=None, changes=None,
    ):
        """Whenever an issue is opened, greet the author and say thanks."""

        github_api = RUNTIME_CONTEXT.app_installation_client
        comments_api_url = issue["comments_url"]
        author = issue["user"]["login"]

        message = (
            f"Thanks for the report @{author}! "
            "I will look into it ASAP! (I'm a bot 🤖)."
        )
        await github_api.post(comments_api_url, data={"body": message})


    if __name__ == "__main__":
        run_app(
            name='PyCon-Bot-by-webknjaz',
            version='1.0.0',
            url='https://github.com/apps/pyyyyyycoooon-booooot111',
        )


Commit that file, push it to GitHub, and deploy it in Heroku.

Almost there!

Go to "Install App" tab in the GitHub App settings and install it into
your test repo from there. It's needed so that your bot would start
actually receiving events from that repository.

Try and create an issue in the repo. See your bot in action!!

Congrats! You now have a bot in place! Let's give it another job.

.. _say_thanks:

Say thanks when an issue has been merged
''''''''''''''''''''''''''''''''''''''''

Let's now have the bot **say thanks, whenever a pull request has been merged**.

For this case, you'll want to subscribe to the ``pull_request`` event, specifically
when the ``action`` to the event is ``closed``.

For reference, the relevant GitHub API documentation for the ``pull_request`` event
is here: https://developer.github.com/v3/activity/events/types/#pullrequestevent.

Scroll a bit to see the example payload for this event.

Try it on your own.

**Note**: A pull request can be closed without it getting merged. You'll need
a way to determine whether the pull request was merged, or simply closed.

.. _react_to_comments:

React to issue comments
'''''''''''''''''''''''

Everyone has opinion on the internet. Encourage more discussion by
**automatically leaving a thumbs up reaction** for every comments in the issue.
Ok you might not want to actually do that, (and whether it can actually encourage
more discussion is questionable). Still, this can be a fun exercise.

How about if the bot always gives **you** a thumbs up?

Try it out on your own.

- The relevant documentation is here: https://developer.github.com/v3/activity/events/types/#issuecommentevent

- The example payload for the event is next to it

- The API documentation for reacting to an issue comment is here: https://developer.github.com/v3/reactions/#create-reaction-for-an-issue-comment

.. _label_prs:

Label the pull request
''''''''''''''''''''''

Let's make your bot do even more hard work. **Each time someone opens a pull request,
have it automatically apply a label**. This can be a "pending review" or
"needs review" label.

The relevant API call is this: https://developer.github.com/v3/issues/#edit-an-issue

.. _`Profile Settings`: https://github.com/settings/profile
.. _`Developer Settings`: https://github.com/settings/developers
.. _`GitHub Apps`: https://github.com/settings/apps
.. _`New GitHub App`: https://github.com/settings/apps/new
.. _`Create a new GitHub App`: https://developer.github.com/apps/building-github-apps/creating-a-github-app/#creating-a-github-app
