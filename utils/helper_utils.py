import base64
import copy
import json
import os
from dotenv import load_dotenv
from flask import request, make_response, Response
from urllib.parse import parse_qs
from twilio.twiml.messaging_response import MessagingResponse
from api.api_core import mc, fcm


def __prepareOutputResponse(myResult) -> Response:
    res = json.dumps(myResult, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def sendWebhookCallback(botMessage: str) -> Response:
    myResult = {
        "source": "dialogFlow",
        "fulfillmentText": botMessage
    }
    return __prepareOutputResponse(myResult)


def changeDialogflowIntent(newIntent: str = None, parameters: dict = None) -> Response:
    myResult = {
        "followupEventInput": {
            "name": newIntent,
            "languageCode": "pt-BR",
            "parameters": parameters or {},
        }}
    return __prepareOutputResponse(myResult)


def changeDialogflowContext(newContext: str = None, parameters: dict = None) -> Response:
    myResult = {
        "outputContexts": [
            {
                "name": newContext,
                "lifespanCount": 1,
                "parameters": parameters or {},
            }
        ]
    }
    return __prepareOutputResponse(myResult)


def getDialogFlowAuth():
    load_dotenv()
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    auth_string = f"{account_sid}:{auth_token}"
    base64_auth_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    print(base64_auth_string)


def extractDictFromBytesRequest():
    payload = request.get_data()
    stringData = payload.decode('utf-8')
    return parse_qs(stringData)


def getJsonCredentialsData() -> dict:
    dialogflowJsonFilePath = os.path.join(os.getcwd(), 'dialogflow.json')
    with open(dialogflowJsonFilePath, 'r') as f:
        return json.load(f)


def __getAllUsersMappedByPhone() -> dict:
    """Retrieve all users from the Firebase and map them by phone number."""
    users = fu.getAllUsers()
    return {user["phoneNumber"]: user for user in users.values()} if users is not None else {}


def __getUserByWhatsappNumber(whatsappNumber: str) -> dict or None:
    """Returns a dict like this:
        {'address': 'Rua das Flores 4984',
        'cpf': '14587544589',
        'name': 'João',
        'phoneNumber': '+5585997548654'}"""
    users = __getAllUsersMappedByPhone()
    return users.get(whatsappNumber)


def __detectIncomingMessage(userMessage: dict) -> dict:
    twilioKeys = ['AccountSid', 'SmsMessageSid', 'NumMedia', 'ProfileName', 'SmsSid', 'WaId', 'SmsStatus', 'To',
                  'NumSegments', 'ReferralNumMedia', 'MessageSid', 'AccountSid', 'From', 'ApiVersion']
    incomingKeys = set(userMessage.keys())
    commonKeys = incomingKeys.intersection(twilioKeys)
    isTwilio = len(commonKeys) / len(twilioKeys) > 50 / 100
    if isTwilio:
        return __processTwilioIncomingMessage(userMessage)


def __addBotMessageToFirebase(phoneNumber, userMessageJSON):
    msgDict = copy.deepcopy(userMessageJSON)
    msgDict["sender"] = "ChatBot"
    fcm.appendMessageToWhatsappNumber(msgDict, phoneNumber)


def sendTwilioResponse(body: str, media: str = None) -> str:
    response = MessagingResponse()
    message = response.message()
    message.body(body)
    if media is not None:
        message.media(media)
    return str(response)


def __processTwilioIncomingMessage(twilioMessage: dict):
    userMessageJSON = mc.convertUserMessage(twilioMessage)
    return {"userMessageJSON": userMessageJSON, "phoneNumber": userMessageJSON["phoneNumber"],
            "receivedMessage": userMessageJSON["body"]}


def __main():
    return


if __name__ == '__main__':
    __main()