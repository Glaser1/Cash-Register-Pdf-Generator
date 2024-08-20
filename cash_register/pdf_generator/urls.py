from django.urls import path
from pdf_generator.views import get_cash_recipe_pdf_from_qr_code, cash_recipe

urlpatterns = [
    path("cash_machine", cash_recipe, name="cash_recipe_qr_code"),
    path(
        "media/", get_cash_recipe_pdf_from_qr_code, name="cash_recipe_pdf"
    ),
]
