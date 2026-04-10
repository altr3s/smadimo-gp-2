# SMADIMO-GP-2

## Git workflow проекта

Репозиторий: https://github.com/altr3s/SMADIMO-GP-2.git

### 1. Клонирование проекта

Сначала необходимо склонировать репозиторий и перейти в папку проекта:

```bash
git clone https://github.com/altr3s/SMADIMO-GP-2.git
```

```bash
cd SMADIMO-GP-2
```

### 2. Переход на ветку разработки

После клонирования переключаемся на основную ветку разработки `dev`:

```bash
git checkout dev
```

### 3. Создание feature-ветки

Все изменения выполняются в отдельной feature-ветке, которая создается от dev.

```bash
git checkout -b feature/{first_name}-{description-feature}
```

### 4. Разработка

Вносите изменения в код, фиксируя их через коммиты:

```bash
git add .
git commit -m "{commit describtion}"
```

### 5. Пуш изменений в ветку

После завершения разработки отправьте ветку в удаленный репозиторий:

```bash
git push origin -u feature/{first_name}-{description-feature}
```

### 6. Создание Pull Request

После того как задача реализована, необходимо создать Pull Request в ветку dev.
