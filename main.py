import math
# Matematiksel işlemler için kullanılır
# Özellikle Öklidyen mesafe hesaplamak için gereklidir

import random
# Rastgelelik gerektiren işlemler için kullanılır
# Random çözüm, selection ve mutation aşamalarında kullanılır

import statistics
# Ortalama, standart sapma ve varyans hesaplamak için kullanılır
# Random search sonuçlarını raporlamak için eklenmiştir

import matplotlib.pyplot as plt
# Genetic Algorithm performansını ve rotayı görselleştirmek için kullanılır


# ===================================================
# TSP PARSER
# ===================================================

def load_tsp(file_path):
    # .tsp dosyasını okuyup şehir koordinatlarını yükleyen fonksiyon

    cities = {}
    # Şehirleri saklamak için boş bir sözlük
    # Key: şehir id, Value: (x, y)

    with open(file_path, "r") as f:
        # Dosya güvenli şekilde açılır

        reading = False
        # NODE_COORD_SECTION'a gelince True olur

        for line in f:
            # Dosya satır satır okunur

            line = line.strip()
            # Satır başı ve sonu boşluklardan temizlenir

            if line == "NODE_COORD_SECTION":
                # Koordinatların başladığı bölüm
                reading = True
                continue

            if line == "EOF":
                # Dosyanın sonu
                break

            if reading:
                # Sadece koordinat bölümündeyken çalışır

                cid, x, y = line.split()
                # Satır şehir id, x ve y olarak ayrılır

                cities[int(cid)] = (float(x), float(y))
                # Şehir sözlüğe eklenir

    return cities
    # Tüm şehirler döndürülür


# ===================================================
# DISTANCE & FITNESS
# ===================================================

def distance(a, b):
    # İki şehir arasındaki Öklidyen mesafeyi hesaplar
    return math.hypot(a[0] - b[0], a[1] - b[1])
    # sqrt((x1-x2)^2 + (y1-y2)^2)


def calculate_fitness(solution, cities):
    # Bir turun toplam mesafesini hesaplar
    # Daha küçük değer = daha iyi çözüm

    total = 0.0
    # Toplam mesafe başlangıç değeri

    for i in range(len(solution)):
        # Turdaki her şehir için döngü

        a = cities[solution[i]]
        # Mevcut şehrin koordinatları

        b = cities[solution[(i + 1) % len(solution)]]
        # Bir sonraki şehir
        # % ile son şehirden ilk şehre dönüş sağlanır

        total += distance(a, b)
        # Mesafe toplama eklenir

    return total
    # Turun toplam uzunluğu döndürülür


# ===================================================
# RANDOM & GREEDY
# ===================================================

def random_solution(cities):
    # Rastgele ama geçerli bir TSP çözümü üretir

    sol = list(cities.keys())
    # Tüm şehirler listeye alınır

    random.shuffle(sol)
    # Şehir sırası karıştırılır

    return sol
    # Rastgele çözüm döndürülür


def greedy_solution(start, cities):
    # Greedy (Nearest Neighbor) algoritması

    unvisited = set(cities.keys())
    # Ziyaret edilmemiş şehirler

    unvisited.remove(start)
    # Başlangıç şehri çıkarılır

    sol = [start]
    # Çözüm başlangıç şehriyle başlar

    current = start
    # Mevcut şehir

    while unvisited:
        # Ziyaret edilmemiş şehir kaldığı sürece

        nxt = min(
            unvisited,
            key=lambda c: distance(cities[current], cities[c])
        )
        # Mevcut şehre en yakın şehir seçilir

        sol.append(nxt)
        # Şehir çözüme eklenir

        unvisited.remove(nxt)
        # Ziyaret edildiği için listeden çıkarılır

        current = nxt
        # Mevcut şehir güncellenir

    return sol
    # Greedy çözüm döndürülür


# ===================================================
# RANDOM SEARCH (RAPOR İÇİN)
# ===================================================

def random_search(cities, runs=100):
    # Tamamen rastgele çözümler üretir
    # İstatistiksel karşılaştırma için kullanılır

    results = []
    # Fitness değerleri tutulur

    for _ in range(runs):
        sol = random_solution(cities)
        # Rastgele çözüm oluşturulur

        results.append(calculate_fitness(sol, cities))
        # Fitness listeye eklenir

    return {
        "best": min(results),
        # En iyi rastgele sonuç

        "mean": statistics.mean(results),
        # Ortalama değer

        "std": statistics.stdev(results),
        # Standart sapma

        "var": statistics.variance(results)
        # Varyans
    }


# ===================================================
# GA OPERATORS
# ===================================================

def tournament_selection(pop, cities, k=3):
    # Tournament selection yöntemi

    competitors = random.sample(pop, k)
    # Popülasyondan k birey seçilir

    competitors.sort(key=lambda s: calculate_fitness(s, cities))
    # Fitness'a göre sıralanır

    return competitors[0]
    # En iyi birey ebeveyn olarak döndürülür


