'''
Reddit LaTeX Bot
A bot that converts commented LaTeX into an image.

@author: Jake Lane
'''
from threading import Thread
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

    # Parse the configuration
    enviroment_fail = False
    
    username = os.environ.get('reddit_username')
    if username == None:
    	logging.error('Could not load username')
    	enviroment_fail = True
        
    password = os.environ.get('reddit_password')
    if password == None:
    	logging.error('Could not load password')
    	enviroment_fail = True
        
    global Imgur_CLIENT_ID
    Imgur_CLIENT_ID = os.environ.get('imgur_client_id')
    if Imgur_CLIENT_ID == None:
    	logging.error('Could not load Client_ID')
    	enviroment_fail = True
        
    global Imgur_CLIENT_SECRET
    Imgur_CLIENT_SECRET = os.environ.get('imgur_client_secret')
    if Imgur_CLIENT_SECRET == None:
    	logging.error('Could not load SECRET_ID')
    	enviroment_fail = True
    
    subreddits = os.environ.get('reddit_subreddits').split(',')
    if subreddits == None:
    	logging.error('Could not load subreddits')
    	enviroment_fail = True
        
    if not enviroment_fail:
        logging.info('Reddit LaTeX Bot v1 by /u/LeManyman has started')
    else:
        logging.error('Could not start bot.')
        sys.exit(0)
    
    # Initiate things
    global banned_subs
    banned_subs = []
    
    # Login to Reddit
    r = praw.Reddit('LaTeX Bot by u/JakeLane'
                    'Url: https://bitbucket.org/JakeLane/reddit-latex-bot')
    r.config.decode_html_entities = True
    r.login(username, password)
    logging.info('Bot has successfully logged in')
    
    # Define the regex
    regex_old = re.compile('\[(.*\n*)\]\(\/latex\)')
    regex = re.compile(r'\\begin{latex}(.*\n*)\\end{latex}', re.S)
    
    already_done = set()
    
    while True:
        try:
            # Generate the multireddit
            if str(subreddits[0]) != 'all':
                multireddit = ('%s') % '+'.join(subreddits)
                logging.info('Bot will be scanning the multireddit "' + multireddit + '".')
            else:
                all_comments = praw.helpers.comment_stream(r, 'all', limit=None)
                logging.info('Bot will be scanning all of reddit.')
            
            # Start the main loop
            
            while True:
                if str(subreddits[0]) != 'all':
                    subs = r.get_subreddit(multireddit)
                    all_comments = subs.get_comments()
                
                for comment in all_comments:
                    latex = []
                    latex.extend(regex_old.findall(comment.body))
                    latex.extend(regex.findall(comment.body))
                    if latex != [] and comment.id not in already_done:
                        logging.info('Found comment with LaTeX')
                        thread = Thread(target=generate_comment, args=(r, comment, username, already_done, latex,))
                        thread.start()
    
        except Exception as e:
            logging.error(e)
            continue

def generate_comment(r, comment, username, already_done, latex):
    comment_with_replies = r.get_submission(comment.permalink).comments[0]
    for reply in comment_with_replies.replies:
        if reply.author.name == username:
            already_done.add(comment.id)
            logging.info('Comment was already done.')
    if comment.id not in already_done:
        comment_reply = ''
        for formula in latex:
            encoded = urllib.quote('%s' % formula)
            url = 'http://latex.codecogs.com/png.latex?' + encoded
            uploaded_image = imgur_upload(url)
            final_link = uploaded_image.link
            comment_reply = comment_reply + '[Automatically Generated Formula](' + final_link + ')\n\n '
            logging.info('Generated image')
        
        comment_reply = comment_reply + '***\n\n^[About](https://bitbucket.org/JakeLane/reddit-latex-bot/wiki/Home) ^| ^[Report a Bug](https://bitbucket.org/JakeLane/reddit-latex-bot/issues) ^| ^Created ^and ^maintained ^by ^/u/LeManyman'
        comment.reply(comment_reply)
        already_done.add(comment.id)
        logging.info('Successfully posted image. ')

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
    encoded = urllib.quote('%s' % formula)
    joined_url = 'http://latex.codecogs.com/png.latex?' + encoded
    return joined_url

if __name__ == '__main__':
    main()
