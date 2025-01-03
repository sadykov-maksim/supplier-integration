import csv

from brom import *
import re
from main.models import Supplier

import pandas as pd

def create_client():
    """
    Creates and returns a БромКлиент object.
    """
    try:
        return БромКлиент(
            публикация="http://v2.bullfinch.it:9090/ut_copy_3/ru_ru/",
            пользователь="bromuser",
            пароль="MxWOLAK@Y0W/_!B~",
        )
    except Exception as error:
        print("Ошибка создания клиента:", error)

def save_to_csv(data, filename):
    """Оптимизированная запись данных в CSV с Pandas."""
    try:
        # Преобразование данных в DataFrame (быстрее, чем писать построчно)
        df = pd.DataFrame.from_records(
            [(row.Номенклатура, row.Артикул, row.Описание, row.ВидЦены, row.Цена, row.Валюта) for row in data],
            columns=['Номенклатура', 'Артикул', 'Описание', 'ВидЦены', 'Цена', 'Валюта']
        )

        # Запись в CSV с параметром ускоренной записи
        df.to_csv(filename, index=False, encoding='utf-8', mode='w')

        print(f"Данные успешно сохранены в {filename}")

    except Exception as error:
        print(f"Ошибка при сохранении в CSV: {error}")

def read_from_csv(filename):
    """Читает данные из CSV файла и возвращает их в виде списка."""
    data = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Пропускаем заголовки
            next(reader)

            # Чтение данных
            for row in reader:
                data.append({
                    'Номенклатура': row[0],
                    'Артикул': row[1],
                    'Описание': row[2],
                    'ВидЦены': row[3],
                    'Цена': row[4],
                    'Валюта': row[5],
                })
        return data
    except Exception as error:
        print(f"Ошибка при чтении CSV: {error}")
        return None

def get_list_product(prefix):
    """
    Fetches product price details based on product name.
    """
    client = create_client()
    req = client.СоздатьЗапрос("""
    ВЫБРАТЬ
        ЦеныНоменклатурыСрезПоследних.Номенклатура КАК Номенклатура,
        ЦеныНоменклатурыСрезПоследних.Номенклатура.Код КАК Код,
        ЦеныНоменклатурыСрезПоследних.Номенклатура.Артикул КАК Артикул,
        ЦеныНоменклатурыСрезПоследних.Номенклатура.Описание КАК Описание,
        ЦеныНоменклатурыСрезПоследних.Номенклатура.Родитель КАК Группа,  
        ЦеныНоменклатурыСрезПоследних.ВидЦены КАК ВидЦены,
        ЦеныНоменклатурыСрезПоследних.Цена КАК Цена,
        ЦеныНоменклатурыСрезПоследних.Валюта КАК Валюта
    ИЗ
        РегистрСведений.ЦеныНоменклатуры.СрезПоследних КАК ЦеныНоменклатурыСрезПоследних
    ГДЕ
	    ЦеныНоменклатурыСрезПоследних.Номенклатура.Артикул ПОДОБНО &Артикул
	    И (ЦеныНоменклатурыСрезПоследних.ВидЦены.Наименование = &ВидЦен
	       ИЛИ ЦеныНоменклатурыСрезПоследних.ВидЦены.Наименование = &ВидЦен2)
	       		И ЦеныНоменклатурыСрезПоследних.Номенклатура.Артикул НЕ ПОДОБНО "%(К)"
   		И НЕ (ЦеныНоменклатурыСрезПоследних.Номенклатура.Родитель.Наименование = "ДЛЯ ЗАКАЗОВ"
          ИЛИ ЦеныНоменклатурыСрезПоследних.Номенклатура.Родитель.Наименование = "!!!!!!НОВИНКИ!!!!")
        И ЦеныНоменклатурыСрезПоследних.Номенклатура.НеВыгружатьНаСайт = Ложь  
	    И ЦеныНоменклатурыСрезПоследних.Номенклатура.ПометкаУдаления = Ложь
    """)
    req.УстановитьПараметр("Артикул", f"{prefix}%")
    req.УстановитьПараметр("ВидЦен", "Прайс-лист")
    req.УстановитьПараметр("ВидЦен2", "Закупочная")
    try:
        res = req.Выполнить()

        return res

    except Exception as error:
        print("Ошибка выполнения запроса:", error)

