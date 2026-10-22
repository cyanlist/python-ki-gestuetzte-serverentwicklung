"""Enum of the Pokémon and move types used in this project."""

from enum import StrEnum

__all__ = ["PokemonType"]


class PokemonType(StrEnum):
    """The types of Pokémon and moves in generation 5 (no Fairy type yet)."""

    NORMAL = "Normal"
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"
    ELECTRIC = "Electric"
    ICE = "Ice"
    FIGHTING = "Fighting"
    POISON = "Poison"
    GROUND = "Ground"
    FLYING = "Flying"
    PSYCHIC = "Psychic"
    BUG = "Bug"
    ROCK = "Rock"
    GHOST = "Ghost"
    DRAGON = "Dragon"
    DARK = "Dark"
    STEEL = "Steel"
