import logging

from data.message_converter import MessageConverter
from intentManipulation.intent_manager import IntentManager
from socketEmissions.socket_emissor import pulseEmit
from api.api_core import dialogFlowInstance, socketInstance
from utils.helper_utils import sendTwilioResponse, __processTwilioIncomingMessage


def __preprocessIncomingMessage(data: dict):
    print("Preprocess Incoming Message")
    processedData = __processTwilioIncomingMessage(data)
    userMessageJSON = processedData["userMessageJSON"]
    phoneNumber = processedData["phoneNumber"]
    receivedMessage = processedData["receivedMessage"]
    return userMessageJSON, phoneNumber, receivedMessage


def __checkUserRegistration(phoneNumber: str):
    im = IntentManager()
    needsToSignUp = not im.existingWhatsapp(phoneNumber)
    return needsToSignUp


def __handleNewUser(phoneNumber: str, receivedMessage: str):
    logging.info("Needs to sign up!")
    im = IntentManager()
    im.extractedParameters["phoneNumber"] = phoneNumber
    botAnswer = im.twilioSingleStep(receivedMessage)
    dialogflowResponseJSON = MessageConverter.convert_dialogflow_message(botAnswer, phoneNumber)
    output = {
        "body": botAnswer,
        "formattedBody": sendTwilioResponse(body=botAnswer)
    }
    return output, dialogflowResponseJSON


def __handleExistingUser(phoneNumber: str, receivedMessage: str):
    logging.info("Already signup!")
    dialogflowResponse = dialogFlowInstance.getDialogFlowResponse(receivedMessage)
    dialogflowResponseJSON = MessageConverter.convert_dialogflow_message(
        dialogflowResponse.query_result.fulfillment_text, phoneNumber)
    output = {
        "body": dialogflowResponse.query_result.fulfillment_text,
        "formattedBody": dialogFlowInstance.extractTextFromDialogflowResponse(dialogflowResponse)
    }
    return output, dialogflowResponseJSON


def processTwilioSandboxIncomingMessage(data: dict):
    userMessageJSON, phoneNumber, receivedMessage = __preprocessIncomingMessage(data)
    pulseEmit(socketInstance, userMessageJSON)
    needsToSignUp = __checkUserRegistration(phoneNumber)
    if needsToSignUp:
        output, dialogflowResponseJSON = __handleNewUser(phoneNumber, receivedMessage)
        pulseEmit(socketInstance, dialogflowResponseJSON)
    else:
        output, dialogflowResponseJSON = __handleExistingUser(phoneNumber, receivedMessage)
    return dialogflowResponseJSON


def __main():
    d1 = {
        "SmsMessageSid": "SMc7f2b5f0c0a4b0b0a1a0a1a0a1a0a1a0",
        "NumMedia": "0",
        "SmsSid": "SMc7f2b5f0c0a4b0b0a1a0a1a0a1a0a1a0",
        "SmsStatus": "received",
        "Body": "oi",
        "To": "whatsapp:+14155238886",
        "NumSegments": "1",
        "MessageSid": "SMc7f2b5f0c0a4b0b0a1a0a1a0a1a0a1a0",
        "AccountSid": "AC034f7d97b8d5bc62dfa91b519ac43b0f",
        "From": "whatsapp:+558599663533",
        "ApiVersion": "2010-04-01"
    }
    response = processTwilioSandboxIncomingMessage(d1)


if __name__ == "__main__":
    __main()