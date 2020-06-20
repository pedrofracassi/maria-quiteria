from datetime import date, timedelta
from logging import info
from pathlib import Path

import requests
from datasets.services import get_s3_client
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from dotenv import find_dotenv, load_dotenv
from dramatiq import actor, middleware, set_broker
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from tika import parser

# Esse bloco (feio) faz com que esse módulo funcione dentro ou fora do Django
try:
    from datasets.models import File
except ImproperlyConfigured:
    import configurations
    import os

    os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    load_dotenv(find_dotenv())
    configurations.setup()
    from datasets.models import File

# models precisam ser importados depois das configurações
# para manter compatibilidade com o scraper
from datasets.webservices.citycouncil import (  # noqa isort:skip
    add_bid,
    add_contract,
    add_expense,
    remove_bid,
    remove_contract,
    remove_expense,
    update_bid,
    update_contract,
    update_expense,
)

rabbitmq_broker = RabbitmqBroker(url=settings.CLOUDAMQP_URL)
rabbitmq_broker.add_middleware(middleware.Prometheus())
set_broker(rabbitmq_broker)
client = get_s3_client(settings)


@actor(max_retries=5)
def content_from_file(file_pk=None, path=None, keep_file=True):
    if not any([file_pk, path]):
        raise Exception("Ou `file_pk` ou `path` devem ser informados.")

    a_file = None
    if file_pk:
        a_file = File.objects.get(pk=file_pk)

        if a_file.content is not None:
            return a_file.content

        path = client.download_file(a_file.s3_file_path)
        keep_file = False

    if not Path(path).exists():
        info(f"Arquivo {path} não encontrado.")
        return

    raw = parser.from_file(path)

    if not keep_file:
        Path(path).unlink()

    if a_file:
        a_file.content = raw["content"]
        a_file.save()

    return raw["content"]


@actor(max_retries=5)
def backup_file(file_id):
    try:
        file_obj = File.objects.get(pk=file_id, s3_url__isnull=True)
    except File.DoesNotExist:
        info(f"O arquivo ({file_id}) não existe ou já possui backup.")
        return

    model_name = file_obj.content_object._meta.model_name
    relative_file_path = (
        f"{model_name}/{file_obj.created_at.year}/"
        f"{file_obj.created_at.month}/{file_obj.created_at.day}/"
    )

    s3_url, s3_file_path = client.upload_file(
        file_obj.url, relative_file_path, prefix=file_obj.checksum
    )
    file_obj.s3_file_path = s3_file_path
    file_obj.s3_url = s3_url
    file_obj.save()

    return s3_url


@actor(max_retries=5)
def retrieve_city_council_updates():
    """Solicita atualizações ao webservice da Câmara."""
    yesterday = date.today() - timedelta(days=1)  # formato aaaa-mm-dd
    response = requests.post(
        settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT,
        data={
            "data": yesterday.strftime("%Y-%m-%d"),
            "token": settings.CITY_COUNCIL_WEBSERVICE_TOKEN,
        },
        headers={"User-Agent": "Maria Quitéria"},
    )
    return response.json()


@actor(max_retries=5)
def sync_city_council_objects(payload):
    action_methods = {
        "inclusoesContrato": add_contract,
        "alteracoesContrato": update_contract,
        "exclusoesContrato": remove_contract,
        "inclusoesLicitacao": add_bid,
        "alteracoesLicitacao": update_bid,
        "exclusoesLicitacao": remove_bid,
        "inclusoesDespesa": add_expense,
        "alteracoesDespesa": update_expense,
        "exclusoesDespesa": remove_expense,
    }
    for action_name, records in payload.items():
        method = action_methods.get(action_name)
        for record in records:
            method(record)
