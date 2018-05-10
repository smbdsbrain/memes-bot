import asyncio

from aiotg import logging
from invoke import task

logging.basicConfig(level=logging.INFO)


@task(default=True)
def run_bot(ctx):
    from main import run
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(ctx.config))
