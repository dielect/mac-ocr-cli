from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from PIL import Image
import io
from ocrmac import ocrmac

app = FastAPI()


class ImageBase64(BaseModel):
    image: str


def get_line_number(bbox, threshold=0.05):
    """
    Calculate the line number based on the bounding box.

    Parameters:
    bbox (list): Bounding box coordinates.
    threshold (float): Threshold to determine the line number.

    Returns:
    int: The calculated line number.
    """
    return int(bbox[1] // threshold)


def merge_text_by_line(ocr_results):
    """
    Merge OCR results by line number.

    Parameters:
    ocr_results (list): OCR results containing text, confidence, and bounding box.

    Returns:
    list: Merged text lines in reverse order.
    """
    lines = {}
    for result in ocr_results:
        text, confidence, bbox = result
        line_number = get_line_number(bbox)
        if line_number not in lines:
            lines[line_number] = []
        lines[line_number].append(text)

    merged_text = ["".join(lines[line_number]) for line_number in sorted(lines.keys())]
    return merged_text[::-1]


@app.post("/ocr")
async def perform_ocr(image_data: ImageBase64):
    """
    Perform OCR on the provided base64 encoded image.

    Parameters:
    image_data (ImageBase64): Base64 encoded image data.

    Returns:
    dict: OCR recognition results.

    Raises:
    HTTPException: If there is an error during the OCR process.
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.image)
        image = Image.open(io.BytesIO(image_bytes))

        # Perform OCR using ocrmac
        annotations = ocrmac.OCR(image, language_preference=["zh-Hans"]).recognize()
        result = merge_text_by_line(annotations)

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)