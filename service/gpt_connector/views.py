from django.http import JsonResponse
from .utils.get_chat_response import get_chat_response

# Create your views here.
def chat_view(request):
    if request.method == "GET":
        try:
            user_input = "What is the best French cheese?"
            response_content = get_chat_response(user_input)
            return JsonResponse({"response": response_content}, status=200)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)