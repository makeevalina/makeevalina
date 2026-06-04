import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import solve

# моя функция
def f(x):
    return x * (np.log(x + 2)) ** 2

# генерируем экспериментальные данные
m = 60  # количество различных x (>=50)
nums = 3  # число измерений в каждой точке
ampl = 0.05  # относительная погрешность
x_min, x_max = 0.0, 4.0  # отрезок, где функция определена и гладкая

x = np.linspace(x_min, x_max, m)
y_exp = []  # список списков измерений для каждой точки
y_avg = []  # средние значения по измерениям

for xi in x:
    true_val = f(xi)
    # Генерируем nums измерений с относительной погрешностью ampl
    measurements = [true_val * (1 + np.random.uniform(-ampl, ampl))
                    for _ in range(nums)]
    y_exp.append(measurements)
    y_avg.append(np.mean(measurements))

# Переводим в массивы numpy, чтобы было убоднее
x_arr = np.array(x)
y_arr = np.array(y_avg)

print("Сгенерировано точек:", m)

# построение матрицы вандермонда размера len(x) x (degree+1)
def vandermonde(x, degree):
    m = len(x)
    V = np.zeros((m, degree + 1))
    for i in range(m):
        for k in range(degree + 1):
            V[i, k] = x[i] ** k
    return V

# возвращаем коэффициенты полинома степени degree по методу нормальных уравнений
def normal_equations(x, y, degree):
    # Строим нормальные уравнения: V^T * V * a = V^T * y
    V = vandermonde(x, degree)
    A = V.T @ V  # матрица системы
    b = V.T @ y  # правая часть
    coeffs = solve(A, b)  # решение слау Ax=b методом гаусса
    return coeffs

# значение полинома в заданных точках
def polyval(coeffs, x):
    res = np.zeros_like(x)
    for k, c in enumerate(coeffs):
        res += c * (x ** k)
    return res

# ортогональные многочлены
def build_orthogonal_polynomials(x, max_degree):
    """
    Строит ортогональные многочлены q0, q1, ..., q_{max_degree}
    на системе точек x
    Возвращает словари: q[k] – массив значений q_k(x_i),
                        norm2[k] – сумма квадратов q_k(x_i)
    """
    m = len(x)
    q = {}
    norm2 = {}
    # q0(x) = 1
    q[0] = np.ones(m)
    norm2[0] = np.sum(q[0] ** 2)

    if max_degree == 0:
        return q, norm2

    # q1(x) = x - alpha1, где alpha1 = (sum x_i)/m
    alpha1 = np.mean(x)
    q[1] = x - alpha1
    norm2[1] = np.sum(q[1] ** 2)

    # Рекуррентное построение для k = 1,2,..., max_degree-1
    for k in range(1, max_degree):
        # вычисляем alpha_{k+1} и beta_k
        alpha = np.sum(x * q[k] ** 2) / norm2[k]
        beta = np.sum(x * q[k] * q[k - 1]) / norm2[k - 1]
        q_next = (x - alpha) * q[k] - beta * q[k - 1]
        q[k + 1] = q_next
        norm2[k + 1] = np.sum(q_next ** 2)
    return q, norm2

# прямая реализация формулы для ak
def ortho_coeffs(y, q, norm2, degree):
    coeffs = []
    for k in range(degree + 1):
        ak = np.sum(y * q[k]) / norm2[k]
        coeffs.append(ak)
    return coeffs

# вычисление итогового полинома
def ortho_polyval(coeffs, q, x_points, degree):
    # P(x_i) = sum a_k * q[k][i]
    res = np.zeros(len(x_points))
    for k in range(degree + 1):
        res += coeffs[k] * q[k]
    return res

# расчёт для степеней 1, 2, 3, 4, 5
degrees = [1, 2, 3, 4, 5]
sse_normal = []
sse_ortho = []

# Построим ортогональные полиномы до максимальной степени (5)
max_deg = max(degrees)
q_dict, norm2_dict = build_orthogonal_polynomials(x_arr, max_deg)

for n in degrees:
    # ---- Нормальные уравнения ----
    coeffs_n = normal_equations(x_arr, y_arr, n)
    y_pred_n = polyval(coeffs_n, x_arr)
    err_n = np.sum((y_arr - y_pred_n) ** 2)
    sse_normal.append(err_n)

    # ---- Ортогональные многочлены ----
    coeffs_o = ortho_coeffs(y_arr, q_dict, norm2_dict, n)
    y_pred_o = ortho_polyval(coeffs_o, q_dict, x_arr, n)
    err_o = np.sum((y_arr - y_pred_o) ** 2)
    sse_ortho.append(err_o)

# выведем таблицу
print("Таблица 1. Суммы квадратов ошибок (SSE) для разных степеней полинома")
print("-" * 70)
print(f"{'Степень n':>10} | {'Нормальные ур-я':>20} | {'Ортогональные многочлены':>25}")
print("-" * 70)
for n, err_n, err_o in zip(degrees, sse_normal, sse_ortho):
    print(f"{n:10d} | {err_n:20.10e} | {err_o:25.10e}")
print("-" * 70)

# построение графиков для каждой степени
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
for idx, n in enumerate(degrees):
    ax = axes[idx]
    # Получаем значения полинома для текущей степени методом нормальных уравнений
    coeffs = normal_equations(x_arr, y_arr, n)
    y_poly = polyval(coeffs, x_arr)
    # Экспериментальные точки
    ax.scatter(x_arr, y_arr, color='red', s=15, label='experimental points')
    ax.plot(x_arr, y_poly, 'b-', linewidth=2, label=f'polynomial degree {n}')
    ax.set_title(f'Аппроксимация степени {n}')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
# удаление лишнего подграфика
for j in range(len(degrees), len(axes)):
    axes[j].set_visible(False)
plt.tight_layout()
plt.show()
