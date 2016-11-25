from __future__ import print_function
import time
import os
import json
import urlparse
import boto3

def handler(event, context):
    """
    This function puts into dynamo and get from it.
    """
    message = event['Records'][0]['Sns']['Message']

    # xxx print("Started up")
    # xxx print("message Below")
    # xxx print(message)
    # xxx print("CONTEXT")
    # xxx print(context)
    # xxx print(dir(context))
    #
    # there is some jiggery pokery required to be able to accept any
    # input from slack, which provides not json input but query params
    #
    url_to_parse = 'http://fake.url.com/?message='+ message
    parsed = urlparse.urlparse(url_to_parse)
    input_text = urlparse.parse_qs(parsed.query)['message']
 
    
    # Just log here, but we could do more
    #  we could also bring this back into slack with an inbound webhook 
    for word in input_text[0].split():
         print("LOG THIS WORD: %s" % (word))
  
    print("This function could do much more than log")
