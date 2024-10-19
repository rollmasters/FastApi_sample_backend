import base64
import os
import time
from datetime import datetime

from fastapi import HTTPException
from mongomock.object_id import ObjectId

from app.utils.file_manger import save_audio_file
from app.utils.http_client import send_request
from app.utils.security import validate_object_id
from app.models.user_messages import UserMessages
from app.models.user_messages import AIResponse as Ai_api_answer
from app.schemas.ai_agent import AIResponse
from app.database import get_db_spatial_ai
from app.core.config import settings


async def process_ai_response(input):
    try:
        start_time = time.time()
        audio_data = base64.b64decode(input.wavData)
        file_path = save_audio_file(audio_data)
        company_id = validate_object_id(input.companyId)
        user_id = validate_object_id(input.userId)

        # Fetch user messages from the database
        db = await get_db_spatial_ai()
        collection = db["UserMessage"]
        filter_query = {"companyId": ObjectId(company_id), "userId": ObjectId(user_id)}
        user_messages =  await collection.find(filter_query).to_list(length=None)

        # Send audio and user messages to AI service
        url = f"{settings.AI_SITE}/process_voice/{input.companyId}"
        ai_response_data = await send_request(url, file_path=file_path, lang=input.lang, user_messages=user_messages)

        if ai_response_data:
            ai_response = AIResponse(**ai_response_data)
            process_ai_response_links(ai_response, input.lang)

            # Calculate processing time
            ai_response.process_time = time.time() - start_time

            # Store user message in the database
            user_message = UserMessages(
                time=datetime.utcnow(),
                AIResponses=ai_response,
                lang=input.lang,
                companyId=ObjectId(company_id),
                userId=ObjectId(user_id)
            )
            await insert_user_message_async(collection, user_message)
            return ai_response
        else:
            raise HTTPException(status_code=500, detail="AI response is invalid")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists("output.wav"):
            os.remove("output.wav")


async def process_ai_response_text(input):
    try:
        start_time = time.time()
        company_id = validate_object_id(input.companyId)
        user_id = validate_object_id(input.userId)

        # Fetch user messages from the database
        db = await get_db_spatial_ai()
        collection = db["UserMessage"]
        filter_query = {"companyId": company_id, "userId": user_id}
        user_messages_list =  await collection.find(filter_query).to_list(length=None)
        # Convert documents to Pydantic models
        user_messages = [UserMessages(**message) for message in user_messages_list]

        # Serialize models to dictionaries with correct field names
        user_messages_json = [message.model_dump(by_alias=True) for message in user_messages]
        payload = {
            "user_messages": user_messages_json,
            "lang": input.lang,
            "question": input.question
        }

        url = f"{settings.AI_SITE}/get_answer/"
        ai_response_data = send_request(url, payload=payload)

        if ai_response_data:
            ai_response = Ai_api_answer(**ai_response_data)
            process_ai_response_links(ai_response, input.lang)

            # Calculate processing time
            ai_response.process_time = time.time() - start_time

            # Store user message in the database
            user_message = UserMessages(
                time=str(datetime.now()),
                AIResponses=ai_response,
                lang=input.lang,
                companyId=company_id,
                userId=user_id
            )
            await insert_user_message_async(collection, user_message)
            return ai_response
        else:
            raise HTTPException(status_code=500, detail="AI response is invalid")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def process_ai_response_links(ai_response, lang):
    import re

    # Extract and remove links from the answer
    link_pattern = re.compile(r'[\[(](https?://[^\s]+|www\.[^\s]+)[\])]')
    ai_response.links = link_pattern.findall(ai_response.answer)
    ai_response.answer = link_pattern.sub('', ai_response.answer)

    # Process list numbers in the answer
    ai_response.voice = replace_list_numbers(ai_response.answer, lang)

    # Clean the answer and voice text
    ai_response.answer = clean_string(ai_response.answer)
    ai_response.voice = clean_string(ai_response.voice)


def replace_list_numbers(input_text, lang):
    import re

    # First stage: Replace main numbers (1., 2., etc.)
    re_main = re.compile(r'(?m)^(\d+)\.')
    input_text = re_main.sub(lambda m: f"numero {m.group(1)}." if lang == "IT" else f"number {m.group(1)}.", input_text)

    # Second stage: Replace nested numbers (1.1, 1.2, etc.)
    re_nested = re.compile(r'(\d+(\.\d+)+)')

    def replace_nested(match):
        numbers = match.group(1).split('.')
        if lang == "IT":
            formatted = "numero " + " punto ".join(numbers) + "."
        else:
            formatted = "number " + " point ".join(numbers) + "."
        return formatted

    input_text = re_nested.sub(replace_nested, input_text)

    return input_text


def clean_string(text):
    # Implement any cleaning logic required
    return text.strip()


async def insert_user_message_async(collection, user_message):
    await collection.insert_one(user_message.dict())