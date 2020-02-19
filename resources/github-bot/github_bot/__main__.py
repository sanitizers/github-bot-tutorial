"""PyCon workshops GitHub bot exercise."""

from datetime import datetime
import logging
import re

from octomachinery.app.server.runner import run as run_app
from octomachinery.routing import process_event_actions
from octomachinery.routing.decorators import process_webhook_payload
from octomachinery.runtime.context import RUNTIME_CONTEXT


logger = logging.getLogger(__name__)


@process_event_actions('issues', {'opened'})
@process_webhook_payload
async def on_issue_opened(*, issue, **_kw):
    """Whenever an issue is opened, greet the author and say thanks."""
    github_api = RUNTIME_CONTEXT.app_installation_client

    comments_api_url = issue['comments_url']
    author = issue['user']['login']
    message = (
        f'Thanks for the report @{author}! '
        "I will look into it ASAP! (I'm a bot 🤖)."
    )
    await github_api.post(comments_api_url, data={'body': message})


@process_event_actions('pull_request', {'closed'})
@process_webhook_payload
async def on_pr_merged(*, number, pull_request, **_kw):
    """Whenever a PR is merged, say thanks to the author."""
    github_api = RUNTIME_CONTEXT.app_installation_client

    if not pull_request['merged']:
        # interrupt early
        logger.info('PR #%d just got closed but not merged', number)
        return

    logger.info('PR #%d just got merged', number)

    comments_api_url = pull_request['comments_url']
    author = pull_request['user']['login']
    message = (
        f'Thanks for the PR @{author}! '
    )
    await github_api.post(
        comments_api_url, data={
            'body': message,
        },
    )


@process_event_actions('issue_comment', {'created'})
@process_webhook_payload
async def on_comment_created(*, comment, **_kw):
    """Whenever an comment is posted, like it."""
    github_api = RUNTIME_CONTEXT.app_installation_client
    comment_reactions_api_url = f'{comment["url"]}/reactions'

    await github_api.post(
        comment_reactions_api_url,
        preview_api_version='squirrel-girl',
        data={'content': '+1'},
    )


@process_event_actions('pull_request', {'opened', 'edited'})
@process_webhook_payload
async def on_pr_check_wip(*, pull_request, repository, **_kw):
    """React to an opened or changed PR event.

    Send a status update to GitHub via Checks API.
    """
    check_run_name = 'Work-in-progress state'

    pr_head_sha = pull_request['head']['sha']
    repo_api_url = repository['url']

    check_runs_base_uri = f'{repo_api_url}/check-runs'

    github_api = RUNTIME_CONTEXT.app_installation_client
    resp = await github_api.post(
        check_runs_base_uri,
        preview_api_version='antiope',
        data={
            'name': check_run_name,
            'head_sha': pr_head_sha,
            'status': 'queued',
            'started_at': f'{datetime.utcnow().isoformat()}Z',
        },
    )

    check_runs_updates_uri = (
        f'{check_runs_base_uri}/{resp["id"]:d}'
    )

    resp = await github_api.patch(
        check_runs_updates_uri,
        preview_api_version='antiope',
        data={
            'name': check_run_name,
            'status': 'in_progress',
        },
    )

    pr_title = pull_request['title'].lower()
    wip_markers = (
        'wip', '🚧', 'dnm',
        'work in progress', 'work-in-progress',
        'do not merge', 'do-not-merge',
        'draft',
    )

    is_wip_pr = any(m in pr_title for m in wip_markers)

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
                    'Debug info:\n'
                    f'is_wip_pr={is_wip_pr!s}\n'
                    f'pr_title={pr_title!s}\n'
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
                    'Debug info:\n'
                    f'is_wip_pr={is_wip_pr!s}\n'
                    f'pr_title={pr_title!s}\n'
                    f'wip_markers={wip_markers!r}',
                'summary':
                    '🚧 Please do not merge this PR '
                    'as it is still under construction.'
                    '\n\n'
                    '![Under constuction tape]('
                    'https://cdn.pixabay.com'
                    '/photo/2012/04/14/14/59'
                    '/border-34209_960_720.png)\n'
                    "![Homer's on the job]("
                    'https://farm3.staticflickr.com'
                    '/2150/2101058680_64fa63971e.jpg)',
            },
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
        },
    )


@process_event_actions('check_run', {'requested_action'})
@process_webhook_payload
async def on_pr_action_button_click(*, check_run, requested_action, **_kw):
    """Flip the WIP switch when user hits a button."""
    requested_action_id = requested_action['identifier']
    if requested_action_id not in {'wip', 'unwip'}:
        return

    github_api = RUNTIME_CONTEXT.app_installation_client

    wip_it = requested_action_id == 'wip'

    pull_request = check_run['pull_requests'][0]
    pr_api_uri = pull_request['url']

    pr_details = await github_api.getitem(pr_api_uri)

    pr_title = pr_details['title']

    if wip_it:
        new_title = f'WIP: {pr_title}'
    else:
        wip_markers = (
            'wip', '🚧', 'dnm',
            'work in progress', 'work-in-progress',
            'do not merge', 'do-not-merge',
            'draft',
        )

        wip_regex = fr'(\s*({"|".join(wip_markers)}):?\s+)'
        new_title = re.sub(
            wip_regex, '', pr_title, flags=re.I,
        ).replace('🚧', '')

    await github_api.patch(
        pr_api_uri,
        data={
            'title': new_title,
        },
    )


if __name__ == '__main__':
    run_app(
        name='PyCon-Bot-by-webknjaz',
        version='1.0.0',
        url='https://github.com/apps/pyyyyyycoooon-booooot111',
    )
