import os
from collections import Counter
from datetime import datetime

import pdfkit
import pytz
from django.conf import settings
from django.template.loader import get_template
from django.http import FileResponse, HttpResponse, Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pdf_generator.models import Item
from pdf_generator.utils.qrcode_generator import generate_qr_code


def prepare_items_with_quantity(item_ids):
    """
    Подготавливает список товаров с указанием количества и общей стоимости каждого товара.

    :param item_ids: Список ID товаров, отправленных в запросе.
    :return Кортеж, содеражщий список товаров с количеством и общей суммой.
    """
    item_counts = Counter(item_ids)
    items = Item.objects.filter(id__in=item_counts.keys())
    items_with_quantity = []
    total_sum = 0

    for item in items:
        quantity = item_counts[item.id]
        total_price = item.price * quantity
        items_with_quantity.append(
            {
                "title": item.title,
                "quantity": quantity,
                "total_price": total_price,
            }
        )
        total_sum += total_price

    return items_with_quantity, total_sum


def get_current_time_in_moscow():
    """
    Возвращает текущее время в московском часовом поясе в формате ДД.ММ.ГГГГ Ч:ММ.

    :return: Строка, представляющая текущее время в Москве.
    """
    moscow_tz = pytz.timezone("Europe/Moscow")
    return datetime.now(moscow_tz).strftime("%d.%m.%Y %H:%M")


def generate_pdf_and_qr_code(html):
    """
    Генерирует PDF-файл и QR-код, содержащий ссылку на этот файл.

    :param html: HTML-контент для генерации PDF.
    :return: HTTP-ответ с QR-кодом в формате изображения PNG.
    """
    try:
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)  # Создаем директорию, если она не существует
        pdfkit.from_string(html, settings.PDF_PATH)  # Генерация PDF-файла
        qr_code = generate_qr_code(f"{settings.LOCALHOST}/{settings.MEDIA_URL}")  # Генерация QR-кода с URL на PDF
        response = HttpResponse(content_type="image/png")
        qr_code.save(response, "PNG")  # Сохранение QR-кода в ответ
        # return response

    except Exception as e:
        raise IOError(f"Ошибка генерации PDF или QR-кода: {str(e)}")


@api_view(["POST"])
def cash_recipe(request):
    """
    Обрабатывает POST-запрос для генерации кассового чека в формате PDF и QR-кода, указывающего на этот файл.

    :param request: Объект запроса, содержащий список ID товаров.
    :return: HTTP-ответ с QR-кодом или сообщением об ошибке.
    """
    item_ids = request.data.get("items")

    if not item_ids:
        return Response(
            {"error": "Список товаров пуст или не передан"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        items_with_quantity, total_sum = prepare_items_with_quantity(item_ids)
        context = {
            "items": items_with_quantity,
            "total_sum": total_sum,
            "current_time": get_current_time_in_moscow(),
        }

        template = get_template("cash_recipe.html")
        html = template.render(context)
        return generate_pdf_and_qr_code(html)

    except Item.DoesNotExist:
        return Response(
            {"error": "Один или несколько товаров не найдены"},
            status=status.HTTP_404_NOT_FOUND,
        )

    except IOError as e:
        # Обработка ошибок, связанных с генерацией PDF-файла
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_cash_recipe_pdf_from_qr_code(request):
    """
    Обрабатывает GET-запрос для загрузки PDF-файла кассового чека, на который указывает QR-код.

    :param request: Объект запроса.
    :return: HTTP-ответ с файлом PDF или ошибка 404, если файл не найден.
    """
    if os.path.exists(settings.PDF_PATH):
        response = FileResponse(
            open(settings.PDF_PATH, "rb"), content_type="application/pdf"
        )
        response["Content-Disposition"] = f'attachment; filename="{settings.PDF_NAME}"'
        return response

    raise Http404(f"Файл {settings.PDF_NAME} не найден")
