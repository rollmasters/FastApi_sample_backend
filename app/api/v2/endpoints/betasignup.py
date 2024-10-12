from fastapi import Depends, HTTPException, status, BackgroundTasks, APIRouter
from motor.motor_asyncio import AsyncIOMotorClient

from app.database import get_db_spatial_ai
from app.models.demo import BetaSignup
from app.services.email import send_email
from jinja2 import Template

router = APIRouter()


@router.post(
    "/demo",
    response_model=BetaSignup,
    status_code=status.HTTP_201_CREATED
)
async def demo(
    data: BetaSignup,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorClient = Depends(get_db_spatial_ai)
):
    # Insert data into MongoDB
    collection = db["demo"]
    try:
        result = await collection.insert_one(data.model_dump(by_alias=True))
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save to database"
            )
    except Exception as e:
        # Catch any database-related exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion error: {str(e)}"
        )

    # Prepare email body
    try:
        email_body = prepare_email_body(data)
    except Exception as e:
        # If there's an issue with preparing the email body, raise an HTTP exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error preparing email body: {str(e)}"
        )

    # Define the list of recipients
    recipients = [
        "amir@morseverse.com",
        "farzad@morseverse.com",
        "mona@morseverse.com",
        "alireza@morseverse.com",
        "amin@morseverse.com",
        "mona131376st@gmail.com"
    ]

    # Schedule the email to be sent in the background
    try:
        background_tasks.add_task(send_email, recipients, "Book a demo", email_body)
    except Exception as e:
        # Catch any exceptions that occur while adding the background task
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule email sending: {str(e)}"
        )

    # Return the data as the response
    return data


def prepare_email_body(data: BetaSignup) -> str:
    tmpl = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo booking</title>
        <style>
            body { font-family: Arial, sans-serif; }
            h1 { color: #333366; }
            p { color: #666; font-size: 16px; }
        </style>
    </head>
    <body>
        <h1>Hello,</h1>
        <ul>
            <li>Name and Last Name: {{ data.firstName }} {{ data.lastName }}</li>
            <li>Email: {{ data.email }}</li>
            <li>Website: {{ data.website }}</li>
            <li>Country: {{ data.country }}</li>
            <li>Community Scale: {{ data.communityScale }}</li>
            <li>Message: {{ data.message }}</li>
            <li>Goals: {{ data.goals }}</li>
        </ul>
    </body>
    </html>
    '''
    template = Template(tmpl)
    return template.render(data=data)