def get_supplier_by_sku(sku):
    # Извлекаем префикс из артикула (предполагаем, что формат всегда "TTT-000123")
    prefix_match = re.match(r"^[A-ZА-ЯЁa-zа-яё]+-", sku)

    if prefix_match:
        prefix = prefix_match.group().rstrip('-')  # Убираем дефис с конца префикса
        print(prefix)
        # Ищем поставщика с соответствующим префиксом
        try:
            supplier = Supplier.objects.get(prefix=prefix)
            return supplier
        except Supplier.DoesNotExist:
            return None  # Если поставщик с таким префиксом не найден
    else:
        return None  # Если префикс не удалось извлечь

def update_product(client, name):
    """
      Fetches product price details based on product name.
      """
    req = client.СоздатьЗапрос("""
        ВЫБРАТЬ
            ЦеныНоменклатуры.Ссылка КАК СсылкаНаДокумент,
            ЦеныНоменклатуры.Цена КАК ТекущаяЦена
        ИЗ
            РегистрСведений.ЦеныНоменклатуры КАК ЦеныНоменклатуры
        ГДЕ
            ЦеныНоменклатуры.Номенклатура.Артикул = &Артикул
      """)
    req.УстановитьПараметр("Артикул", name)
    try:
        res = req.Выполнить()
        return res

    except Exception as error:
        print("Ошибка выполнения запроса:", error)


def update_product_description(article, neuro_description):
    """
    Получает информацию о товаре по его артикулу и обновляет описание.

    Параметры:
    - client: Экземпляр клиента 1С для выполнения запросов.
    - article (str): Артикул товара, для которого необходимо получить данные.

    Функционал:
    - Извлекает информацию о товаре из справочника "Номенклатура", где артикул совпадает с указанным параметром.
    - Обновляет описание товара на новое значение ("Новое описание").
    - Выводит информацию о товаре, включая наименование, описание, код и артикул.
    """
    client = create_client()

    req = client.СоздатьЗапрос("""
        ВЫБРАТЬ
            Номенклатура.Ссылка КАК Ссылка,
            Номенклатура.Код КАК Код,
            Номенклатура.Наименование КАК Наименование,
            Номенклатура.Описание КАК Описание,
            Номенклатура.Артикул КАК Артикул
        ИЗ
            Справочник.Номенклатура КАК Номенклатура
        ГДЕ
            Номенклатура.ЭтоГруппа = ЛОЖЬ
            И Номенклатура.Артикул = &Артикул
    """)
    req.УстановитьПараметр("Артикул", article)

    try:
        res = req.Выполнить()
        for row in res:
            print(f"Код: {row.Код}\n"
                  f"Номенклатура: {row.Наименование}\n"
                  f"Артикул: {row.Артикул}\n"
                  f"Описание: {row.Описание}\n")
            try:
                product_link = row.Ссылка
                product = product_link.ПолучитьОбъект()
                product.Описание = neuro_description
                product.Записать()
                print(f"Описание для товара с артикулом '{row.Артикул}' успешно обновлено.")
            except Exception as e:
                print(f"Ошибка при обновлении товара '{row.Наименование}': {e}")
    except Exception as error:
        print("Ошибка выполнения запроса:", error)

def normalize_article(article):
    """
    Нормализует артикул товара, убирая возможные префиксы.
    Например, 'СШ3-2000' и 'ЗСШЗ-2000' станут одинаковыми.
    """
    return article.lstrip('СЗ')  # Убираем префиксы 'С' или 'З', оставляем остальную часть артикула