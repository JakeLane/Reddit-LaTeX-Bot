'''
Reddit LaTeX Bot
A bot that converts commented LaTeX into an image.

@author: Jake Lane
'''

import ConfigParser
import logging
import os
from os.path import sys
import praw
import pyimgur
import re
from time import sleep
import urllib


def main():
    # Start the logger
    initialize_logger('log')
    # Do not launch if no configuration
    if not os.path.exists('config.cfg'):
        logging.error('No config file.')
        sys.exit()
    logging.info('Reddit LaTeX Bot v1 by /u/LeManyman has started')
    # Parse the configuration
    config = configuration()
    username = config.get('Configuration', 'Username')
    password = config.get('Configuration', 'Password')
    global Imgur_CLIENT_ID
    global Imgur_CLIENT_SECRET
    Imgur_CLIENT_ID = config.get('Configuration', 'Imgur Client ID')
    Imgur_CLIENT_SECRET = config.get('Configuration', 'Imgur Secret ID')
    subreddits = config.get('Configuration', 'Subreddits').split(',')
    
    # Login to Reddit
    r = praw.Reddit('LaTeX Bot by u/JakeLane'
                    'Url: https://bitbucket.org/JakeLane/reddit-latex-bot')
    r.login(username, password)
    logging.info('Bot has successfully logged in')
    
    # Generate the multireddit
    if str(subreddits[0]) != 'all':
        multireddit = ('%s') % '+'.join(subreddits)
        logging.info('Bot will be scanning the multireddit "' + multireddit + '".')
    else:
        all_comments = praw.helpers.comment_stream(r, 'all', limit=None)
        logging.info('Bot will be scanning all of reddit.')
    
    # Define the regex
    regex = re.compile('\[(.*\n*)\]\(\/latex\)')
    
    # Start the main loop
    while True:
        try:
            if str(subreddits[0]) != 'all':
                subs = r.get_subreddit(multireddit)
                all_comments = subs.get_comments()
            
            # Load already done
            already_done = set()
            for comment in all_comments:
                latex = regex.findall(comment.body)
                if latex != [] and comment.id not in already_done:
                    logging.info('Found comment with LaTeX')
                    comment_with_replies = r.get_submission(comment.permalink).comments[0]
                    for reply in comment_with_replies.replies:
                        if reply.author.name == username:
                            already_done.add(comment.id)
                            logging.info('Comment was already done.')
                    if comment.id not in already_done:
                        comment_reply = ''
                        for formula in latex:
                            url = formula_as_url(formula)
                            uploaded_image = imgur_upload(url)
                            final_link = uploaded_image.link
                            comment_reply = comment_reply + '[Automatically Generated Formula](' + final_link + ')\n\n ' 
                        
                        comment_reply = comment_reply + '***\n\n^[About](https://bitbucket.org/JakeLane/reddit-latex-bot/wiki/Home) ^| ^[Source](https://bitbucket.org/JakeLane/reddit-latex-bot/src) ^| ^Created ^and ^maintained ^by ^/u/LeManyman'
                        comment.reply(comment_reply)
                        already_done.add(comment.id)
                        logging.info('Successfully posted image. ')
        except Exception as e:
            logging.error(e)
            sleep(60)
            continue
            
def configuration():
    config = ConfigParser.ConfigParser()
    config.read('config.cfg')
    return config

def initialize_logger(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if not os.path.exists(output_dir + '/all.log'):
        open(output_dir + '/all.log', 'w+').close()
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
     
    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
 
    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(output_dir, "error.log"), "w", encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
 
    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "all.log"), "w")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def imgur_upload(formula_url):
    im = pyimgur.Imgur(Imgur_CLIENT_ID, Imgur_CLIENT_SECRET)
    return im.upload_image(url=formula_url)

def formula_as_url(formula):
    encoded = urllib.quote('\dpi{120} %s' % formula)
    joined_url = 'http://latex.codecogs.com/png.latex?' + encoded
    return joined_url

if __name__ == '__main__':
    main()
