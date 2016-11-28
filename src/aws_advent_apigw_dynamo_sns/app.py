from __future__ import print_function
import time
import os
import json
import urlparse
import boto3

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', None)
DYNAMO_TABLE = os.environ.get('DYNAMO_TABLE', None)

#
def handler(event, context):
    """
    This function puts into DynamoDB and get from it.
    """
    # xxx print("Started up")
    # xxx print("EVENT")
    # xxx print(event)
    # xxx print("CONTEXT")
    # xxx print(context)
    # xxx print(dir(context))
    #
    # there is some jiggery pokery required to be able to accept any
    # input from slack, which provides not json input but query params
    #
    url_to_parse = 'http://fake.url.com/?' + event['body']
    parsed = urlparse.urlparse(url_to_parse)
    input_text = urlparse.parse_qs(parsed.query)['text']
    slack_keyword = urlparse.parse_qs(parsed.query)['trigger_word']

    if DYNAMO_TABLE is None:
        return {'statusCode': 200,
                'headers': {
                   'x-api-gateway': 'well hidden secret format for lambda proxy responses'
                },
                'body': json.dumps({'text': 'You need to set the DYNAMO_TABLE env variable on this lambda',
                                    'username': urlparse.parse_qs(parsed.query)['user_name']
                               })
                }

    client = boto3.client('dynamodb')
    return_response = {}
    # now we save into redis ( or update if it already exists )
    for word in input_text[0].split():
         # xxx print("Checking on %s" % ( word ))
         response = client.update_item(TableName=DYNAMO_TABLE,
                        Key={'word': {'S':  word}},
                        AttributeUpdates={
                           'count': {"Action": "ADD", "Value": {"N": "1"}}
                        },
                        ReturnValues="UPDATED_NEW")
         print("RESPONSE IS ")
         print(response)
         return_response[word] = response['Attributes']['count']['N']
    
    # 
    # Publish to SNS directly. Lambdas can't run in a VPC and talk to
    # the API Gateway without a NAT Gateway in the VPC, so we're gonna
    # Call SNS Directly
    # 
    if SNS_TOPIC_ARN is not None:
       try:
           print("publishing to %s - %s" % (SNS_TOPIC_ARN, input_text[0]))
           client = boto3.client('sns')
           response = client.publish(
                      TopicArn = SNS_TOPIC_ARN,
                      Message = input_text[0])
       except Exception as e:
           print("Ended up with this exception: %s " % (e))

    # yeah, the return is a little gnarly, I want to be sure it's a string
    # xxx print("response is %s" % ( response))
    # OMGWTFBBQ magic return structure for proxy lambdas
    # http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-set-up-simple-proxy.html#api-gateway-simple-proxy-for-lambda-output-format
    return {'statusCode': 200,
            'headers': {
               'x-api-gateway': 'well hidden secret format'
              },
            'body': json.dumps({'text': str([(k, return_response[k]) for k in return_response]),
                                'username': urlparse.parse_qs(parsed.query)['user_name']
                               })
           }
