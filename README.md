# Final Year Project: True Bus Ireland

This project is an Alexa Skill that provides users with real-time bus information from the GTFS-R API released by the National Transport Authority in Ireland.
It was created as part of the final year degree program at Munster Technological University.

The skill can be accessed on the Alexa Store at the following link:
[Amazon Store Page](https://www.amazon.co.uk/dp/B0C3W2DXLX/)

## Features

True Bus supports the following example queries:

- "Alexa ask True Bus what buses go to Macroom"
- "Alexa ask True Bus what time is the next bus to Mardyke Walk from MTU"
- "Alexa ask True Bus I want to arrive at Grand Parade from Victoria Cross at 3pm when should I leave"
- "Alexa ask True Bus I want to depart to Grand Parade from Victoria Cross at 4pm when should I leave"
- "Alexa ask True Bus How long is the journey between Victoria Cross and Grand Parade"

## Project Structure

The repository contains two folders:

1. Alexa Skill - This folder contains the files hosted on the Alexa Developer Console, including the lambda function used to call the intents when the user talks with Alexa.
2. Lambda Function - This folder contains the lambda function hosted on Amazon Web Services console. This function calls the GTFS API to get the latest real-time bus information and stores it inside the RDS Database.

The **thesis.pdf** file contains the analysis and research done for this project, as well as the conclusions.

## Installation

To run this project, you need to follow these steps:

1. Clone this repository.
2. Set up an Alexa Developer Account, and create a new Alexa Skill using the files in the **Alexa Skill** folder.
3. Set up an Amazon Web Services account, and deploy the lambda function contained in the **Lambda Function** folder.
4. Update the necessary credentials in the lambda function code.
5. You're all set! You can now interact with True Bus on your Alexa device.

## Conclusion
True Bus is an Alexa Skill that provides users with real-time bus information in Ireland.
It was created as part of the final year degree program at Munster Technological University, and it demonstrates the potential for voice-controlled interfaces to provide useful services to users.
