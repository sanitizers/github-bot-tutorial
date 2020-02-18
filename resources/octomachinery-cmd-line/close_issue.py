import asyncio
import os

from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI


async def main():
    access_token = GitHubOAuthToken(os.environ["GITHUB_TOKEN"])
    gh = RawGitHubAPI(access_token, user_agent='webknjaz')
    await gh.patch(
        '/repos/mariatta/strange-relationship/issues{/number}',
        data={'state': 'closed'},
        url_vars={'number': 28},
    )

asyncio.run(main())
