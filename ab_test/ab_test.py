import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sqlalchemy import create_engine

# Подключение к базе данных PostgreSQL
engine = create_engine('postgresql://postgres:ACCORD@localhost:5432/test_database')

# Стоимость картин для двух направлений
query = """
WITH movement_prices AS (
    SELECT 
        aw.estimated_value_eur,
        am.movement_name
    FROM artworks aw
    JOIN artist_movements amv ON aw.artist_id = amv.artist_id
    JOIN art_movements am ON amv.movement_id = am.movement_id
    WHERE am.movement_name IN ('Impressionism', 'Post-Impressionism')
      AND aw.estimated_value_eur IS NOT NULL
)
SELECT * FROM movement_prices;
"""

df = pd.read_sql(query, engine)

impressionism = df[df['movement_name'] == 'Impressionism']['estimated_value_eur']
post_impressionism = df[df['movement_name'] == 'Post-Impressionism']['estimated_value_eur']

print("Количество картин импрессионистов:", len(impressionism))
print("Количество картин постимпрессионистов:", len(post_impressionism))
print("Средняя стоимость импрессионистов: {:.2f} €".format(impressionism.mean()))
print("Средняя стоимость постимпрессионистов: {:.2f} €".format(post_impressionism.mean()))

# Статистический тест (Манна-Уитни — аналог t-test для любых распределений)
stat, p_value = stats.mannwhitneyu(impressionism, post_impressionism, alternative='greater')
print("\n Результаты теста Манна-Уитни:")
print(f"   U-statistic = {stat:.4f}")
print(f"   p-value = {p_value:.6f}")

alpha = 0.05
if p_value < alpha:
    print("Отвергаем нулевую гипотезу: есть статистически значимая разница")
    if impressionism.mean() > post_impressionism.mean():
        print("Импрессионисты в среднем дороже постимпрессионистов")
    else:
        print("Постимпрессионисты в среднем дороже")
else:
    print("Не отвергаем нулевую гипотезу: разница статистически не значима")

# Визуализация
fig, ax = plt.subplots(figsize=(10, 6))

df.boxplot(column='estimated_value_eur', by='movement_name', ax=ax)

plt.title('Распределение стоимости картин по направлениям', fontsize=14, fontweight='bold')
plt.suptitle('')  # убираем автоматический заголовок pandas
plt.ylabel('Стоимость, €', fontsize=12)
plt.xticks(rotation=45, fontsize=10)

from matplotlib.lines import Line2D
from matplotlib.patches import Patch

legend_elements = [
    Patch(facecolor='white', edgecolor='blue', label='Ящик (25-75 процентили)'),
    Line2D([0], [0], color='green', linewidth=2, label='Медиана'),
    Line2D([0], [0], color='black', linewidth=1, label='Границы типичного разброса'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='black',
           markersize=8, markeredgewidth=1, label='Выбросы')
]

ax.legend(
    handles=legend_elements,
    loc='center left',
    fontsize=9,
    framealpha=0.9,
    bbox_to_anchor=(1, 0.5)
)

plt.tight_layout()
plt.savefig('ab_test_boxplot_with_legend.png', dpi=300)
plt.show()
