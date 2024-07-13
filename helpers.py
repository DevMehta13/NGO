import os
from flask import redirect, render_template, request, session, send_file, url_for
from functools import wraps
import pandas as pd
import re
import asyncio
import aiohttp
from pyembed.core import PyEmbed
from pyembed.core.consumer import PyEmbedConsumerError

pyembed_instance = PyEmbed()


ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", error_code=code, error_message=escape(message)), code


def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin") != ADMIN_USERNAME:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def upload_to_excel(path: str, data, sheet_name):

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data)

    # Write the combined DataFrame back to the Excel file
    df.to_excel(path, sheet_name=sheet_name, index=False)
    print(f"Data saved to {path}")


# Function to extract URLs from the text
def extract_urls(text):
    import re
    url_pattern = re.compile(r'https?://\S+')
    return url_pattern.findall(text)


async def fetch_embed(session, url):
    try:
        # Using PyEmbed to fetch embed HTML asynchronously
        embed_html = pyembed_instance.embed(url)
        if embed_html:
            return {
                'url': url,
                'html': embed_html,
                'is_embed': True
            }
    except PyEmbedConsumerError as e:
        print(f"Error embedding {url}: {e}")
    except Exception as e:
        print(f"Error embedding {url}: {e}")
    return {
        'url': url,
        'html': f'<a href="{url}" target="_blank">{url}</a>',
        'is_embed': False
    }


async def generate_previews(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_embed(session, url) for url in urls]
        return await asyncio.gather(*tasks)


def embed_link(link_text):
    urls = extract_urls(link_text)
    if urls:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        previews = loop.run_until_complete(generate_previews(urls))
        preview = previews[0] if previews else None
    else:
        preview = None
    post = {
        'content': link_text,
        'preview': preview
    }
    return post