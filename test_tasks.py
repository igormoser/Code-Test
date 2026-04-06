import pytest
from tasks import somar, fatorial


def test_task_soma_retorna_resultado_correto():
    assert somar(2, 3) == 5


def test_task_fatorial_retorna_resultado_correto():
    assert fatorial(5) == 120


def test_task_fatorial_de_zero_retorna_um():
    assert fatorial(0) == 1


def test_task_fatorial_numero_negativo_lanca_erro():
    with pytest.raises(ValueError, match="Número negativo, não permitido!"):
        fatorial(-1)


