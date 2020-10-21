#!/usr/bin/env python3

from PIL import Image, ImageOps
import os
import requests
import io
from angellib import unittests

def getSubIcon(sub):
    """Function to get the icon of a subreddit, and save to a predefined location.

    Args:
        sub (str): The display name (without /r/ prefix) of the subreddit to fetch
            the image for

    Returns:
        str: The fully quantified path of the image
    """
    if os.name != "posix":
        mask = Image.open('{}/Angel/mask.png'.format(os.environ.get("APPDATA", "").replace('\\', '/'))).convert('L')
    else:
        mask = Image.open('/opt/angel-reddit/mask.png').convert('L')
    if sub == "all":
      if os.name != "posix":
          image = Image.open('{}/Angel/default.png'.format(os.environ.get("APPDATA", "").replace('\\', '/')))
      else:
          image = Image.open('/opt/angel-reddit/default.png')
          output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
          output = output.convert('RGBA')
          output.putalpha(mask)
          unittests._test_tempfiles()
    if os.name != "posix":
        try:
            output.save('{0}/Angel/temp/.subimg.{1}'.format(os.environ.get("APPDATA", "").replace('\\', '/'), 'png'))
        except OSError:
            image = Image.open('{}/Angel/default.png'.format(os.environ.get("APPDATA", "").replace('\\', '/'), 'png'))
            output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
            output = output.convert('RGBA')
            output.putalpha(mask)
            output.save('{0}/Angel/temp/.subimg.{1}'.format(os.environ.get("APPDATA", "").replace('\\', '/'), 'png'))
            return '{0}/Angel/temp/.subimg.{1}'.format(os.environ.get("APPDATA", "").replace('\\', '/'), 'png')
        else:
            return '{0}/Angel/temp/.subimg.{1}'.format(os.environ.get("APPDATA", "").replace('\\', '/'), 'png')
    try:
        if 'http' in sub.icon_img:
            image = requests.get(sub.icon_img)
            imageBytes = io.BytesIO(image.content)
            image = Image.open(imageBytes)
            image = image.convert('RGBA')
            if os.environ.get("DEBUG", "") == 'true':
                print(image.mode)
    except:
      try:
          if os.environ.get("DEBUG", "") == 'true':
              print(output.mode)
          output.save('/opt/angel-reddit/temp/.subimg.png')
          return '/opt/angel-reddit/temp/.subimg.png'
      except OSError:
          image = Image.open('/opt/angel-reddit/default.png')
          output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
          output = output.convert('RGBA')
          output.putalpha(mask)
          unittests._test_tempfiles()
          output.save('/opt/angel-reddit/temp/.subimg.png')
          return '/opt/angel-reddit/temp/.subimg.png'
      else:
          return '/opt/angel-reddit/temp/.subimg.png'
