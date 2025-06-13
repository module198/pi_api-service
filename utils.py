import logging
from dotenv import load_dotenv
import os

load_dotenv()
stored_api_key = os.getenv("MY_API_KEY") # API key for the service 
openai_api_key = os.getenv("OPENAI_API_KEY") # API key for the OpenAI service

# Настройка конфигурации логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (можно выбрать: DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат сообщения
    handlers=[
        logging.StreamHandler(),  # Вывод логов в консоль
        logging.FileHandler('pi_api_service.log', encoding='utf-8')  # Запись логов в файл 'app.log' с UTF-8 кодировкой
    ]
)
logger = logging.getLogger('pi_api_service')

default_response_dict = {
                "city": None,
                "clinic": None,
                "diagnosis": None,
                "doctorName": None,
                "doctorSpec": None,
                "eventDate": None,
                "patient": None,
                "subject": None
            }