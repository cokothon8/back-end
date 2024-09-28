from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from domain.user import router as user_router

tags_metadata = [
    {
        "name": "user",
        "description": "회원 기능",
    },
    {
        "name": "history",
        "description": "기록",
    },
    {
        "name": "friend",
        "description": "친구",
    }
]

app = FastAPI(
    openapi_tags=tags_metadata
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router.router, tags=["users"])