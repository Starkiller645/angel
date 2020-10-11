#!/usr/bin/env python3

"""Extension library of angellib containing class-agnostic helper functions.

Functions:
    getSubIcon(str): Fetches the icon of a given subreddit, and returns the image path.
        See subicon.py

Classes:
    MarkdownText (str): Intialise class with the Markdown text to convert, then
        take the output of the parse() function

"""

__all__ = ["subicon", "markdownparse", "modprawini"]
