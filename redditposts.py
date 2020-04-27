from bs4 import BeautifulSoup
import json
import asyncio
import urllib
import discord
from discord.ext import commands
import staticconfig
import sys
import botauth
import os.path
from xml.dom.minidom import Document, Element, parseString
from typing import List

reddit_base_url: str = 'https://www.reddit.com'
subreddit_url:      str = f'{reddit_base_url}/r/PBE+leaguePBE/new.rss'
file_name:       str = 'cache/reddit_cache.json'

redditposts_announced: list = []

if os.path.isfile(file_name):
    try:
        with open(file_name) as forums_cache:
            redditposts_announced = json.load(forums_cache)
    except FileNotFoundError as e:
        print('File does not exist, will be created (eventually): ', e)
else:
    print(f'File does not exist, will be created (eventually): {file_name}')


def get_latest_reddit_post() -> list:
    request: urllib.request.Request = urllib.request.Request(
        subreddit_url,
        data = None,
        headers = {
            'User-Agent': 'brodiril:v0.1 (by /u/493msi)'
        }
    )

    document = urllib.request.urlopen(request).read()

    rss_data: Document       = parseString(document)

    feed:     Element        = rss_data.getElementsByTagName("feed")[0]

    posts:    List[Element]  = feed.getElementsByTagName("entry")

    new_posts: list = []

    for post in posts:
        category: Element      = post.getElementsByTagName("category")[0]

        subreddit: str      = category.getAttribute("label")

        author: Element      = post.getElementsByTagName("author")[0]

        author_name: str     = author.getElementsByTagName("name")[0].firstChild.nodeValue
        # author_link: str   = author.getElementsByTagName("uri")[0].firstChild.nodeValue

        post_id: str         = post.getElementsByTagName("id")[0].firstChild.nodeValue

        link: Element        = post.getElementsByTagName("link")[0]
        link_href: str       = link.getAttribute("href")

        title: str           = post.getElementsByTagName("title")[0].firstChild.nodeValue

        if post_id in redditposts_announced:
            break

        postdata: dict = {
            'id': post_id,
            'sub': subreddit,
            'url': link_href,
            'author': author_name,
            'title': title
        }

        new_posts.append(postdata)
    
    new_posts.reverse()

    return new_posts

async def check_forums_reddit(forumschannel : discord.TextChannel, emoji_kekban_emoji : discord.Emoji):
    newposts = None

    try:
        newposts: list = get_latest_reddit_post()

        if newposts:
            for reddit_post in newposts:
                if reddit_post and reddit_post['id'] and reddit_post['url']:
                    if reddit_post['id'] not in redditposts_announced:
                        redditposts_announced.append(reddit_post['id'])

                        print(f'New {reddit_post["sub"]} post:', reddit_post['id'])

                        if botauth.testing_mode:
                            continue

                        post_message: str = f'<@&{staticconfig.bug_notifications_role}> New post on **{reddit_post["sub"]}** by **{reddit_post["author"]}**:\n{reddit_post["url"]}'

                        try:
                            reddit_post_message: discord.Message = await forumschannel.send(post_message)
                            await reddit_post_message.add_reaction(emoji_kekban_emoji)
                        except Exception as e:
                            print('Discord error:', e, file=sys.stderr)

            with open(file_name, 'w') as forums_cache_file:
                json.dump(redditposts_announced, forums_cache_file)
    except Exception as e:
        print('Error while retrieving the posts:', e, file=sys.stderr)

def init(bot: commands.Bot, loop: asyncio.AbstractEventLoop):
    check_forums_task_started: bool = False

    async def check_forums():
        vandiland:          discord.Guild       = bot.get_guild(staticconfig.vandiland_id)
        emoji_kekban_emoji: discord.Emoji       = await vandiland.fetch_emoji(staticconfig.emoji_kekban)
        forumschannel:      discord.TextChannel = vandiland.get_channel(staticconfig.forums_channel_id)

        while True:
            await check_forums_reddit(forumschannel, emoji_kekban_emoji)
            await asyncio.sleep(staticconfig.delay_refresh)

    if not check_forums_task_started:
        loop.create_task(check_forums())
        check_forums_task_started = True

