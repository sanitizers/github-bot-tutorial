import asyncio
import os

from aiohttp.client import ClientSession
from octomachinery.github.api.tokens import GitHubOAuthToken
from octomachinery.github.api.raw_client import RawGitHubAPI


async def main():
    access_token = GitHubOAuthToken(os.environ['GITHUB_TOKEN'])
    async with ClientSession() as http_session:
        gh = RawGitHubAPI(
            access_token,
            session=http_session,
            user_agent='webknjaz',
        )
        await gh.patch(
            '/repos/mariatta/strange-relationship/issues{/number}',
            data={'state': 'closed'},
            url_vars={'number': 28},
        )


asyncio.run(main())
