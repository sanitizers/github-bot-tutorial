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

.. code::

    from datetime import datetime

    ...

    ...
        ...
        pr_head_branch = pull_request['head']['ref']
        pr_head_sha = pull_request['head']['sha']
        repo_url = pull_request['head']['repo']['url']

        check_runs_base_uri = f'{repo_url}/check-runs'

        resp = await github_api.post(
            check_runs_base_uri,
            preview_api_version='antiope',
            data={
                'name': 'Work-in-progress state 🤖',
                'head_branch': pr_head_branch,
                'head_sha': head_sha,
                'status': 'queued',
                'started_at': f'{datetime.utcnow().isoformat()}Z',
            },
        )

        check_runs_updates_uri = f'{check_runs_base_uri}/{resp["id"]:d}'
        ...
        resp = await github_api.patch(
            check_runs_updates_uri,
            preview_api_version='antiope',
            data={
                'name': 'Work-in-progress state 🤖',
                'status': 'in_progress',
            },
        )

.. code::

    pr_title = pull_request['title'].lower()
    wip_markers = (
        'wip', '🚧', 'dnm',
        'work in progress', 'work-in-progress',
        'do not merge', 'do-not-merge',
        'draft',
    )

    is_wip_pr = any(m in pr_title for m in wip_markers)

.. code::

    resp = await github_api.patch(
        check_runs_updates_uri,
        preview_api_version='antiope',
        data={
            'name': 'Work-in-progress state 🤖',
            'status': 'completed',
            'conclusion': 'success' if not is_wip_pr else 'neutral',
            'completed_at': f'{datetime.utcnow().isoformat()}Z',
            'output': {
                'title': '🤖 This PR is not Work-in-progress: Good to go',
                'text':
                    'Debug info: '
                    f'is_wip_pr={is_wip_pr!s} '
                    f'pr_title={pr_title!s} '
                    f'wip_markers={wip_markers!r}',
                'summary':
                    'This change is ready to be reviewed.'
                    '\n\n'
                    '<center>'
                    '![Go ahead and review it!]('
                    'https://farm1.staticflickr.com'
                    '/173/400428874_e087aa720d_b.jpg)'
                    '</center>',
            } if not is_wip_pr else {
                'title': '🤖 This PR is Work-in-progress: It is incomplete',
                'text':
                    'Debug info: '
                    f'is_wip_pr={is_wip_pr!s} '
                    f'pr_title={pr_title!s} '
                    f'wip_markers={wip_markers!r}',
                'summary':
                    '🚧 Please do not merge this PR '
                    'as it is still under construction.'
                    '\n\n'
                    '<center>'
                    '![Under constuction tape]('
                    'https://cdn.pixabay.com'
                    '/photo/2012/04/14/14/59/border-34209_960_720.png)'
                    "![Homer's on the job]("
                    'https://farm3.staticflickr.com'
                    '/2150/2101058680_64fa63971e.jpg)'
                    '</center>',
            },
        },
    )

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

.. _`Checks API`: https://developer.github.com/apps/quickstart-guides/creating-ci-tests-with-the-checks-api/
