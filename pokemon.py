def calcula_pontos_ataque(pokemon: dict) -> int:
    return pokemon["forca_base"] * pokemon["nível"]

def pokemon_evoluiu(pokemon: dict, nivel_evolucao: int) -> bool:
    return pokemon["nível"] >= nivel_evolucao
