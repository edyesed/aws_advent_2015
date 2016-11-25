from __future__ import print_function
import time
import os
import json
import urlparse
import boto3

DYNAMO_TABLE = os.environ.get('DYNAMO_TABLE', None)

def handler(event, context):
    """
    This function puts into dynamo and get from it.
    """
    message = event['Records'][0]['Sns']['Message']

    print("Started up")
    print("message Below")
    print(message)
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
 
    if DYNAMO_TABLE is None:
        print("This lambda needs the DYNAMO_TABLE environment variable set")
    
    client = boto3.client('dynamodb')
    return_response = {} 
    # 
    #  Now updating the value in Dynamo
    #  This out of band processor adds ten to our word counts
    #  we could also bring this back into slack with an inbound webhook 
    for word in input_text[0].split():
         response = client.update_item(TableName=DYNAMO_TABLE,
                        Key={'word': {'S':  word}},
                        AttributeUpdates={
                           'count': {"Action": "ADD", "Value": {"N": "10"}}
                        },
                        ReturnValues="UPDATED_NEW")
         print("RESPONSE IS ")
         print(response)
         return_response[word] = response['Attributes']['count']['N']
  
    print("We set the values due to out of band updates to %s" % ( return_response))
