import pytest
from pokemon import calcula_pontos_ataque, pokemon_evoluiu

@pytest.fixture
def bulbasaur():
    return {"nome": "Bulbasaur", "forca_base": 49, "nível": 10}

@pytest.fixture
def charmander():
    return {"nome": "Charmander", "forca_base": 52, "nível": 15}

@pytest.fixture
def mewtwo():
    return {"nome": "Mewtwo", "forca_base": 999, "nível": 100}


def test_calcula_pontos_ataque_bulbasaur(bulbasaur):
    assert calcula_pontos_ataque(bulbasaur) == 490

def test_calcula_pontos_ataque_charmander(charmander):
    assert calcula_pontos_ataque(charmander) == 780

def test_calcula_pontos_ataque_mewtwo(mewtwo):
    assert calcula_pontos_ataque(mewtwo) == 99900

def test_pokemon_evoluiu_charmander(charmander):
    assert pokemon_evoluiu(charmander, 20 ) is False
    assert pokemon_evoluiu(charmander, 15) is True

def test_pokemon_evoluiu_mewtwo(mewtwo):
    assert pokemon_evoluiu(mewtwo, 50 ) is True

