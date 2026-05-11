# GA TSP Solver

Solving the **Travelling Salesman Problem (TSP)** using a Genetic Algorithm in Python.

Built as a personal project to practice optimization algorithms and data visualization.

## What it does

Given a set of cities with coordinates, the algorithm evolves a population of routes over multiple generations to find the shortest possible tour.

- Greedy initialization + random population
- Tournament selection, Ordered Crossover (OX), Inversion Mutation
- Elitism to preserve the best solution each generation
- Matplotlib visualization of fitness curve and best route

## Datasets

Standard TSPLIB benchmark files included in `/data`:
- `berlin11_modified.tsp` — 11 cities
- `berlin52.tsp` — 52 cities
- `kroA100.tsp` — 100 cities
- `kroA150.tsp` — 150 cities

## Run

```bash
pip install matplotlib
python main.py
```

Change the `DATASET` variable in `main.py` to switch between datasets.

## Example output

GA converges within ~25 epochs on berlin11, reducing tour distance from ~4500 to ~4038.
