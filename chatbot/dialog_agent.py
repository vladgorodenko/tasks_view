import os
import dialogflow_v2
from google.api_core.exceptions import InvalidArgument

DIALOGFLOW_PROJECT_ID = 'sweetmagic-cake-bot-fomknc'
DIALOGFLOW_LANGUAGE_CODE = 'ru'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'


class DialogFlowAssistent:

    def __init__(self, session_id=None):
        self.session_id = session_id
        self.dialogflow_project_id = DIALOGFLOW_PROJECT_ID
        self.dialogflow_language_code = DIALOGFLOW_LANGUAGE_CODE

    def get_answer(self, inputed_text):
        session_client = dialogflow_v2.SessionsClient()
        session = session_client.session_path(self.dialogflow_project_id, self.session_id)
        text_input = dialogflow_v2.types.session_pb2.TextInput(text=inputed_text,
                                                               language_code=self.dialogflow_language_code)
        query_input = dialogflow_v2.types.session_pb2.QueryInput(text=text_input)

        try:
            response = session_client.detect_intent(session=session, query_input=query_input)
        except InvalidArgument:
            raise

        # response.query_result.parameter
        return response.query_result.fulfillment_text, response.query_result.parameters.fields
