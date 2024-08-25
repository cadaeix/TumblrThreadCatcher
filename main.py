import argparse
import config
import pytumblr

from src.utils import fetch_and_process_posts, save_threads, table_of_contents_maker

OUTPUT_DIR = "outputs"
MAX_POSTS_PER_REQUEST = 20


def main():
    parser = argparse.ArgumentParser(description="Fetch and save Tumblr blog posts.")
    parser.add_argument("blog_name", help="Name of the Tumblr blog to fetch posts from")
    parser.add_argument(
        "--txt", action="store_true", help="Save posts as text files (default is HTML)"
    )
    parser.add_argument("--images", action="store_true", help="Download images locally")
    parser.add_argument(
        "--contents",
        action="store_true",
        help="Generate a table of contents linking to all threads with more than one post",
    )

    args = parser.parse_args()

    blog_identifier = args.blog_name
    save_as_html = not args.txt
    download_images = args.images

    print(f"Fetching posts from: {blog_identifier}")
    print(f"Saving as: {'HTML' if save_as_html else 'Text'}")
    print(f"Downloading images: {'Yes' if download_images else 'No'}")

    client = pytumblr.TumblrRestClient(config.CONSUMER_KEY)

    thread_info = fetch_and_process_posts(client, blog_identifier)
    save_threads(
        thread_info, blog_identifier, OUTPUT_DIR, save_as_html, download_images
    )
    if args.contents:
        table_of_contents_maker(thread_info, OUTPUT_DIR, blog_identifier)


if __name__ == "__main__":
    main()
