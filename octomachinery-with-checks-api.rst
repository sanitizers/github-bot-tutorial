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

.. code::

    @process_event_actions('pull_request', {'opened', 'edited'})
    @process_webhook_payload
    async def on_pr_check_wip(
            *,
            action, number, pull_request,
            repository, sender,
            organization,
            installation,
    ):
        """React to an opened or changed PR event.

        Send a status update to GitHub via Checks API.
        """
        github_api = RUNTIME_CONTEXT.app_installation_client

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

.. code::

    from datetime import datetime

    ...

    ...
        ...
        # check_run_name = 'Work-in-progress state 🤖'
        check_run_name = 'Work-in-progress state'

        pr_head_branch = pull_request['head']['ref']
        pr_head_sha = pull_request['head']['sha']
        repo_url = pull_request['head']['repo']['url']

        check_runs_base_uri = f'{repo_url}/check-runs'

        resp = await github_api.post(
            check_runs_base_uri,
            preview_api_version='antiope',
            data={
                'name': check_run_name,
                'head_branch': pr_head_branch,
                'head_sha': head_sha,
                'status': 'queued',
                'started_at': f'{datetime.utcnow().isoformat()}Z',
            },
        )

        check_runs_updates_uri = (
            f'{check_runs_base_uri}/{resp["id"]:d}'
        )
        ...
        resp = await github_api.patch(
            check_runs_updates_uri,
            preview_api_version='antiope',
            data={
                'name': check_run_name,
                'status': 'in_progress',
            },
        )

.. warning::

    Using this API requires setting a special marker with `antiope`
    codename in order to flag GitHub that you *really* want to access
    this preview api version. If you miss that, attempting to use this
    API will result in an error response from the GitHub platform.

Now, let's check the PR title and figure out whether it looks WIP or
not:

.. code::

    pr_title = pull_request['title'].lower()
    wip_markers = (
        'wip', '🚧', 'dnm',
        'work in progress', 'work-in-progress',
        'do not merge', 'do-not-merge',
        'draft',
    )

    is_wip_pr = any(m in pr_title for m in wip_markers)

The last thing left is sending this information to GitHub.
Let's include some illustrative data to the Checks page. For this, we'll
use Markdown markup and some emojis 👩‍🔬.

Add this snippet in the end of our ``on_pr_check_wip`` event handler:

.. code::

    await github_api.patch(
        check_runs_updates_uri,
        preview_api_version='antiope',
        data={
            'name': check_run_name,
            'status': 'completed',
            'conclusion': 'success' if not is_wip_pr else 'neutral',
            'completed_at': f'{datetime.utcnow().isoformat()}Z',
            'output': {
                'title':
                    '🤖 This PR is not Work-in-progress: Good to go',
                'text':
                    'Debug info: '
                    f'is_wip_pr={is_wip_pr!s} '
                    f'pr_title={pr_title!s} '
                    f'wip_markers={wip_markers!r}',
                'summary':
                    'This change is ready to be reviewed.'
                    '\n\n'
                    '![Go ahead and review it!]('
                    'https://farm1.staticflickr.com'
                    '/173/400428874_e087aa720d_b.jpg)',
            } if not is_wip_pr else {
                'title':
                    '🤖 This PR is Work-in-progress: '
                    'It is incomplete',
                'text':
                    'Debug info: '
                    f'is_wip_pr={is_wip_pr!s} '
                    f'pr_title={pr_title!s} '
                    f'wip_markers={wip_markers!r}',
                'summary':
                    '🚧 Please do not merge this PR '
                    'as it is still under construction.'
                    '\n\n'
                    '![Under constuction tape]('
                    'https://cdn.pixabay.com'
                    '/photo/2012/04/14/14/59'
                    '/border-34209_960_720.png)'
                    "![Homer's on the job]("
                    'https://farm3.staticflickr.com'
                    '/2150/2101058680_64fa63971e.jpg)',
            },
        },
    )

That's it! You can now commit, push and deploy your app to Heroku. Then,
go create a PR in you test repo, try out adding WIP into its title and
removing it. See what happens, visit Checks page...

Action buttons
''''''''''''''

Manual editing of PR title is nice but let's have more fun and add a
button to the Checks page!

Extend the ``data`` argument of the last API call like this:

.. code::

    ...
    ...,
    'actions': [
        {
            'label': 'WIP it!',
            'description': 'Mark the PR as WIP',
            'identifier': 'wip',
        } if not is_wip_pr else {
            'label': 'UnWIP it!',
            'description': 'Remove WIP mark from the PR',
            'identifier': 'unwip',
        },
    ],
    ...

Now, your Checks page will have `WIP it!` or `UnWIP it!` button
available on the UI.

Clicking that button causes another event in GitHub. So now we have to
write another handler to properly process and react to it.

Add this code to achieve what we need:

.. code::

    @process_event_actions('check_run', {'requested_action'})
    @process_webhook_payload
    async def on_pr_action_button_click(
            *,
            action, check_run, requested_action,
            repository, sender,
            installation,
    ):
        """Flip the WIP switch when user hits a button."""
        if requested_action not in {'wip', 'unwip'}:
            return

        github_api = RUNTIME_CONTEXT.app_installation_client

        wip_it = requested_action == 'wip'

        pr = check_run['pull_requests']
        pr_title = pr['title']
        pr_update_uri = pr['url']

        if wip_it:
            new_title = f'WIP: {pr_title}'
        else:
            wip_markers = (
                'wip', '🚧', 'dnm',
                'work in progress', 'work-in-progress',
                'do not merge', 'do-not-merge',
                'draft',
            )

            wip_regex = f"(\s*({'|'.join(wip_markers)}):?\s+)"
            new_title = re.sub(
                wip_regex, '', pr_title, flags=re.I,
            ).replace('🚧','')

        await github_api.patch(
            pr_update_uri,
            data={
                'title': new_title,
            },
        )

So this basically edits PR title depending on which of two buttons have
been clicked.

Redeploy your updated code to Heroku and have some fun with it!

.. _`Checks API`: https://developer.github.com/apps/quickstart-guides/creating-ci-tests-with-the-checks-api/
.. _`GitHub protected branches bug`: https://github.community/t5/GitHub-API-Development-and/BUG-Branch-protection-settings-break-for-checks-with-emojis-%EF%B8%8F/m-p/20951/highlight/true#M1225
