# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import mysql.connector
import sys
import boto3
import os
from datetime import datetime

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import get_supported_interfaces

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HOST = os.getenv('DB_HOST')
USERNAME = os.environ.get('DB_USERNAME')
PASSWORD = os.environ.get('DB_PASSWORD')
DBNAME = os.environ.get('DB_NAME')

rds_host = HOST
user_name = USERNAME
password = PASSWORD
db_name = DBNAME

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, to True Bus Ireland"
        print(f"This is the handler_input {handler_input}")

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello and welcome to my Alexa Skill Application!"

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class FindBusNumIntentHandler(AbstractRequestHandler):
    """Handler for specific bus Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("FindBusNum")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        userDestination = ask_utils.request_util.get_slot_value(handler_input, "destination")
        # print(type(userDestination))

        userDestinationTuple = [userDestination]
        print(userDestinationTuple)

        try:
            conn = mysql.connector.connect(host=rds_host, user=user_name, password=password, database=db_name)

        except mysql.connector.Error as e:
            print("ERROR: Unexpected error: Could not connect to MySQL instance.")
            print(e)
            sys.exit(1)

        print("SUCCESS: Connection to RDS MySQL instance succeeded")

        cursor = conn.cursor()

        selectStopsQuery = """select distinct r.route_short_name from stops s join stop_times st on st.stop_id = s.id join trips t on t.id = st.trip_id join routes r on r.id = t.route_id where stop_name like %s;"""
        print(selectStopsQuery)
        cursor.execute(selectStopsQuery, userDestinationTuple)

        result = cursor.fetchone()
        print(result)
        if result:
            speak_output = "The Bus Number " + ", ".join(result) + " goes to " + userDestination
        else:
            speak_output = "Sorry we could not find this bus stop inside our records. Please remember to say the full name of the bus stop."

        # speak_output = result
        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class NextBusToAreaIntentHandler(AbstractRequestHandler):
    """Handler for specific bus Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("NextBusToArea")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        userDestination = ask_utils.request_util.get_slot_value(handler_input, "location")
        userSoucre = ask_utils.request_util.get_slot_value(handler_input, "soucre")
        print(type(userDestination))
        print(f"userDestination: {userDestination}")

        print(type(userSoucre))
        print(f"userSoucre: {userSoucre}")

        userDestination1 = userDestination
        userSoucre1 = userSoucre
        userSoucre2 = userSoucre

        userData = [userDestination, userSoucre, userDestination1, userSoucre1, userSoucre2]

        try:
            conn = mysql.connector.connect(host=rds_host, user=user_name, password=password, database=db_name)

        except mysql.connector.Error as e:
            print("ERROR: Unexpected error: Could not connect to MySQL instance.")
            print(e)
            sys.exit(1)

        print("SUCCESS: Connection to RDS MySQL instance succeeded")

        cursor = conn.cursor()

        selectStopsQuery = \
            f""" with all_trips as (
                    select * 
                    from trips t 
                    where t.id in (select trip_id from stops_info where stop_name like %s ) 
                        and t.id in (select trip_id from stops_info where stop_name like %s )
                ), cte as(
                    select t.* 
                    from all_trips t 
                        join stops_info s1 on t.id = s1.trip_id and s1.stop_name like %s 
                        join stops_info s2 on t.id = s2.trip_id and s2.stop_name like %s
                    where s2.stop_sequence < s1.stop_sequence
                ) 
                select min(arrival_time)
                from cte c
                    join stops_info s on c.id = s.trip_id
                where stop_name like %s and arrival_time > CONVERT_TZ(current_time(), 'UTC', 'Europe/Dublin');"""
        print(selectStopsQuery)
        cursor.execute(selectStopsQuery, userData)

        result = cursor.fetchone()
        print(result)
        print(type(result))
        if result == (None,):
            speak_output = "Sorry there currently isn't any buses running from "+ userDestination + " and " + userSoucre + ". Please try again later."
        elif result:
            item = result[0]
            item = str(item)
            hour = item[:2]
            if str.__contains__(hour, ':'):
                hour = item[:1]
            else:
                hour = item[:2]
            minutes = item[3:5]
            newTime = f"{hour}:{minutes}"
            print(newTime)
            speak_output = "The next bus to " + userDestination + " is at " + newTime
        else:
            speak_output = "Sorry we could not find "+ userDestination + " on our records. Please try again, with the specific and full name of your intended bus stop."

        # speak_output = result
        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class HowLongToArriveByBusToAreaIntentHandler(AbstractRequestHandler):
    """Handler for specific bus Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HowLongToArriveByBusToArea")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        userDestination = ask_utils.request_util.get_slot_value(handler_input, "locationA")
        userSoucre = ask_utils.request_util.get_slot_value(handler_input, "locationB")
        print(type(userDestination))
        print(f"userDestination: {userDestination}")

        print(type(userSoucre))
        print(f"userSoucre: {userSoucre}")

        userDestination1 = userDestination
        userSoucre1 = userSoucre
        userSoucre2 = userSoucre

        userData = [userDestination, userSoucre, userDestination1, userSoucre1, userSoucre2]

        try:
            conn = mysql.connector.connect(host=rds_host, user=user_name, password=password, database=db_name)

        except mysql.connector.Error as e:
            print("ERROR: Unexpected error: Could not connect to MySQL instance.")
            print(e)
            sys.exit(1)

        print("SUCCESS: Connection to RDS MySQL instance succeeded")

        cursor = conn.cursor()

        selectStopsQuery = \
            f""" with all_trips as (
                    select * 
                    from trips t 
                    where t.id in (select trip_id from stops_info where stop_name like %s) 
                        and t.id in (select trip_id from stops_info where stop_name like  %s)
                ), cte as(
                    select t.id as trip_id, s2.stop_name as src_stop, s2.arrival_time as src_time, s1.stop_name as dest_stop, s1.arrival_time as dest_time
                    from all_trips t 
                        join stops_info s1 on t.id = s1.trip_id and s1.stop_name like  %s
                        join stops_info s2 on t.id = s2.trip_id and s2.stop_name like  %s
                    where s2.stop_sequence < s1.stop_sequence
                ) 
                select min(timediff(dest_time, src_time))
                from cte c
                    join stops_info s on c.trip_id = s.trip_id
                where stop_name like %s and arrival_time > CONVERT_TZ(current_time(), 'UTC', 'Europe/Dublin');"""
        print(selectStopsQuery)
        cursor.execute(selectStopsQuery, userData)

        result = cursor.fetchone()
        print(result)
        if result == (None,):
            speak_output = "Sorry we could not find any direct buses running from "+ userDestination + " and " + userSoucre + ". Please try again later and remember to include bus stops on the same route only."
        elif result:
            item = result[0]
            item = str(item)
            hour = item[:2]
            minutes = item[3:5]
            newTime = ""
            if str.__contains__(hour, ':'):
                hour = item[:1]
            else:
                hour = item[:2]
                newTime = f"{hour} hours {minutes} minutes"
                print(newTime)

            if int(hour) < 1:
                newTime = f"{minutes} minutes"
                print(newTime)
            # print(newTime)
            speak_output = "The journey time between " + userDestination + " and " + userSoucre + " is " + newTime
        else:
            speak_output = "Sorry we could not find a trip between "+ userDestination + " and" + userSoucre + " on our records. Please try again, with the full name of your intended bus stop."

        # speak_output = result
        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class ArriveByBusToAreaIntentHandler(AbstractRequestHandler):
    """Handler for specific bus Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ArriveByBusToArea")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        userDestination = ask_utils.request_util.get_slot_value(handler_input, "location")
        userSoucre = ask_utils.request_util.get_slot_value(handler_input, "source")
        userTime = ask_utils.request_util.get_slot_value(handler_input, "time")
        print(type(userDestination))
        print(f"userDestination: {userDestination}")

        print(type(userSoucre))
        print(f"userSoucre: {userSoucre}")

        userDestination1 = userDestination
        userSoucre1 = userSoucre
        userSoucre2 = userSoucre

        userData = [userDestination, userSoucre, userDestination1, userSoucre1, userSoucre2, userTime]

        try:
            conn = mysql.connector.connect(host=rds_host, user=user_name, password=password, database=db_name)

        except mysql.connector.Error as e:
            print("ERROR: Unexpected error: Could not connect to MySQL instance.")
            print(e)
            sys.exit(1)

        print("SUCCESS: Connection to RDS MySQL instance succeeded")

        cursor = conn.cursor()

        selectStopsQuery = \
            f"""with all_trips as (
            	select * 
            	from trips t 
            	where t.id in (select trip_id from stops_info where stop_name like %s) 
            		and t.id in (select trip_id from stops_info where stop_name like %s)
            ), cte as(
            	select t.id as trip_id, s2.stop_name as src_stop, s2.departure_time as src_time, s1.stop_name as dest_stop, s1.arrival_time as dest_time
                , s2.arrival_time as abc
            	from all_trips t 
            		join stops_info s1 on t.id = s1.trip_id and s1.stop_name like %s
            		join stops_info s2 on s1.trip_id = s2.trip_id and s2.stop_name like %s
            	where s2.stop_sequence < s1.stop_sequence
            ) 
            select c.src_time
            from cte c
            	join stops_info s on c.trip_id = s.trip_id
            where stop_name like %s and departure_time < %s
            order by dest_time desc limit 1;"""
        print(selectStopsQuery)
        cursor.execute(selectStopsQuery, userData)

        result = cursor.fetchone()
        print(result)
        if result == (None,):
            speak_output = "Sorry there currently isn't any buses running from "+ userDestination + " and " + userSoucre + ". Please try again later."
        elif result:
            item = result[0]
            item = str(item)
            hour = item[:2]
            if str.__contains__(hour, ':'):
                hour = int(item[:1])
            else:
                hour = int(item[:2])
            minutes = item[3:5]
            newTime = f"{hour}:{minutes}"
            print(newTime)
            speak_output = "If you want to arrive at " + userDestination + " from " + userSoucre + " at " + userTime + ", You will need to take the bus at " + newTime 
        else:
            speak_output = "Sorry we could not find bus stop on our records. Please try again, with the full name of your intended bus stop."

        # speak_output = result
        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class DepartByBusToAreaIntentHandler(AbstractRequestHandler):
    """Handler for specific bus Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("DepartByBusToArea")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        userDestination = ask_utils.request_util.get_slot_value(handler_input, "location")
        userSoucre = ask_utils.request_util.get_slot_value(handler_input, "source")
        userTime = ask_utils.request_util.get_slot_value(handler_input, "time")
        print(type(userDestination))
        print(f"userDestination: {userDestination}")

        print(type(userSoucre))
        print(f"userSoucre: {userSoucre}")

        userDestination1 = userDestination
        userSoucre1 = userSoucre
        userSoucre2 = userSoucre

        userData = [userDestination, userSoucre, userDestination1, userSoucre1, userSoucre2, userTime]

        try:
            conn = mysql.connector.connect(host=rds_host, user=user_name, password=password, database=db_name)

        except mysql.connector.Error as e:
            print("ERROR: Unexpected error: Could not connect to MySQL instance.")
            print(e)
            sys.exit(1)

        print("SUCCESS: Connection to RDS MySQL instance succeeded")

        cursor = conn.cursor()

        selectStopsQuery = \
            f"""with all_trips as (
                	select * 
                	from trips t 
                	where t.id in (select trip_id from stops_info where stop_name like %s) 
                		and t.id in (select trip_id from stops_info where stop_name like %s)
                ), cte as(
                	select t.id as trip_id, s2.stop_name as src_stop, s2.arrival_time as src_time, s1.stop_name as dest_stop, s1.arrival_time as dest_time
                	from all_trips t 
                		join stops_info s1 on t.id = s1.trip_id and s1.stop_name like %s
                		join stops_info s2 on t.id = s2.trip_id and s2.stop_name like %s
                	where s2.stop_sequence < s1.stop_sequence
                ) 
                select distinct src_time
                from cte c
                	join stops_info s on c.trip_id = s.trip_id
                where stop_name like %s and arrival_time > %s
                order by dest_time asc;"""
        print(selectStopsQuery)
        cursor.execute(selectStopsQuery, userData)

        result = cursor.fetchone()
        print(result)
        if result == (None,):
            speak_output = "Sorry there currently isn't any buses running from "+ userDestination + " and " + userSoucre + ". Please try again later."
        elif result:
            item = result[0]
            item = str(item)
            hour = item[:2]
            if str.__contains__(hour, ':'):
                hour = int(item[:1])
            else:
                hour = int(item[:2])
            minutes = item[3:5]
            newTime = f"{hour}:{minutes}"
            print(newTime)
            speak_output = "If you want to depart from " + userSoucre + " at " + userTime + ", You will need need to take the bus at " + newTime + " for the bus going to " + userDestination
        else:
            speak_output = "Sorry we could not find this bus stop on our records. Please try again, with the full name of your intended bus stop."

        # speak_output = result
        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FindBusNumIntentHandler())
sb.add_request_handler(NextBusToAreaIntentHandler())
sb.add_request_handler(HowLongToArriveByBusToAreaIntentHandler())
sb.add_request_handler(ArriveByBusToAreaIntentHandler())
sb.add_request_handler(DepartByBusToAreaIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
