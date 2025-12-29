# Mythology in Digital Games - Dataset

This repository contains the dataset and analysis code for a thesis about how different mythologies are represented and deepened in digital games.

## Contents

- `data/sqlite/when_everything_is_known.sqlite`  
  Full SQLite database with all tables.

- `data/sql/when_everything_is_known_dump.sql`  
  SQL dump to recreate the database on any SQL engine.

- `data/csv/*.csv`  
  One CSV file per table (mythologies, games, game_mythologies, platforms, genres, studios, sources, etc.).

- `analysis/python/`  
  Python notebooks and scripts used for statistical analysis and plots.

- `analysis/r/`  
  R scripts/notebooks used for analysis (if applicable).

- `docs/schema.md`  
  Description of each table and field.

- `docs/methodology.md`  
  Data collection and coding methodology (sources, inclusion/exclusion criteria, depth scale, etc.).

## Database overview

The database is structured as a small relational schema covering:

- **MYTHOLOGIES** – catalog of historical mythologies.
- **GAMES** – digital games that use at least one mythology.
- **GAME_MYTHOLOGIES** – link between games and mythologies, including a depth level (1–5) describing how deeply the mythology is integrated into the game.
- **PLATFORMS / GAME_PLATFORMS** – platforms where each game is available.
- **GENRES / GAME_GENRES** – genres associated with each game.
- **STUDIOS / GAME_STUDIOS** – game developers and publishers.
- **SOURCES / GAME_SOURCES** – where each game entry was collected from (Steam, RAWG, etc.).

More details are in `docs/schema.md`.

## License

### Code

All analysis code and scripts in this repository are released under the **MIT License** (see `LICENSE`).

### Data

The dataset (files inside `data/`) is released under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

You are free to share and adapt the data, as long as you provide appropriate credit.

## How to cite

If you use this dataset, please cite it as:

> Simões, D. (2025). *Mythology in Digital Games* [Data set]. (Repository: GitHub; DOI link will be added after deposit in Zenodo/OSF).

The formal citation and DOI will be updated once the dataset is deposited in a long-term repository (e.g. Zenodo/OSF).


Ligar o Apache no Xampp e correr php -S localhost:8000 no cmd.