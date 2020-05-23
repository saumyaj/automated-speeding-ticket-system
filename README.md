# automated-speeding-ticket-system

We implemented an end-to-end speed ticketing system which uses a Peer-to-peer network of nodes to process images of speeding cars, notifies the offender about the violation and offers a payment portal for the speeding ticket. We make use of a number of technology concepts such as Peer-to-peer system, blockchain for Decentralized application, machine learning for image processing, IoT for managing nodes and cloud services like Google Pub/Sub and Amazon Rekognition. A database log is maintained which stores details of a ticket such as timestamp, image evidence, speed, amount fined and ticket status, for future reference.

The deployment of the whole application consists of many components. We have described each component in this section

Note-1: You have to replace files in gcloud_creds folder with actual cloud credentials in order to run the end-to-end application

Note-2: You need to have metamask installed in order to run the dapp part of this application

#### 1. Cloud deployments
   Deploy all cloud functions and lambda function code given in the cloud_functions folder on the google cloud and AWS.
   Create two Dynamodb databases
   OwnerInfo
   Tickets
   Create google cloud storage bucket to store captured images

#### 2. p2p Network
   Run deployMessageServer.py given in MessageServerPeer folder to deploy the message node
   Run deploySensor.py to simulate the sensor code given in SensorPeer folder
   Run deploySubscriber.py given in SubscriberPeer folder to simulate subscriber behavior

#### 3. Dapp component
   Create an S3 bucket with appropriate permissions in order to host a public frontend app
   Upload files in the dapp/frontend/dist folder to this bucket.
   Deploy Fine.sol file on a blockchain network using remix browser. Make sure to use web3 injection while deploying.
