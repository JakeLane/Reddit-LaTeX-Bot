'''
Reddit LaTeX Bot v2
A bot that converts commented LaTeX into an image.

@author: Jake Lane
'''

from threading import Thread
import os
import praw
import pyimgur
import re
import urllib

def main():
    username = os.environ.get('latexbot_reddit_username')        
    password = os.environ.get('latexbot_reddit_password')

    global imgur_CLIENT_ID, imgur_CLIENT_SECRET
    imgur_CLIENT_ID = os.environ.get('latexbot_imgur_client_id')
    imgur_CLIENT_SECRET = os.environ.get('latexbot_imgur_client_secret')
    
    print('LaTeX Bot v2 by /u/JakeLane has started')
        
    # Login to Reddit
    r = praw.Reddit('LaTeX Bot v2 by /u/JakeLane Url: https://bitbucket.org/JakeLane/reddit-latex-bot')
    r.config.decode_html_entities = True # Translate html entities to normal text
    r.login(username, password)
    print('Bot has successfully logged in')
    
    # Define the regex
    regex = re.compile(r'\\begin{tex}(.*?\n*?)\\end{tex}', re.S) # Detects any comment with \begin{tex} and \end{tex}
    
    already_done = set() # Intialise a list of comments already done (to stop any duplicates if the Reddit API messes up)
    
    while True:
        for comment in praw.helpers.comment_stream(r, 'all', limit=None): # For every new comment
            latex = []
            latex.extend(regex.findall(comment.body)) # For each formula found, add to the list
            if latex != [] and comment.id not in already_done: # If there is a formula and it is not already done
                try:
                    print('Found comment with LaTeX')
                    thread = Thread(target=generate_comment, args=(r, comment, username, already_done, latex))
                    thread.start() # Make a new thread to parse the comment
                except Exception as e:
                    print("The show must go on: " + e)
                    continue

def formula_as_url(formula):
    encoded = urllib.quote('%s' % formula)
    joined_url = 'http://latex.codecogs.com/png.latex?' + encoded
    return joined_url                

def imgur_upload(formula_url):
    im = pyimgur.Imgur(imgur_CLIENT_ID, imgur_CLIENT_SECRET)
    return im.upload_image(url=formula_url)

def generate_comment(r, comment, username, already_done, latex):
    comment_with_replies = r.get_submission(comment.permalink).comments[0]
    for reply in comment_with_replies.replies:
        if reply.author.name == username:
            already_done.add(comment.id)
            print('Comment was already done.')
    
    if comment.id not in already_done:
        comment_reply = ''
        try:
            for formula in latex:
                encoded = urllib.quote('%s' % formula)
                url = 'http://latex.codecogs.com/png.latex?' + encoded
                uploaded_image = imgur_upload(url)
                final_link = uploaded_image.link
                comment_reply = comment_reply + '[Automatically Generated Formula](' + final_link + ')\n\n '
                print('Generated image')
            
            comment_reply = comment_reply + '***\n\n[^About](https://bitbucket.org/JakeLane/reddit-latex-bot/) ^| [^Report ^a ^Bug](https://bitbucket.org/JakeLane/reddit-latex-bot/issues) ^| ^Created ^and ^maintained ^by ^/u/JakeLane'
            comment.reply(comment_reply)
            print('Successfully posted image.')
        except HTTPError as e:
            print("HTTPError: Most likely banned from the subreddit")
        already_done.add(comment.id)

if __name__ == '__main__':
    main()
