import os
import requests
import hashlib
import math
import shutil

from typing import List, Dict, Any
from pytumblr import TumblrRestClient
from urllib.parse import urlparse

MAX_POSTS_PER_REQUEST = 20

def fetch_and_process_posts(
    client: TumblrRestClient, blog_identifier: str) -> List[Dict[str, Any]]:
    blog_url = f"{blog_identifier}.tumblr.com"
    processed_posts: List[str] = []
    thread_list: List[Dict[str, Any]] = []
    skipped_posts = 0
    processed = 0

    post_types = ["text", "answer", "photo"]

    for post_type in post_types:
        offset = 0
        try:
            # First request to get total number of posts for this type
            initial_posts = client.posts(blog_url, type=post_type, limit=1)
            total_posts = initial_posts["total_posts"]
            total_requests = math.ceil(total_posts / MAX_POSTS_PER_REQUEST)

            print(f"Total {post_type} posts to process: {total_posts}")
            print(f"Total requests needed for {post_type} posts: {total_requests}")

            for request_num in range(total_requests):
                print(
                    f"Processing request {request_num + 1} of {total_requests} for {post_type} posts"
                )
                try:
                    posts = client.posts(
                        blog_url,
                        type=post_type,
                        limit=MAX_POSTS_PER_REQUEST,
                        offset=offset,
                    )
                except Exception as e:
                    print(f"Error fetching {post_type} posts (offset {offset}): {e}")
                    continue

                for post in posts["posts"]:
                    if str(post["id"]) in processed_posts:
                        skipped_posts += 1
                        continue

                    thread_posts = process_post(post, blog_identifier, processed_posts)

                    if thread_posts:
                        thread_list.append(
                            {
                                "slug": post["slug"] or str(post["id"]),
                                "tags": post["tags"],
                                "date": post["date"],
                                "timestamp": post["timestamp"],
                                "posts": thread_posts,
                            }
                        )

                    processed += len(thread_posts)
                    processed_posts.append(str(post["id"]))

                offset += MAX_POSTS_PER_REQUEST
                # time.sleep(1)

        except Exception as e:
            print(f"Error fetching initial {post_type} posts: {e}")
            continue

    print(f"Skipped Duplicate Posts: {skipped_posts}")
    print(f"Processed Posts: {processed}")
    return thread_list

def process_post(post: Dict[str, Any], blog_identifier: str, processed_posts: List[str]) -> List[Dict[str, Any]]:
    thread_posts = []
    if post.get('trail'):
        for trail_post in post['trail']:
            if trail_post['post']['id'] in processed_posts and str(post['id']) in processed_posts:
                continue

            post_info = create_post_info(trail_post, post, blog_identifier)
            thread_posts.append(post_info)
            processed_posts.append(trail_post['post']['id'])

        if post['type'] == "answer":
            initial_post = create_ask_post_info(post)
            thread_posts = [initial_post] + thread_posts

    return thread_posts

def create_post_info(trail_post: Dict[str, Any], original_post: Dict[str, Any], blog_identifier: str) -> Dict[str, Any]:
    is_root_post = trail_post.get('is_root_item') == True
    is_post_being_processed = str(original_post['id']) == trail_post['post']['id']
    is_owned_by_blog_owner = blog_identifier == trail_post['blog']['name']

    if is_post_being_processed and is_root_post:
        post_position_type = "single_post"
    elif is_root_post and not is_owned_by_blog_owner and original_post['type'] == "answer":
        post_position_type = "trail_root_ask"
    elif is_root_post:
        post_position_type = "trail_root"
    elif is_post_being_processed:
        post_position_type = "trail_end"
    else:
        post_position_type = "trail"

    post_content = trail_post.get('content', trail_post.get('answer', ""))

    return {
        'id': trail_post['post']['id'],
        'blog_name': trail_post['blog']['name'],
        'content': post_content,
        'post_position_type': post_position_type
    }

def create_ask_post_info(post: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'id': post['id'],
        'blog_name': post['asking_url'] or "Anonymous",
        'content': post['question'],
        'post_position_type': "ask"
    }

