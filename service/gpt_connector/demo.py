from .models import GPTConnectorSettings, ChatRequest, ChatResponse
from mistralai import Mistral


def get_chat_response(user_input):
    """Получает ответ от API Mistral и сохраняет запрос и ответ в базе данных."""
    # Получение активных настроек API
    settings = GPTConnectorSettings.objects.filter(is_active=True).first()
    if not settings:
        raise ValueError("Active GPTConnectorSettings not found.")

    # Настройка клиента API
    client = Mistral(api_key=settings.api_key)

    # Создание запроса
    chat_request = ChatRequest.objects.create(
        user_input=user_input,
        model_name=settings.model_name,
        api_key_used=settings.api_key,
    )

    # Отправка запроса к API
    response = client.chat.complete(
        model=settings.model_name,
        messages=[{"role": "user", "content": user_input}],
    )

    # Извлечение контента ответа
    response_content = response.choices[0].message.content

    # Сохранение ответа в базе данных
    ChatResponse.objects.create(
        request=chat_request,
        response_content=response_content,
    )

    return response_content

if __name__ == '__main__':
    user_input = "What is the best French cheese?"
    response = get_chat_response(user_input)
    print(f"API Response: {response}")