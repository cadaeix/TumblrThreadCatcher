import argparse
import config
import pytumblr

from src.utils import fetch_and_process_posts, table_of_contents_maker

OUTPUT_DIR = "outputs"
MAX_POSTS_PER_REQUEST = 20


def main():
    parser = argparse.ArgumentParser(description="Fetch and save Tumblr blog posts.")
    parser.add_argument("blog_name", help="Name of the Tumblr blog to fetch posts from")

    args = parser.parse_args()

    blog_identifier = args.blog_name

    print(f"Fetching posts from: {blog_identifier}")

    client = pytumblr.TumblrRestClient(config.CONSUMER_KEY)

    thread_info = fetch_and_process_posts(client, blog_identifier)
    table_of_contents_maker(thread_info, OUTPUT_DIR, blog_identifier)


if __name__ == "__main__":
    main()
