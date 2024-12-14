# Bitcoin Mining Model

Návod jak spustit model napsaný pomocí frameworku Mesa v Dockeru za použití Docker Compose.

## 1. Naklonování repozitáře

Nejprve naklonujte repozitář s projektem z GitHubu.

```bash
git clone https://github.com/joachim162/Bitcoin-Mining-model
cd Bitcoin-Mining-model
```

## 2. Příprava prostředí

### Instalace Docker a Docker Compose

Ujistěte se, že máte nainstalovaný Docker a jeho plugin Docker Compose. Pokud nemáte, postupujte podle oficiální dokumentace: 

- [Průvodce pro instalaci Docker](https://docs.docker.com/get-docker/).
- [Průvodce pro instalaci Docker Compose](https://docs.docker.com/compose/install/) 

## 3. Spuštění modelu

Spusťte model následujícím příkazem (v Linuxu, macOS i Windows je postup stejný):
```bash
docker-compose up
```

## 4. Přístup k modelu pomocí webového rozhraní

Pro přístup k webovému rozhraní modelu otevřete ve vašem prohlížeči adresu:
```
http://localhost:8521
```

