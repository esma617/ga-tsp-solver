import math
import random
import statistics
import matplotlib.pyplot as plt


# ===================================================
# TSP PARSER
# ===================================================

def load_tsp(file_path):
    cities = {}

    with open(file_path, "r") as f:
        reading = False

        for line in f:
            line = line.strip()

            if line == "NODE_COORD_SECTION":
                reading = True
                continue

            if line == "EOF":
                break

            if reading:
                cid, x, y = line.split()
                cities[int(cid)] = (float(x), float(y))

    return cities


# ===================================================
# DISTANCE & FITNESS
# ===================================================

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def calculate_fitness(solution, cities):
    total = 0.0

    for i in range(len(solution)):
        a = cities[solution[i]]
        b = cities[solution[(i + 1) % len(solution)]]
        total += distance(a, b)

    return total


# ===================================================
# RANDOM & GREEDY
# ===================================================

def random_solution(cities):
    sol = list(cities.keys())
    random.shuffle(sol)
    return sol


def greedy_solution(start, cities):
    unvisited = set(cities.keys())
    unvisited.remove(start)

    sol = [start]
    current = start

    while unvisited:
        nxt = min(
            unvisited,
            key=lambda c: distance(cities[current], cities[c])
        )
        sol.append(nxt)
        unvisited.remove(nxt)
        current = nxt

    return sol


# ===================================================
# RANDOM SEARCH
# ===================================================

def random_search(cities, runs=100):
    results = []

    for _ in range(runs):
        sol = random_solution(cities)
        results.append(calculate_fitness(sol, cities))

    return {
        "best": min(results),
        "mean": statistics.mean(results),
        "std": statistics.stdev(results),
        "var": statistics.variance(results)
    }


# ===================================================
# GA OPERATORS
# ===================================================

def tournament_selection(pop, cities, k=3):
    competitors = random.sample(pop, k)
    competitors.sort(key=lambda s: calculate_fitness(s, cities))
    return competitors[0]


def ordered_crossover(p1, p2):
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))

    child = [None] * n
    child[a:b] = p1[a:b]

    fill = [c for c in p2 if c not in child]
    idx = 0

    for i in range(n):
        if child[i] is None:
            child[i] = fill[idx]
            idx += 1

    return child


def inversion_mutation(sol, rate):
    if random.random() < rate:
        i, j = sorted(random.sample(range(len(sol)), 2))
        sol[i:j] = reversed(sol[i:j])
    return sol


# ===================================================
# EVOLUTION
# ===================================================

def evolve_population(pop, cities, mutation_rate, elitism=1):
    new_pop = []
    sorted_pop = sorted(pop, key=lambda s: calculate_fitness(s, cities))

    for i in range(elitism):
        new_pop.append(sorted_pop[i][:])

    while len(new_pop) < len(pop):
        p1 = tournament_selection(pop, cities)
        p2 = tournament_selection(pop, cities)
        child = ordered_crossover(p1, p2)
        child = inversion_mutation(child, mutation_rate)
        new_pop.append(child)

    return new_pop


# ===================================================
# MAIN
# ===================================================

DATASET = "berlin11"

if DATASET == "berlin11":
    FILE = "data/berlin11_modified.tsp"
    POP, EPOCHS, MUT = 50, 150, 0.05
elif DATASET == "berlin52":
    FILE = "data/berlin52.tsp"
    POP, EPOCHS, MUT = 80, 300, 0.08
elif DATASET == "kroA100":
    FILE = "data/kroA100.tsp"
    POP, EPOCHS, MUT = 40, 150, 0.10
else:
    FILE = "data/kroA150.tsp"
    POP, EPOCHS, MUT = 30, 100, 0.12


cities = load_tsp(FILE)
start_city = list(cities.keys())[0]

greedy = greedy_solution(start_city, cities)
greedy_fit = calculate_fitness(greedy, cities)
print("Greedy fitness:", greedy_fit)

print("Random search stats:", random_search(cities))

population = [greedy]
for _ in range(POP - 1):
    population.append(random_solution(cities))

global_best = greedy_fit
best_solution = greedy[:]
history = []

for epoch in range(EPOCHS):
    population = evolve_population(population, cities, MUT, elitism=1)
    epoch_best = min(population, key=lambda s: calculate_fitness(s, cities))
    epoch_fit = calculate_fitness(epoch_best, cities)

    if epoch_fit < global_best:
        global_best = epoch_fit
        best_solution = epoch_best[:]

    history.append(global_best)

    if epoch % 20 == 0:
        print(f"Epoch {epoch} | Best = {global_best:.2f}")

print("Best GA fitness:", global_best)

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(history)
plt.xlabel("Epoch")
plt.ylabel("Best fitness")
plt.title(f"{DATASET} – GA Performance")
plt.grid()

plt.subplot(1, 2, 2)
x = [cities[c][0] for c in best_solution] + [cities[best_solution[0]][0]]
y = [cities[c][1] for c in best_solution] + [cities[best_solution[0]][1]]
plt.plot(x, y, marker="o")
plt.xlabel("X")
plt.ylabel("Y")
plt.title(f"{DATASET} – Best Route")
plt.grid()

plt.tight_layout()
plt.show()
