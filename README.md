# Bitcoin Mining Model v Dockeru

Tato dokumentace popisuje, jak spustit model simulace těžby Bitcoinu napsaný pomocí frameworku **Mesa**. Model umožňuje simulaci těžby Bitcoinu v závislosti na různých parametrech, jako jsou hashrate těžařů, cena Bitcoinu a obtížnost těžby.

## 1. Naklonování repozitáře

Nejprve naklonujte repozitář s projektem z GitHubu:
```bash
git clone https://github.com/joachim162/Bitcoin-Mining-model
cd Bitcoin-Mining-model
```

## 2. Příprava prostředí

### Instalace Docker a Docker Compose

Ujistěte se, že máte nainstalovaný Docker a jeho plugin Docker Compose. Pokud nemáte, postupujte podle oficiální dokumentace: 
- [Průvodce pro instalaci Docker](https://docs.docker.com/get-docker/)
- [Průvodce pro instalaci Docker Compose](https://docs.docker.com/compose/install/)

## 3. Struktura Docker konfigurace

### Dockerfile
Projekt obsahuje `Dockerfile`, který definuje, jak se má vytvořit Docker image pro náš model. Dockerfile specifikuje:
- Základní Python image
- Pracovní adresář v kontejneru
- Kopírování zdrojových souborů modelu
- Instalaci potřebných závislostí z `requirements.txt`
- Konfiguraci webového serveru pro Mesa rozhraní

### Docker Compose
Soubor `docker-compose.yml` definuje služby, které má Docker spustit, včetně:
- Názvu služby
- Cesty k Dockerfile
- Mapování portu 8521 pro webové rozhraní
- Mapování volumes pro přímý přístup k souborům projektu
- Konfigurace prostředí pro vývoj

## 4. Spuštění modelu

Když spustíte příkaz:
```bash
docker-compose up
```

Následuje tento proces:
1. Docker Compose načte konfiguraci z `docker-compose.yml`
2. Pokud image ještě neexistuje, Docker sestaví novou image podle instrukcí v Dockerfile
3. Vytvoří a spustí kontejner z této image
4. Spustí Mesa server na portu 8521

### Přístup k webovému rozhraní
Po spuštění kontejneru můžete přistoupit k modelu přes webový prohlížeč na adrese:
```
http://localhost:8521
```

## 5. Komponenty a funkcionalita modelu

### Hlavní komponenty modelu

1. **Těžaři (Miner) - Agent**
   - Každý těžař má vlastní hashrate určující pravděpodobnost nalezení bloku
   - Dynamické přizpůsobování hashratu podle ceny bitcoinu

2. **Cena Bitcoinu**
   - Simulace včetně náhlých cenových šoků
   - Ovlivňuje chování těžařů

3. **Obtížnost těžby**
   - Dynamicky se upravuje každých 50 bloků
   - Reaguje na průměrnou dobu těžby bloků

4. **Bloky a odměny**
   - Systém odměn za vytěžené bloky
   - Sledování statistik jednotlivých těžařů

5. **Hashrate sítě**
   - Agregace výkonu všech aktivních těžařů
   - Vliv na pravděpodobnost těžby

### Průběh simulace

1. **Inicializace**
   - Nastavení počátečního počtu těžařů
   - Inicializace parametrů sítě

2. **Časové kroky**
   - Těžba bloků
   - Aktualizace ceny Bitcoinu
   - Přizpůsobení hashratu těžařů
   - Úprava obtížnosti

### Sledované metriky
Model vizualizuje v reálném čase:
- Celkový hashrate sítě
- Aktuální obtížnost
- Počet vytěžených bloků
- Cenu Bitcoinu
- Počet aktivních těžařů

### Interaktivní prvky
Webové rozhraní nabízí:
- Nastavení počtu těžařů
- Vizualizaci stavu těžařů v mřížce
- Interaktivní grafy metrik

## 6. Správa kontejneru

Užitečné příkazy pro práci s modelem:
```bash
# Zastavení modelu
Ctrl+C

# Odstranění kontejnerů
docker-compose down

# Zobrazení logů
docker-compose logs

# Přestavění image
docker-compose build --no-cache
```

## 7. Vývoj a úpravy

Model podporuje hot-reload během vývoje:
- Soubory projektu jsou namapované do kontejneru
- Změny v kódu se projeví po automatickém restartu aplikace
- Úpravy lze provádět v Python souborech bez nutnosti rebuildu kontejneru

## 8. Řešení problémů

Při potížích zkontrolujte:
1. Dostupnost portu 8521
2. Oprávnění pro práci s Dockerem
3. Správnost instalace všech závislostí
4. Logy kontejneru pomocí `docker-compose logs`