def ordered_crossover(p1, p2):
    # Ordered Crossover (OX)

    n = len(p1)
    # Şehir sayısı

    a, b = sorted(random.sample(range(n), 2))
    # Rastgele iki kesim noktası

    child = [None] * n
    # Çocuk çözüm

    child[a:b] = p1[a:b]
    # Parent1’den parça kopyalanır

    fill = [c for c in p2 if c not in child]
    # Parent2’den eksik şehirler alınır

    idx = 0
    # Fill indeksi

    for i in range(n):
        if child[i] is None:
            child[i] = fill[idx]
            idx += 1

    return child
    # Geçerli çocuk çözüm döndürülür


def inversion_mutation(sol, rate):
    # Inversion mutation

    if random.random() < rate:
        # Mutasyon olasılığı kontrol edilir

        i, j = sorted(random.sample(range(len(sol)), 2))
        # Rastgele iki indeks

        sol[i:j] = reversed(sol[i:j])
        # Seçilen aralık ters çevrilir

    return sol
    # Çözüm döndürülür


# ===================================================
# EVOLUTION
# ===================================================

def evolve_population(pop, cities, mutation_rate, elitism=1):
    # Bir nesilden diğerine geçişi sağlar

    new_pop = []
    # Yeni nesil

    sorted_pop = sorted(pop, key=lambda s: calculate_fitness(s, cities))
    # Popülasyon fitness’a göre sıralanır

    for i in range(elitism):
        new_pop.append(sorted_pop[i][:])
        # En iyi bireyler direkt korunur

    while len(new_pop) < len(pop):
        p1 = tournament_selection(pop, cities)
        # Birinci ebeveyn

        p2 = tournament_selection(pop, cities)
        # İkinci ebeveyn

        child = ordered_crossover(p1, p2)
        # Çaprazlama

        child = inversion_mutation(child, mutation_rate)
        # Mutasyon

        new_pop.append(child)
        # Yeni birey eklenir

    return new_pop
    # Yeni nesil döndürülür


# ===================================================
# MAIN
# ===================================================

DATASET = "berlin11"
# Kullanılacak veri seti

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
# Şehirler dosyadan yüklenir

start_city = list(cities.keys())[0]
# Greedy için başlangıç şehri


greedy = greedy_solution(start_city, cities)
# Greedy çözüm oluşturulur

greedy_fit = calculate_fitness(greedy, cities)
# Greedy çözümün fitness değeri

print("Greedy fitness:", greedy_fit)
# Greedy sonucu yazdırılır


print("Random search stats:", random_search(cities))
# Random search istatistikleri yazdırılır


population = [greedy]
# Popülasyon greedy çözümle başlatılır

for _ in range(POP - 1):
    population.append(random_solution(cities))
    # Rastgele çözümler eklenir


global_best = greedy_fit
# Şu ana kadarki en iyi değer

best_solution = greedy[:]
# En iyi rota

history = []
# Epoch bazlı en iyi fitness değerleri


for epoch in range(EPOCHS):
    # Genetic Algorithm ana döngüsü

    population = evolve_population(population, cities, MUT, elitism=1)
    # Yeni nesil oluşturulur

    epoch_best = min(population, key=lambda s: calculate_fitness(s, cities))
    # O anki en iyi birey

    epoch_fit = calculate_fitness(epoch_best, cities)
    # Fitness değeri

    if epoch_fit < global_best:
        global_best = epoch_fit
        best_solution = epoch_best[:]
        # Global en iyi güncellenir

    history.append(global_best)
    # Geçmişe eklenir

    if epoch % 20 == 0:
        print(f"Epoch {epoch} | Best = {global_best:.2f}")
        # İlerleme yazdırılır


print("Best GA fitness:", global_best)
# GA sonucu yazdırılır


plt.figure(figsize=(12, 5))
# Grafik alanı oluşturulur

plt.subplot(1, 2, 1)
# Sol grafik

plt.plot(history)
# GA performansı çizilir

plt.xlabel("Epoch")
plt.ylabel("Best fitness")
plt.title(f"{DATASET} – GA Performance")
plt.grid()


plt.subplot(1, 2, 2)
# Sağ grafik

x = [cities[c][0] for c in best_solution] + [cities[best_solution[0]][0]]
# X koordinatları

y = [cities[c][1] for c in best_solution] + [cities[best_solution[0]][1]]
# Y koordinatları

plt.plot(x, y, marker="o")
# En iyi rota çizilir

plt.xlabel("X")
plt.ylabel("Y")
plt.title(f"{DATASET} – Best Route")
plt.grid()

plt.tight_layout()
# Grafik düzeni ayarlanır

plt.show()
# Grafikler gösterilir





















