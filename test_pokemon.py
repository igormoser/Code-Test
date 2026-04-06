
from pokemon import calcula_pontos_ataque, pokemon_evoluiu


def test_calcula_pontos_ataque_nivel_1():
    pokemon = {"forca_base": 10, "nível": 1}
    assert calcula_pontos_ataque(pokemon) == 10


def test_calcula_pontos_ataque_nivel_0():
    pokemon = {"forca_base": 5, "nível": 0}
    assert calcula_pontos_ataque(pokemon) == 0


def test_calcula_pontos_ataque_nivel_5():
    pokemon = {"forca_base": 20, "nível": 5}
    assert calcula_pontos_ataque(pokemon) == 100


def test_pokemon_evolui_nivel_menor_que_evolucao():
    pokemon = {"nível": 15}
    nivel_evolucao = 20
    assert pokemon_evoluiu(pokemon, nivel_evolucao) is False


def test_pokemon_evolui_nivel_igual_ao_da_evolucao():
    pokemon = {"nível": 20}
    nivel_evolucao = 20
    assert pokemon_evoluiu(pokemon, nivel_evolucao) is True


def test_pokemon_evolui_nivel_maior_que_evolucao():
    pokemon = {"nível": 25}
    nivel_evolucao = 20
    assert pokemon_evoluiu(pokemon, nivel_evolucao) is True