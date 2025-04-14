import pandas as pd

# Загрузка данных
df = pd.read_csv("online_store_data.csv")  # замени на путь к своему CSV

# Очистка и преобразование
df['category'] = df['category'].astype(str).str.strip().str.lower()
df['product_name'] = df['product_name'].astype(str).str.lower()
df['brand'] = df['brand'].astype(str).str.strip()

# Преобразуем нужные столбцы в числовой тип
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce')
df['rating'] = df['rating'].str.extract(r'([\d.]+)').astype(float)
df['num_of_ratings'] = pd.to_numeric(df['num_of_ratings'], errors='coerce')

# ───────── 1. Разница рейтинга среди телевизоров ───────── #
tv_df = df[df['category'].str.contains('tv') | df['product_name'].str.contains('tv')]
if not tv_df.empty:
    tv_rating_diff = tv_df['rating'].max() - tv_df['rating'].min()
    print(f"1. Разница рейтинга среди телевизоров: {tv_rating_diff:.2f}")
else:
    print("1. Телевизоры не найдены в данных")

# ───────── 2. Межквартильный диапазон цен для смартфонов ───────── #
smartphones_df = df[df['category'].str.contains('smartphone')]
if not smartphones_df.empty:
    q1 = smartphones_df['price'].quantile(0.25)
    q3 = smartphones_df['price'].quantile(0.75)
    iqr = q3 - q1
    print(f"\n2. Межквартильный диапазон цен для смартфонов: {iqr:.1f}")
else:
    print("\n2. Смартфоны не найдены")

# ───────── 3. Бренды с наиболее стабильными рейтингами ───────── #
# Убираем бренды с NaN
stable_brands_df = df.dropna(subset=['brand', 'rating'])
brand_std = stable_brands_df.groupby('brand')['rating'].std().dropna().sort_values().head(5)

print("\n3. Бренды с наиболее стабильными рейтингами:")
print(brand_std)

# ───────── 4. Продажи по квартилям количества оценок ───────── #
df['rating_quartile'] = pd.qcut(df['num_of_ratings'], 4, labels=[
    '1-й квартиль', '2-й квартиль', '3-й квартиль', '4-й квартиль'
])
quartile_sales = df.groupby('rating_quartile', observed=True)['quantity_sold'].sum()

print("\n4. Продажи по квартилям количества оценок:")
print(quartile_sales)