def copy_css_to_blog_output(blog_output_dir: str):
    css_source = 'style.css'  # Adjust this path as needed
    css_destination = os.path.join(blog_output_dir, 'style.css')
    shutil.copy2(css_source, css_destination)

def download_image(url: str, images_dir: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        filename = hashlib.md5(url.encode()).hexdigest() + os.path.splitext(urlparse(url).path)[1]
        filepath = os.path.join(images_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filename
    return ""


def process_content_for_images(content: str, images_dir: str, download_images: bool) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(content, 'html.parser')
    img_tags = soup.find_all('img')

    for img in img_tags:
        src = img.get('src')
        if src and download_images:
            local_filename = download_image(src, images_dir)
            if local_filename:
                img['src'] = f'../images/{local_filename}'
        elif not download_images:
            img.extract()

    return str(soup)

def save_threads(thread_list: List[Dict[str, Any]], blog_name: str, output_dir: str, is_html: bool = False, download_images: bool = False) -> None:
    blog_output_dir = os.path.join(output_dir, blog_name)
    posts_dir = os.path.join(blog_output_dir, 'posts')
    images_dir = os.path.join(blog_output_dir, 'images')

    os.makedirs(blog_output_dir, exist_ok=True)
    os.makedirs(posts_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    print(f"Saving {len(thread_list)} files in {"html" if is_html else "txt"} format to {output_dir}. {"Images will be downloaded." if download_images else ""}")
    if is_html:
        copy_css_to_blog_output(blog_output_dir)
    for thread in thread_list:
        file_name = thread['slug']
        if not file_name:
            file_name = f"{thread['posts'][0]['blog_name']}_{thread['posts'][0]['id']}"

        save_to_filepath = os.path.join(posts_dir, f'{thread['timestamp']}_{file_name}.{"html" if is_html else "txt"}')

        with open(save_to_filepath, "w", encoding="utf-8") as file:
            if is_html:
                text = f"""
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{thread['timestamp']}_{file_name}</title>
                    <link rel="stylesheet" href="../style.css">
                </head>
                <body>
                <h2>{thread['timestamp']}_{file_name}</h2>
                <h3>{thread['date']}</h3>
                """
            else:
                text = f"{thread['date']}\n\n"

            for post in thread['posts']:
                text += format_post(post, is_html, images_dir, download_images)

            if len(thread['tags']) > 0:
                if is_html:
                    text += f"<p class='tags'>Tags: {', '.join(thread['tags'])}</p>"
                else:
                    text += f"Tags: {', '.join(f"{thread['tags']}")}"

            if is_html:
                text += "<hr /></body></html>"

            file.write(text)
            if not text:
                print(f"Empty thread: {thread}")
    print("Done!")


def format_post(post: Dict[str, Any], is_html: bool = False, images_dir: str = "", download_images: bool = False) -> str:
    listed_url = post['blog_name'] if post['post_position_type'] == 'ask' else f"{post['blog_name']}.tumblr.com/post/{post['id']}"
    if is_html:
        content = post['content'] if not download_image else process_content_for_images(post['content'], images_dir, download_images)
        return f"""
        <hr />
        <h4><strong><a href="https://{listed_url}">{listed_url}</a>:</strong></h4>
        <div class="post-content">
            {content}
        </div>
        """
    else:
        return f"{listed_url}:\n\n{post['content']}\n\n"

def table_of_contents_maker(thread_list: List[Dict[str,Any]], output_dir: str, blog_name: str) -> None:
    sorted_threads = sorted(thread_list, key=lambda x: x['timestamp'])
    table_of_contents = "<html>\n<body>\n<ul>"
    for thread in sorted_threads:
        if len(thread['posts']) > 1:
            current_post = thread['posts'][-1]
            link = f"https://{current_post['blog_name']}.tumblr.com/post/{current_post['id']}"
            table_of_contents += f'\n\t<li><a href="{link}">{thread["slug"]}</a></li>'
    table_of_contents += "\n</ul>\n</body>\n</html>"
    blog_output_dir = os.path.join(output_dir, blog_name)
    save_to_filepath = os.path.join(blog_output_dir, "table_of_contents.html")

    with open(save_to_filepath, "w", encoding="utf-8") as file:
        file.write(table_of_contents)
    print("Table of Contents written!")
