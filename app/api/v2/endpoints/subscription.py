from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.subscription import Person, SubscriptionCollection
from app.database import get_db
from typing import Dict

router = APIRouter()

@router.post("/person", response_model=Dict[str, str],
             status_code=status.HTTP_201_CREATED)
async def create_subscription(person: Person, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Create a subscription entry in MongoDB."""
    try:
        subscription_collection = db.get_collection("Subscriptions")

        # Convert the Pydantic model to a dictionary, excluding the `id` field if it's auto-generated
        person_dict = person.model_dump(by_alias=True, exclude=["id"])

        # Insert the person data into the 'Subscriptions' collection
        result = await subscription_collection.insert_one(person_dict)

        # Retrieve the inserted subscription for confirmation
        created_subscription = await subscription_collection.find_one(
            {"_id": result.inserted_id}
        )

        return {"message": "Subscription created successfully", "id": str(result.inserted_id)}

    except Exception as e:
        # Handle any exceptions that occur during database operations
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/people", response_model=SubscriptionCollection,
            status_code=status.HTTP_200_OK)
async def get_subscriptions(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Fetch all subscriptions from MongoDB."""
    try:
        # Fetch all documents from the Subscriptions collection
        cursor = db["Subscriptions"].find({})
        people = []
        async for person in cursor:
            person["_id"] = str(person["_id"])  # Convert ObjectId to string
            people.append(Person(**person))
        return {"people": people}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch subscriptions: {e}")
