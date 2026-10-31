from fastapi import FastAPI, UploadFile, File, HTTPException
import traceback

from vision_engine import analyze_nameplate


app = FastAPI(
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