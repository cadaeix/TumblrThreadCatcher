# TumblrThreadCatcher

Commandline tool to download text posts from Tumblr and "stitch" posts with reblog chains in chronological order together for archival purposes, primarily intended for roleplay blogs with text heavy reblog chains but also has the option to download images locally.

## Features

- Fetch text, answer, and photo posts from a specified Tumblr blog
- Save posts as HTML (default) or plain text files with only blog urls as headers
- Option to download and save images locally
- Generated HTML files can be opened in a browser (eg. Firefox, Chrome, etc), with a little bit of custom formatting to try and reflect some of Tumblr's custom styling
- Option to generate a "table of contents" html file that links chronologically to all posts that have more than one post in the reblog chain (plus accidentally every ask) for thread conversation archival purposes

## TODO

- Currently only retrieves text, ask and photo posts, supporting other types
- Not yet updated to deal with very large blogs with very long histories, only tested on fairly new blogs, may hit rate limits and die without saving anything
- Does not support archiving before/after a certain date yet

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/tumblr-thread-catcher.git
   cd tumblr-thread-catcher
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create a `config.py` file in the project directory with your Tumblr API credentials:

   ```python
   CONSUMER_KEY = 'your_consumer_key_here'
   ```

   You can obtain a Tumblr API key by registering your application at https://www.tumblr.com/oauth/apps - this program won't be using the OAuth authorisation, but it still needs one.

## Usage

Run the script from the command line with the following syntax:

```
python tumblr_thread_catcher.py <blog_name> [--txt] [--images]
```

Arguments:

- `blog_name`: The name of the Tumblr blog you want to fetch posts from (required)
- `--txt`: Save posts as text files instead of HTML (optional)
- `--images`: Download images locally (optional)
- `--contents`: Creates `table_of_contents.html` that is a list of all posts with more than one threaded conversation (plus accidentally every ask) (optional)

Examples:

- To fetch posts from "example-blog" and save as HTML with locally downloaded images:

  ```
  python main.py example-blog
  ```

- To fetch posts from "example-blog" and save as text files without downloading images:
  ```
  python main.py example-blog --txt
  ```

If you want to just run the table of contents cataloguer without saving any posts, just run

```
python cataloguer.py example-blog
```

## Output

The script will create an `outputs` directory with the following structure:

```
outputs/
    <blog_name>/
        style.css
        posts/
            <timestamp>_<post_slug>.html (or .txt)
        images/
            <image_files>
```

## Acknowledgements

This project was developed in collaboration with Claude.ai (I wrote most of the code and then had Claude pretty it up and refactor it).

## License

This project is open sourced under the Unlicense.
