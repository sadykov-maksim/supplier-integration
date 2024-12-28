import requests
from bs4 import BeautifulSoup


def parse_price_from_website(url, price_selector):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск элемента с использованием селектора из модели
        price_element = soup.select_one(price_selector)

        if price_element:
            price = price_element.text.strip()
            return price
        else:
            return "Цена не найдена"

    except requests.exceptions.RequestException as e:
        return f"Ошибка при запросе: {e}"
    except AttributeError:
        return "Некорректная структура страницы или отсутствует элемент"