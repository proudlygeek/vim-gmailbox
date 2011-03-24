# -*- coding: utf-8 -*-
"""

    Gmailbox
    ~~~~~~~~~~~~~~~~~~

    A Vim plugin for displaying your Gmail inbox
    within your favourite text editor ;)

    :copyright: (c) 2011 by Gianluca Bargelli.
    :license: MIT License, see LICENSE for more details.


"""


import vim
import base64
import urllib2
import xml.etree.cElementTree as etree


def python_input(message, secret=False):
    """
    Acts as a bridge to handle user's inputs from vim to python
    objects; the vim command being called is vim's input() (or alternatively
    inputsecret() if secret is True) and displays a nice message using
    the string passed into the 'message' argument. Finally, it returns
    the previously collected value.

    Example #1:

    user = python_input("Enter your username")

    ~displays~

    Enter your username: _

    Example #2:

    pass = python_input("Enter your password", secret=True)

    Enter your password: _

    ~while the user types~

    Enter your password: ***_

    """
    # Calls vim's input() or inputsecret() (for passwords)
    input_type = "inputsecret" if secret else "input"
    vim.command('call inputsave()')
    vim.command("let user_input = %s('%s: ')" %(input_type, message))
    vim.command('call inputrestore()')
    # Returns the value stored in user_input
    return vim.eval('user_input')


def Gmail_auth(username, password):
    """
    Performs a Basic HTTP Authentication by encoding credentials into an Authentication
    header without the need to get a preliminar 401 Unauthorized error
    (see http://stackoverflow.com/questions/2407126/python-urllib2-basic-auth-problem).
    """
    request = urllib2.Request("https://mail.google.com/mail/feed/atom")
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)

    try:
        feed = urllib2.urlopen(request)
    except IOError as e:
        print e

    return feed


def relative(tag):
    """
    A shortcut method for accessing the namespace of the
    XML file; Python 2.7 or later implements 
    xml.etree.ElementTree.register_namespace(prefix, uri)
    for this task.
    """
    return r"""{http://purl.org/atom/ns#}%s""" % tag


def entry_generator(tree):
    """
    Since the RSS Feed has a fixed structure the method
    heavily relies on simply finding the nodes belonging
    to the same level: shortly, it yields a new dictionary 
    containing at every <entry> tag it finds; this is 
    useful for appending them to a list (see how is called
    in a list comprehension in the main() method).
    """
    for entry in tree.findall(relative("entry")):
        entry_dict = {'title': entry.find(relative("title")).text,
                      'summary': entry.find(relative("summary")).text,
                      'issued': entry.find(relative("issued")).text,
                      'id': entry.find(relative("id")).text,
                      'name': entry.find(relative("author")).find(relative("name")).text,
                      'email': entry.find(relative("author")).find(relative("email")).text}

        yield entry_dict


def print_mailbox(res):
    """
    Pretty prints the parsed feed into a nice (?)
    format. To complete.

    """

    vim.command("vsp new")

    # Some quick lambdas for styling
    longest_line = vim.current.window.width - 1

    margin = lambda x: (longest_line - len(x))/2

    print_key = lambda key, add="": \
            "|" + " " * (margin(res[key]) - (len(add)/2)) \
            + "%s" % (res[key]) \
            + add \
            + " " * (margin(res[key]) - (len(add)/2) - 1) + "|"

    print_text = lambda text: "|" + " " * (margin(text)) + "%s" % text \
                              + " " * (margin(text)) + "|"

    print_line = lambda symbol: " " + symbol * (longest_line - 1)

    # The printing begins here
    vim.current.buffer.append(print_line("-"))
    vim.current.buffer.append(print_key("title"))

    if int(res['fullcount']) > 0:
        vim.current.buffer.append(print_key("tagline", " (%s)" % res['fullcount']))
    else:
        vim.current.buffer.append(print_text("No new messages in your Gmail Inbox"))

    vim.current.buffer.append(print_line("-"))


def main():
    # Ask credentials directly from vim's command line
    username = python_input('Gmail Username')
    password = python_input('Gmail Password', secret=True)

    # Do basic authentication and get the feed
    feed = Gmail_auth(username, password)

    # Parse the feed's xml
    xmltree = etree.parse(feed)

    # Build a dict by hand
    mailbox = {'title': xmltree.find(relative("title")).text,
               'tagline': xmltree.find(relative("tagline")).text,
               'fullcount': xmltree.find(relative("fullcount")).text,
               'link': xmltree.find(relative("link")).items(),
               'modified': xmltree.find(relative("modified")).text,
               'entries': [entry for entry in entry_generator(xmltree)]}

    # Displays the results in vim
    print_mailbox(mailbox)


if __name__ == '__main__':
    main()
