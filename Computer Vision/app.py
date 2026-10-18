import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException
import traceback

from vision_engine import analyze_nameplate


app =
allowed_origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS","*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
 FastAPI(
    title="Visual Operator Rounds API"
)


@app.get("/")
def home():

    return {
        "message": "Visual Operator Rounds API running"
    }


@app.post("/vision/nameplate")
async def read_nameplate(
    file: UploadFile = File(...)
):

    try:

        image_bytes = await file.read()

        print(
            "Uploaded:",
            file.filename,
            "| bytes:",
            len(image_bytes),
            "| type:",
            file.content_type
        )

        if len(image_bytes) == 0:
            raise ValueError(
                "Uploaded image contains zero bytes"
            )

        return analyze_nameplate(
            image_bytes
        )

    except Exception as e:

        print(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )