# aws_advent_2016

* We're going to make a collection of widgets that count words. It'll be triggered by Slack ( or a `curl` call to AWS API Gateway ).
* The API Gateway will call a Lambda Function that will split whatever text it is given into specific words
      * A) Upsert a key in a dynamodb table with the number 1
      * B) Drop a message on a SNS Topic
* The SNS Topic will have two lambdas attached to it that will
      * A) upsert the same keys in the dynamodb with the number 10
      * B) log a message to CloudWatchLogs

It looks like this picture here ![diagram here](https://github.com/edyesed/aws_advent_2016/raw/master/img/AWS_Advent_Diagram.png "AWS Advent chat thing")

Example code for AWS Advent near-code-free pubsub. 
Technologies you'll use
* Slack  ( outgoing webhooks )
* API Gateway
* IAM
* SNS
* Lambda
* DynamoDB

# Pub/Sub is teh.best.evar* ( *for some values of best )
I came into the world of computing by way of *The Operations Path*.  The [Publish-Subscribe Pattern](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) has always been near and dear to my ❤️. 

There are a few things about pubsub that I really appreciate as an "infrastructure person". 
     1. Scalability. In the pubsub pattern, scalability is largely a concern of of the message brokers.  The brokers are ( hopefully ) observable. They have known boundaries of scale and known methods by which capacity or throughput can be modified.  They can handle more volume, or handle the volume they have more effienciently without having to get into code.
     1. Loose Coupling. In the happy path, publishers don't know anything about what subscribers are doing with the messages they publish.  There's admittedly a little hand-waving here, and folks new to pubsub (and sometimes those that are experienced ) get rude suprises as messages mutate over time.
     1. Asynchronous. This is not necessarily inherent in the pubsub pattern, but it's the most common implementation that I've seen.  There's quite a lot of pressure that can be absent from Dev Teams, Operations Teams, or DevOps Teams when there is no expectation from the business that systems will retain single millisecond response times.
     1. New Cloud Ways. Once upon a time, we needed to queue messages in pubsub systems ( and you might you might still have a need for that feature ), but with Lambda, we can also invoke consumers _on demand_ as messages pass through our system. We don't have necessarily keep things in the queue at all. Message appears, processing code runs, everybody's happy.

# Yo dawg, I heard you like ️☁️
One of the biggest benefits that we can enjoy from being hosted with AWS is *not having to manage stuff*.  Running your own message bus might be something that separates your business from your competition, but it might also be _undifferentiated heavy lifting_.  IMO, if AWS can and will handle scaling issues for you ( to say nothing of only paying for the transactions that you use ), then it might be the right choice for you to let them take care of that for you.

I would also like to point out that running these things without servers isn't quite the same thing as running them simply.  I ended up redoing this implementation a few times as I kept finding the rough edges of running things serverless. All were ultimately addressable, but I wanted to keep the complexity of this down somewhat.


# WELCOME TO THE FUTURE, FRIENDS
`TL;DR` GIMMIE SOME EXAMPLES
CloudFormation is pretty well covered by [AWS Advent](awsadvent.tumblr.com), we'll configure this little diddy via the AWS console. 


## Get the first lambda setup
### Setup the DynamoDB [![Video to DynamoDB Create](https://img.youtube.com/vi/ww3aSExgkRM/1.jpg)](https://youtu.be/ww3aSExgkRM "Make a DynamoDB")
    1. Console
    1. DynamoDB
    1. Create Table
        1. Table Name `table`
        1. Primary Key `word`
        1. `Create`

### Setup the First Lambda [![Video to Create the first Lambda](https://img.youtube.com/vi/7gkmqYd6v8w/1.jpg)](https://youtu.be/7gkmqYd6v8w "Make The First Lambda to accept outgoing slack webhooks")
1. Make the first lambda, which accepts slack outgoing webook input, and saves that in DynamoDB
    1. Console
    1. lambda
    1. Get Started Now
    1. Select Blueprint
        1. Blank Function
    1. Configure Triggers
        1. Click in the empty box
        1. Choose API Gateway
    1. API Name
        1. aws_advent ( This will be the /PATH of your API Call )
    1. Security
        1. Open 
    1. Name
        1. aws_advent
    1. Runtime
        1. Python 2.7
    1. Code Entry Type
        1. Inline
        1. It's included as [app.py](src/aws_advent_apigw_dynamo_sns/app.py) in this repo. [There are more Lambda Packaging Examples here](http://docs.aws.amazon.com/lambda/latest/dg/vpc-ec-deployment-pkg.html)
    1. Environment Variables
        1. `DYNAMO_TABLE` = `table`
    1. Handler
        1. app.handler
    1. Role
        1. Create new role from template(s)
    1. Policy Templates
        1. Simple Microservice permissions
    1. Triggers
        1. API Gateway
        1. `save the URL`

        
### Link it to your favorite slack [![Video for setting up the slack outbound wehbook](https://img.youtube.com/vi/fnt78n2tvak/1.jpg)](https://youtu.be/fnt78n2tvak "Setup the slack outgoing webhook")
1. Setup an outbound webhook in your favorite slack team.
    1. Manage
    1. search
          1. outgoing wehbooks
    1. channel ( optional )
    1. trigger words
        1. awsadvent
    1. URLs
        1. Your API Gateway Endpoint on the lambda from above
    1. Customize Name
        1. awsadvent-bot

1. Go to slack
     1. join the room
     1. say the trigger word
     1. You should see ![something like this](https://github.com/edyesed/aws_advent_2016/raw/master/img/AWS_Advent_Diagram.png "First post of the awsadvent bot")


## ☝️☝️ CONGRATS YOU JUST DID CHATOPS ☝️☝️

*** 


# Ok. now we want to do the awesome pubsub stuff
1. Make the SNS Topic
    1. Console
    1. SNS
    1. New Topic
    1. Name `awsadvent`
    1. Note your topic ARN
           arn:aws:sns:us-west-2:488887740717:awsadvent

    1. Go back and twiddle the IAM permissions on the role for the first lambda
         1. Console
         1. IAM
         1. Roles `aws_advent_lambda_dynamo`

             ```
{
   "Version":"2012-10-17",
   "Statement":[{
      "Effect":"Allow",
      "Action":"sns:Publish",
      "Resource":"arn:aws:sns:*:*:awsadvent"
      }
   ]
}
     ```

1. Make the multiplier lambda
    1. Console
    1. lambda
    1. Create a Lambda function
    1. Select Blueprint
        1. search sns
        1. `sns-message` python2.7 runtime
    1. Configure Triggers
        1. SNS topic
           1. `awsadvent`
        1. click `enable trigger`
    1. Name
        1. aws_advent_sns_multiplier
    1. Runtime
        1. Python 2.7
    1. Code Entry Type
        1. upload a zip file
        1. It's included as [sns_multiplier.zip](src/sns_multiplier/sns_multiplier.zip) in this repo.
    1. Handler
        1. sns_multiplier.handler
    1. Role
        1. Create new role from template(s)
    1. Policy Templates
        1. Simple Microservice permissions
    1. Next
    1. Create Function

