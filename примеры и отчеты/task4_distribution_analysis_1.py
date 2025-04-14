import pandas as pd

# Загружаем CSV
df = pd.read_csv('online_store_data.csv')

# ----------------- Очистка и подготовка -----------------
# Преобразуем рейтинг: "8.75 out of 10" → 8.75
df['rating'] = df['rating'].str.extract(r'(\d+\.?\d*)').astype(float)

# Преобразуем числовые колонки
df['price'] = df['price'].astype(float)
df['quantity_sold'] = df['quantity_sold'].astype(float)
df['num_of_ratings'] = pd.to_numeric(df['num_of_ratings'], errors='coerce')
df = df.dropna(subset=['num_of_ratings'])
df['num_of_ratings'] = df['num_of_ratings'].astype(int)
# Приводим категории к нижнему регистру для надёжности
df['category'] = df['category'].str.lower()

# ------------------------- ВОПРОС 1 -------------------------
# Разница между лучшим и худшим телевидением (в нашем примере таких нет, но покажем общий подход)
tv_df = df[df['category'] == 'televisions']
if not tv_df.empty:
    tv_rating_range = tv_df['rating'].max() - tv_df['rating'].min()
else:
    tv_rating_range = "Нет телевизоров в выборке"

print("1. Разница рейтинга среди телевизоров:", tv_rating_range)

# ------------------------- ВОПРОС 2 -------------------------
# IQR цен среди смартфонов
phone_df = df[df['category'] == 'smartphones']
if not phone_df.empty:
    q1 = phone_df['price'].quantile(0.25)
    q3 = phone_df['price'].quantile(0.75)
    iqr = q3 - q1
else:
    iqr = "Нет смартфонов в выборке"

print("\n2. Межквартильный диапазон цен для смартфонов:", iqr)

# ------------------------- ВОПРОС 3 -------------------------
# Топ-5 брендов с наименьшим отклонением рейтинга
brand_rating_std = df.groupby('brand')['rating'].std().dropna().sort_values()
top5_stable_brands = brand_rating_std.head(5)

print("\n3. Бренды с наиболее стабильными рейтингами:")
print(top5_stable_brands)

# ------------------------- ВОПРОС 4 -------------------------
# Делим по квартилям по количеству оценок
quartiles = df['num_of_ratings'].quantile([0.25, 0.5, 0.75])

def assign_quartile(value):
    if value <= quartiles[0.25]:
        return '1-й квартиль'
    elif value <= quartiles[0.5]:
        return '2-й квартиль'
    elif value <= quartiles[0.75]:
        return '3-й квартиль'
    else:
        return '4-й квартиль'

df['rating_quartile'] = df['num_of_ratings'].apply(assign_quartile)

# Суммарные продажи по квартилям
quartile_sales = df.groupby('rating_quartile')['quantity_sold'].sum()

print("\n4. Продажи по квартилям количества оценок:")
print(quartile_sales)
