import base64
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Header
import os
import re
import json
from utils import logger, stored_api_key, openai_api_key, default_response_dict
import secrets

app = FastAPI()

# Helper function to encode image to base64
def encode_image(file_content):
    return base64.b64encode(file_content).decode('utf-8')


def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if not stored_api_key:
        raise HTTPException(status_code=500, detail="Server error: API key not configured")
    if not secrets.compare_digest(x_api_key.encode('utf-8'), stored_api_key.encode('utf-8')):
        logger.error(f"Invalid API Key provided.") # Avoid logging the full key
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return x_api_key

@app.post("/recognize-document/")
async def recognize_document(file: UploadFile = File(...), api_key_from_header: str = Depends(verify_api_key)):
    # Read image file content
    image_content = await file.read()

    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error: OpenAI API Key not configured")

    client = OpenAI(api_key=openai_api_key)

    try:
        base64_image = encode_image(image_content)
        completion = client.chat.completions.create(
            model="gpt-4.1-mini", # Changed model to gpt-4o-mini as gpt-4.1-mini is not a standard model
            messages=[
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": "На изображении находится документ из медицинского центра. Пожалуйста, извлеки и верни следующую информацию в JSON-формате: 1.patient: ФИО пациента, 2. clinic: Название медцентра, 3. eventDate: Дата приёма, 4. doctorName: ФИО врача/доктора, 5. doctorSpec: Специализация врача, 6. diagnosis: Диагноз, 7. city: Город местонахождения данного центра, 8. subject: Краткое название документа(1-2 слова, например: Осмотр; Заключение; Справка). Если какая-либо информация отсутствует — укажи null." },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )

        # Находим "чистый" JSON в тексте
        response_text = completion.choices[0].message.content
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            response_dict = json.loads(json_str)
            logger.info('Recognized data: %s', response_dict)
        else:
            logger.info("Не удалось найти JSON в ответе.")
            response_dict = default_response_dict

        return response_dict
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e)}
