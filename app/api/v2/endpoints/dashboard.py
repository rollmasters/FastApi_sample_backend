from datetime import datetime

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from app.database import get_db_spatial_ai
from app.models.dashboard import Settings, TableData, AIInfo, Preferences, BugReport
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models.user_messages import UserMessages, convert_DB_user_message_pydantic
from app.schemas.ai_agent import AISummary
from app.services.ai_service import summarize_data
from app.utils.security import validate_object_id

router = APIRouter()


@router.get("/aiSettings/{id}", response_model=Settings)
async def get_ai_settings(id: str, db=Depends(get_db_spatial_ai)):
    company_id = id
    settings_collection = db['ai_setting']
    settings_doc = await settings_collection.find_one({'companyId': company_id})

    if not settings_doc:
        # No settings found, create new one with default values
        default_settings = Settings(
            companyId=company_id,
            chatEnabled=False,
            creative=False,
            unknown=False,
            url=""
        )
        # Insert the new settings into the database
        await settings_collection.insert_one(default_settings.dict(by_alias=True))
        return default_settings
    else:
        # Return the existing settings
        return Settings(**settings_doc)


# POST /aiSettings/{id}
@router.post("/aiSettings/{id}")
async def update_ai_settings(id: str, new_settings: Settings, db=Depends(get_db_spatial_ai)):
    company_id = id
    settings_collection = db['ai_setting']

    # Exclude 'url' and 'companyId' fields from the update
    update_data = new_settings.model_dump(by_alias=True, exclude={'url', 'companyId'})

    result = await settings_collection.update_one(
        {'companyId': company_id},
        {'$set': update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="No matching company ID found")

    return {"message": "Settings updated successfully"}


@router.get("/getAiList/{id}", response_model=List[TableData])
async def get_ai_list(id: str, db=Depends(get_db_spatial_ai)):
    company_id = id
    table_data_collection = db['changes']

    # Query the collection
    cursor = table_data_collection.find({'companyId': company_id}, {'_id': 0})

    # Fetch all documents
    data = []
    async for document in cursor:
        data.append(TableData(**document))

    # If no data found, return an empty list
    if not data:
        data = []

    return data


# GET /ai_info/{companyID}
@router.get("/ai_info/{companyID}", response_model=AIInfo)
async def get_ai_info(companyID: str, db=Depends(get_db_spatial_ai)):
    collection = db['Company']
    try:
        ai_info_doc = await collection.find_one({'companyId': companyID})
        if not ai_info_doc:
            # No document found, create a new one with default values
            ai_info = AIInfo(
                companyId=companyID,
                enterpriseName='',
                website='',
                industry='',
                description='',
                agentName='',
                commonInquiries=[],
                adjustments='',
                language='English',
                documentationLinks=[],
                referredLinks=[],
            )
            result = await collection.insert_one(ai_info.model_dump(by_alias=True))
            ai_info.id = result.inserted_id
            return ai_info
        else:
            # Document found, return it
            ai_info_doc["_id"] = str(ai_info_doc.get("_id"))
            ai_info = AIInfo(**ai_info_doc)
            return ai_info
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Unable to fetch AI info: {str(e)}")


# POST /ai_info/{companyID}
@router.post("/ai_info/{companyID}", response_model=AIInfo)
async def update_ai_info(companyID: str, updated_info: AIInfo, db=Depends(get_db_spatial_ai)):
    collection = db['Company']
    updated_info.companyId = companyID  # Ensure the companyId matches the URL parameter
    try:
        result = await collection.update_one(
            {'companyId': companyID},
            {'$set': updated_info.dict(by_alias=True, exclude={'id', 'companyId'})},
            upsert=True
        )
        if result.upserted_id:
            updated_info.id = result.upserted_id
        else:
            existing_doc = await collection.find_one({'companyId': companyID})
            updated_info.id = existing_doc['_id']
        return updated_info
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Failed to update AI info: {str(e)}")


@router.get("/appearance/{company_id}", response_model=Preferences)
async def get_ai_appearance(company_id: str, db=Depends(get_db_spatial_ai)):
    collection = db["specialAI"]["appearance"]

    # Find the preferences by company ID
    prefs = await collection.find_one({"company_id": company_id})

    if prefs is None:
        # Default values if no document exists
        default_prefs = Preferences(company_id=company_id)
        # Insert default preferences
        await collection.insert_one(default_prefs.model_dump(by_alias=True))
        return default_prefs

    return Preferences(**prefs)


# POST: Update AI appearance preferences
@router.post("/appearance/{company_id}")
async def set_ai_appearance(company_id: str, prefs: Preferences, db=Depends(get_db_spatial_ai)):
    collection = db["appearance"]

    # Update or insert the preferences
    updated_prefs = await collection.find_one_and_update(
        {"company_id": company_id},
        {"$set": prefs.model_dump(by_alias=True)},
        return_document=ReturnDocument.AFTER,
        upsert=True
    )

    if updated_prefs is None:
        raise HTTPException(status_code=500, detail="Failed to update preferences")

    return {"message": "Preferences updated successfully"}


@router.post("/bugreport", response_model=BugReport)
async def create_bug_report(report: BugReport, db=Depends(get_db_spatial_ai)):
    collection = db["bug_reports"]

    # Set the created_at timestamp to the current time
    report.created_at = datetime.now()

    # Insert the report into the database
    result = await collection.insert_one(report.model_dump(by_alias=True))

    if result.inserted_id:
        return report
    else:
        raise HTTPException(status_code=500, detail="Failed to create new bug report")


@router.get("/ai_summary/{company_id}", response_model=AISummary)
async def get_ai_summary(company_id: str, db=Depends(get_db_spatial_ai)):
    # Validate and convert company_id to ObjectId
    try:
        company_id = validate_object_id(company_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid company ID")

    collection = db["UserMessage"]
    filter_query = {"companyId": company_id}
    user_messages_list = await collection.find(filter_query).sort("time",-1).to_list(length=None)


    if not user_messages_list:
        raise HTTPException(status_code=404, detail="No messages found")

    # Convert MongoDB documents to Pydantic models
    user_messages_list =  convert_DB_user_message_pydantic(user_messages_list)
    user_messages = [UserMessages(**message) for message in user_messages_list]

    # Summarize the data
    summary = summarize_data(user_messages)

    return summary





@router.post("/ai_agent", response_model=dict)
async def create_ai_agent(agent: TableData, db=Depends(get_db_spatial_ai)):
    # Check if the companyID is provided
    if not agent.companyId:
        raise HTTPException(status_code=400, detail="Company ID is required")

    # Set the current date if not provided
    if agent.date is None:
        agent.date = datetime.now()

    # Insert into MongoDB
    collection = db["changes"]
    try:
        result = await collection.insert_one(agent.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create new AI agent")

    return {"message": "AI agent created successfully", "id": str(result.inserted_id)}


