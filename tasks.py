import time
from celery_app import celery_app


@celery_app.task(name="tasks.calcular_soma")
def somar(a, b):
    time.sleep(3)
    return a + b


@celery_app.task(name="tasks.calcular_fatorial")
def fatorial(n):
    time.sleep(3)

    if n < 0:
        raise ValueError("Número negativo, não permitido!")

    resultado = 1
    for i in range(2, n + 1):
        resultado *= i

    return resultado