# Bitcoin Mining Model

Návod, jak spustit model simulace těžby Bitcoinu napsaný pomocí frameworku **Mesa**. Model umožňuje simulaci těžby Bitcoinu v závislosti na různých parametrech, jako jsou hashrate těžařů, cena Bitcoinu a obtížnost těžby.

## 1. **Naklonování repozitáře**

Nejprve naklonujte repozitář s projektem z GitHubu.

```bash
git clone https://github.com/joachim162/Bitcoin-Mining-model
cd Bitcoin-Mining-model
```

## 2. **Příprava prostředí**

### Instalace Docker a Docker Compose

Ujistěte se, že máte nainstalovaný Docker a jeho plugin Docker Compose. Pokud nemáte, postupujte podle oficiální dokumentace: 

- [Průvodce pro instalaci Docker](https://docs.docker.com/get-docker/).
- [Průvodce pro instalaci Docker Compose](https://docs.docker.com/compose/install/).

## 3. **Spuštění modelu**

Pro spuštění modelu použijte následující příkaz (platí pro Linux, macOS i Windows):

```bash
docker-compose up
```

## 4. **Přístup k modelu pomocí webového rozhraní**

Po spuštění modelu otevřete ve vašem webovém prohlížeči adresu:

```
http://localhost:8521
```

Zde se zobrazí grafické uživatelské rozhraní simulace, které vám umožní sledovat a analyzovat chování modelu.

## 5. **Jak model funguje**

### **Hlavní komponenty modelu**

1. **Těžaři (Miner)** - Agent
   - Těžaři mají individuální **hashrate** (výpočetní výkon), který určuje pravděpodobnost nalezení nového bloku.
   - Těžaři dynamicky přizpůsobují svůj hashrate na základě ceny bitcoinu.

 **Cena Bitcoinu (Bitcoin Price)**
   - Cena Bitcoinu je simulována s výskytem náhlých šoků (prudký růst nebo pokles).  
   - Změny ceny ovlivňují rozhodnutí těžařů o jejich hashrate v síti.

3. **Obtížnost těžby (Difficulty)**  
   - Obtížnost je klíčový parametr, který určuje, jak složité je nalézt nový blok.  
   - Pokud je průměrná doba na nalezení bloku vyšší než cílový čas, obtížnost se zvýší.  
   - Pokud je doba kratší, obtížnost se sníží.  

4. **Bloky a odměny**  
   - Těžaři získávají **odměnu za blok** vynásobenou aktuální cenou Bitcoinu.  
   - Model sleduje počet vytěžených bloků a odměny, které jednotliví těžaři získali.

5. **Síťový hashrate**  
   - Celkový výkon sítě je součtem hashrate aktivních těžařů.  
   - Výkon sítě a obtížnost spolu úzce souvisí: čím vyšší je hashrate, tím roste pravděpodobnost dřívějšího vytěžení bloku.

### **Průběh simulace**

1. **Inicializace modelu**  
   - Model je inicializován s určitým počtem těžařů. Uživatel si počet může zvolit sám.

1. **Časové kroky (Steps)**  
   - V každém kroku simulace:  
     - Těžaři provádějí těžbu a kontrolují, zda našli nový blok.
     - Cena Bitcoinu se aktualizuje pomocí náhodného růstu nebo poklesu.  
     - Těžaři přizpůsobují svůj hashrate na základě změn ceny bitcoinu.  
     - Model kontroluje a upravuje obtížnost těžby každých 50 bloků (neodpovídá realitě – pouze jako ukázka).

### **Sledované metriky**

Model poskytuje důležité metriky, které můžete sledovat pomocí grafů:

- **Celkový výkon sítě (Total Hash Rate)**: Ukazuje celkový výpočetní výkon všech těžařů.  
- **Obtížnost (Difficulty)**: Dynamicky se mění na základě průměrného času pro těžbu bloku.  
- **Počet bloků (Blocks Mined)**: Celkový počet bloků, které byly vytěženy během simulace.  
- **Cena Bitcoinu (Bitcoin Price)**: Simulovaná cena Bitcoinu v čase.  
- **Počet aktivních těžařů (Active Miners)**: Počet těžařů.

### **Interaktivní prvky**

Ve webovém rozhraní může uživatel experimentovat s následujícími parametry:

- **Počet těžařů (Number of Miners)**: Umožňuje nastavit počet těžařů na začátku simulace.  
- **Vizualizace mřížky**: Zobrazuje stav těžarů.
- **Grafy**: Interaktivní grafy ukazují změny hashratu, ceny Bitcoinu, obtížnosti a dalších metrik v čase.

## 6. **Zastavení modelu**

Pro zastavení modelu použijte v terminálu klávesovou zkratku **Ctrl+C**. Chcete-li odstranit vytvořené kontejnery, spusťte:

```bash
docker-compose down
```

## 7. **Další úpravy a rozšíření**

Model je napsán v Pythonu pomocí frameworku **Mesa**, který umožňuje snadnou úpravu a rozšíření:

- Chcete-li upravit chování těžařů nebo simulaci ceny Bitcoinu, editujte soubory v adresáři projektu. Díky tomu že má kontejner přímý přístup k souborům repozitáře se aplikace po modifikaci kódu automaticky restartuje.
- Hlavní soubor modelu je `bitcoin_mining_simulation.py`.
