# 03 SQLAlchemy entities

**Goal:** Python classes for the three tables, including the 1:1 and the 1:N relation.

**Checklist item:** App server → "Entities for all three tables, including both
relations".

## Background

An **entity** is a Python class that represents a table. One object is one row.
SQLAlchemy 2 uses type annotations to define the columns:

| Annotation | Meaning |
|---|---|
| `Mapped[str]` | column `NOT NULL` |
| `Mapped[str \| None]` | column that allows `NULL` |
| `mapped_column(...)` | extra options such as `primary_key`, `unique`, `ForeignKey` |
| `relationship(...)` | link to the objects of another table, no column |

The relations in this project:

```text
pokemon 1 ──── 0..1 pokemon_detail     (1:1, pokemon_id is UNIQUE)
pokemon 1 ──── 0..N attacke            (1:N)
```

- **1:1:** `Pokemon.detail` is a single object, `PokemonDetail.pokemon_id` is `UNIQUE`,
  so a Pokémon has at most one detail row.
- **1:N:** `Pokemon.attacken` is a list, `Attacke.pokemon_id` is the foreign key.
- `back_populates` connects both sides: setting one side updates the other.
- `cascade="all, delete-orphan"` means: saving or deleting a Pokémon also saves or
  deletes its detail and moves.
- **Column names stay German** because they are defined in `01-schema.sql`. The Python
  attributes must have the same names as the columns.

Two details that are easy to miss:

- `MetaData(schema="pokemon")` puts all tables into the schema `pokemon`. That is why
  the foreign keys say `pokemon.pokemon.id` (schema, table, column).
- `version` is the version counter for optimistic locking. The line
  `__mapper_args__ = {"version_id_col": version}` makes SQLAlchemy add
  `AND version = <old>` to every `UPDATE` and increase the number. Guide 08 uses it.

## Steps

### Create `src/pokemon/entity.py`

```python
"""SQLAlchemy entities for the tables `pokemon`, `pokemon_detail` and `attacke`."""

from datetime import datetime

from sqlalchemy import ForeignKey, MetaData, Numeric, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class of all entities. All tables live in the schema `pokemon`."""

    metadata = MetaData(schema="pokemon")


class Pokemon(Base):
    """A Pokémon. This is the main table."""

    __tablename__ = "pokemon"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    """The Pokédex number. It is set by the caller and not generated."""

    name: Mapped[str]
    typ1: Mapped[str]
    typ2: Mapped[str | None]
    groesse_m: Mapped[float] = mapped_column(Numeric(4, 1, asdecimal=False))
    gewicht_kg: Mapped[float] = mapped_column(Numeric(5, 1, asdecimal=False))
    legendaer: Mapped[bool]

    version: Mapped[int] = mapped_column()
    """Version number for optimistic locking (see the PUT guide)."""

    aktualisiert: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
    """Timestamp of the last change. The database sets it on INSERT."""

    detail: Mapped["PokemonDetail | None"] = relationship(
        back_populates="pokemon",
        cascade="all, delete-orphan",
    )
    """The 1:1 relation: at most one detail row per Pokémon."""

    attacken: Mapped[list["Attacke"]] = relationship(
        back_populates="pokemon",
        cascade="all, delete-orphan",
    )
    """The 1:N relation: many moves per Pokémon."""

    # SQLAlchemy raises StaleDataError if the row was changed by someone else
    __mapper_args__ = {"version_id_col": version}

    def __repr__(self) -> str:
        """Short representation without the relations (they would trigger queries)."""
        return f"Pokemon(id={self.id}, name={self.name!r}, version={self.version})"


class PokemonDetail(Base):
    """Details of a Pokémon (1:1)."""

    __tablename__ = "pokemon_detail"

    id: Mapped[int] = mapped_column(primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(
        ForeignKey("pokemon.pokemon.id"), unique=True
    )
    fangrate: Mapped[int]
    basis_erfahrung: Mapped[int]

    pokemon: Mapped[Pokemon] = relationship(back_populates="detail")


class Attacke(Base):
    """A move of a Pokémon (N:1 to the Pokémon, so 1:N from its point of view)."""

    __tablename__ = "attacke"

    id: Mapped[int] = mapped_column(primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.pokemon.id"))
    name: Mapped[str]
    typ: Mapped[str]
    staerke: Mapped[int | None]
    genauigkeit: Mapped[int | None]

    pokemon: Mapped[Pokemon] = relationship(back_populates="attacken")
```

Why some choices were made:

- `Numeric(4, 1, asdecimal=False)` returns a normal `float` instead of `Decimal`.
  Pydantic writes `Decimal` as a string in JSON, which is not what you want here.
- `id` has `autoincrement=False` because the Pokédex number comes from the caller.
- The tables `pokemon_detail` and `attacke` use generated IDs (`GENERATED ALWAYS AS
  IDENTITY` in the schema). SQLAlchemy does not send an `id` for them on `INSERT`.
- `erzeugt` (created timestamp) is not mapped. The database fills it by default and
  the application never reads it. Map it if you need it.
- `__repr__` does not print `detail` or `attacken`. Accessing them in a log message
  would trigger additional queries.

## Check it

Create a throwaway script outside the project, for example in your temp folder, or run
it from the project root with `uv run python`:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from pokemon.database import SessionFactory
from pokemon.entity import Pokemon

with SessionFactory() as session:
    statement = (
        select(Pokemon)
        .where(Pokemon.id == 644)
        .options(selectinload(Pokemon.attacken))
    )
    zekrom = session.scalars(statement).one()
    print(zekrom, zekrom.detail.fangrate, [a.name for a in zekrom.attacken])
```

Expected output:

```text
Pokemon(id=644, name='Zekrom', version=0) 3 ['Donnerblitz', 'Drachenklaue']
```

Then run:

```shell
uv run ruff format
uv run ruff check
uv run ty check
```

## Common pitfalls

| Problem | Cause and fix |
|---|---|
| `NameError: name 'version' is not defined` | `version` needs a value on the right-hand side (`= mapped_column()`). A bare annotation does not create the name that `__mapper_args__` uses. |
| Error about a table or column that cannot be found when the entities are loaded | Check the foreign keys. They must contain the schema: `ForeignKey("pokemon.pokemon.id")`. |
| `relation "pokemon.pokemon" does not exist` | The init scripts did not run. See guide 02. |
| `column ... does not exist` | An attribute name differs from the column name in `01-schema.sql`. |
| Seed data has `version` 0, new rows start at 1 | Normal. SQLAlchemy sets the version of new rows to 1. It only matters that the number grows with every change. |
| `DetachedInstanceError` | A lazy relation was read after the session was closed. Load it in the query with `selectinload` or `joinedload` (guide 04). |

## Commit

```shell
git add src/pokemon/entity.py
git commit -m "feat(db): add SQLAlchemy entities"
```

## Prompt idea

```text
Context: PostgreSQL schema in extras/compose/postgres/init/01-schema.sql (tables
pokemon, pokemon_detail, attacke in the schema "pokemon"), SQLAlchemy 2.1 with
Mapped and mapped_column.
Task: Write src/pokemon/entity.py with one entity per table. pokemon_detail is 1:1
(unique foreign key), attacke is 1:N. Use back_populates and cascade
"all, delete-orphan". Use a version column for optimistic locking with
version_id_col. Float columns, not Decimal. Attribute names equal the column names.
Comments in English.
```
