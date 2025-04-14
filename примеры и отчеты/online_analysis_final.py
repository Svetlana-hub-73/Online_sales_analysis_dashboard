import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from pptx import Presentation
from pptx.util import Inches
import os

# Настройка стиля графиков
sns.set(style="whitegrid")

# ───────── Загрузка и очистка данных ───────── #
df = pd.read_csv("online_store_data.csv")

df['category'] = df['category'].astype(str).str.strip().str.lower()
df['product_name'] = df['product_name'].astype(str).str.lower()
df['brand'] = df['brand'].astype(str).str.strip()
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce')
df['rating'] = df['rating'].astype(str).str.extract(r'([\d.]+)').astype(float)
df['num_of_ratings'] = pd.to_numeric(df['num_of_ratings'], errors='coerce')

st.title("📊 Анализ онлайн-продаж")

# ───────── 1. Разница рейтинга среди телевизоров ───────── #
tv_df = df[df['category'].str.contains('tv') | df['product_name'].str.contains('tv')]
if not tv_df.empty:
    tv_rating_diff = tv_df['rating'].max() - tv_df['rating'].min()
    st.subheader("1. Разница рейтинга среди телевизоров")
    st.write(f"Разница: {tv_rating_diff:.2f}")

    fig, ax = plt.subplots()
    sns.histplot(tv_df['rating'], bins=10, kde=True, ax=ax)
    ax.set_title("Распределение рейтингов телевизоров")
    st.pyplot(fig)

# ───────── 2. Межквартильный диапазон цен для смартфонов ───────── #
smartphones_df = df[df['category'].str.contains('smartphone')]
if not smartphones_df.empty:
    q1 = smartphones_df['price'].quantile(0.25)
    q3 = smartphones_df['price'].quantile(0.75)
    iqr = q3 - q1
    st.subheader("2. IQR цен для смартфонов")
    st.write(f"IQR: {iqr:.1f}")

    fig2, ax2 = plt.subplots()
    sns.boxplot(x=smartphones_df['price'], ax=ax2)
    ax2.set_title("Boxplot цен смартфонов")
    st.pyplot(fig2)

# ───────── 3. Бренды с наиболее стабильными рейтингами ───────── #
stable_brands_df = df.dropna(subset=['brand', 'rating'])
brand_std = stable_brands_df.groupby('brand')['rating'].std().dropna().sort_values().head(5)

st.subheader("3. Бренды с наиболее стабильными рейтингами")
st.dataframe(brand_std)

fig3, ax3 = plt.subplots()
brand_std.plot(kind='barh', ax=ax3, color='skyblue')
ax3.set_title("ТОП-5 брендов с минимальным разбросом рейтингов")
st.pyplot(fig3)

# ───────── 4. Продажи по квартилям количества оценок ───────── #
df['rating_quartile'] = pd.qcut(df['num_of_ratings'], 4, labels=[
    '1-й квартиль', '2-й квартиль', '3-й квартиль', '4-й квартиль'
])
quartile_sales = df.groupby('rating_quartile', observed=True)['quantity_sold'].sum()

st.subheader("4. Продажи по квартилям количества оценок")
st.dataframe(quartile_sales)

fig4, ax4 = plt.subplots()
sns.barplot(x=quartile_sales.index, y=quartile_sales.values,
            hue=quartile_sales.index, palette='viridis', legend=False, ax=ax4)
ax4.set_title("Продажи по квартилям")
st.pyplot(fig4)

# ───────── 5. Генерация презентации PowerPoint ───────── #
prs = Presentation()
title_slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)
slide.shapes.title.text = "Анализ данных онлайн-магазина"
slide.placeholders[1].text = "Продажи, рейтинги, бренды, корреляции"

def add_slide(title, content):
    layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title
    slide.placeholders[1].text = content

add_slide("1. Рейтинг ТВ", f"Разница рейтингов: {tv_rating_diff:.2f}")
add_slide("2. Смартфоны", f"IQR цен: {iqr:.1f}")
add_slide("3. ТОП-бренды", brand_std.to_string())
add_slide("4. Квартильные продажи", quartile_sales.to_string())

pptx_path = "presentation_output.pptx"
prs.save(pptx_path)
st.success("Презентация сгенерирована!")
st.download_button("📥 Скачать презентацию", data=open(pptx_path, "rb"), file_name="online_analysis.pptx")

