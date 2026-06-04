import math
import numpy as np
import matplotlib.pyplot as plt

#интервал и число проверочных точек
A = 1.0
B = 3.0
M = 1000 #M>>n?

#функция
def f(x):
    return math.cos(x)/math.sin(x) + x*x

#равноотстоящие узлы
def equidistant_nodes(n, a, b):
    x = []
    for i in range(n):
        x.append(a + i*(b-a)/(n-1))
    return x

#оптимальные (чебышевские) узлы
def chebyshev_nodes(n, a, b):
    x = []
    for i in range(n):
        t = (2*i + 1)/(2*n)*math.pi
        xi = 0.5*((b-a)*math.cos(t)+(b+a))
        x.append(xi)
    return x

#проверочные точки
def check_points(a, b, m):
    return [(a + i*(b-a)/(m-1)) for i in range(m)]

#находим точки и вычисляем в них значения функции
t = check_points(A, B, M)
f_vals = [f(x) for x in t]

#ПОЛИНОМ ЛАГРАНЖА
#x_val - точка, в которой хотим вычислить значение интер полинома, xn - список координат узлов интерполяции
def lagrange_point(x_val, xn, yn):
    n = len(xn)
    res = 0.0
    for i in range(n):
        li = 1.0
        for j in range(n):
            if j != i:
                li *= (x_val - xn[j])/(xn[i] - xn[j])
        res += li*yn[i]
    return res

#значения сразу всех проверочных точек
def lagrange_vec(xn, yn, t):
    return[lagrange_point(x, xn, yn) for x in t]

#ПОЛИНОМ НЬЮТОНА
#вычисление разделённых разностей
def newton_coef(xn, yn):
    n = len(xn)
    cc = list(yn) #копия значений, будем перезаписывать
    coeffs = [cc[0]]
    for k in range(1, n):
        for i in range(n-k):
            cc[i] = (cc[i+1] - cc[i])/(xn[i+k] - xn[i])
        coeffs.append(cc[0])
    return coeffs

#вычисление значения полинома в точке (использкем схему горнера, идём от старшего коэффициента к младшему)
def newton_point(x_val, xn, coeffs):
    n = len(coeffs)
    res = coeffs[-1]
    for k in range(n-2, -1, -1):
        res = res*(x_val - xn[k]) + coeffs[k]
    return res

#значения в точках t
def newton_vec(xn, yn, t):
    coeffs = newton_coef(xn, yn)
    return [newton_point(x, xn, coeffs) for x in t]


#вспомогательная функция для оценки погрешности
def max_err(t, f_vals, p_vals):
    return max(abs(f - p) for f, p in zip(f_vals, p_vals))

n_list = [3, 5, 10, 15, 20, 30, 50, 70, 100]

#ЧАСТЬ 1. ПОЛИНОМЫ ЛАГРАНЖА И НЬЮТОНА

#----Таблица 1: Лагранж----
print("\nТаблица 1. Полином Лагранжа")
print("-" * 65)
print(f"{'n':>4} | {'m':>5} | {'RL_n (равноотст.)':>25} | {'RLopt_n (чебышёв.)':>25}")
print("-" * 65)

#словари для хранения значений полиномов (для графиков)
lag_eq_plot = {} 
lag_opt_plot = {}

for n in n_list:
    #для равноотстоящих узлов
    xe = equidistant_nodes(n, A, B)
    ye = [f(x) for x in xe]
    Le = lagrange_vec(xe, ye, t)
    rl_eq = max_err(t, f_vals, Le)

    #для чебышёвских
    xc = chebyshev_nodes(n, A, B)
    yc = [f(x) for x in xc]
    Lc = lagrange_vec(xc, yc, t)
    rl_opt = max_err(t, f_vals, Lc)

    print(f"{n:4} | {M:5} | {rl_eq:25.10e} | {rl_opt:25.10e}")

    #сохраняем значения для графиков
    if n in (5, 15, 30):
        lag_eq_plot[n] = Le
        lag_opt_plot[n] = Lc
print("-" * 65)

#----Таблица 2: Ньютон----
print("\nТаблица 2. Полином Ньютона")
print("-" * 65)
print(f"{'n':>4} | {'m':>5} | {'RN_n (равноотст.)':>25} | {'RNopt_n (чебышёв.)':>25}")
print("-" * 65)

newt_eq_plot = {}
newt_opt_plot = {}

for n in n_list:
    xe = equidistant_nodes(n, A, B)
    ye = [f(x) for x in xe]
    Ne = newton_vec(xe, ye, t)
    rn_eq = max_err(t, f_vals, Ne)

    xc = chebyshev_nodes(n, A, B)
    yc = [f(x) for x in xc]
    Nc = newton_vec(xc, yc, t)
    rn_opt = max_err(t, f_vals, Nc)

    print(f"{n:4} | {M:5} | {rn_eq:25.10e} | {rn_opt:25.10e}")

    if n in (5, 15, 30):
        newt_eq_plot[n] = Ne
        newt_opt_plot[n] = Nc
print("-" * 65)

#----Графики для полиномов----
print("\nПостроение графиков полиномов...")
n_plot = [5, 15, 30]
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
styles = ['--', '-.', ':']

# Лагранж
plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
plt.plot(t, f_vals, 'k-', lw=2.5, label='f(x)')
for i, n in enumerate(n_plot):
    plt.plot(t, lag_eq_plot[n], color=colors[i], linestyle=styles[i], lw=2.5, label=f'L_{n}')
plt.title('Лагранж: равноотстоящие узлы')
plt.grid(True, alpha=0.3)
plt.legend()
plt.subplot(1, 2, 2)
plt.plot(t, f_vals, 'k-', lw=2.5, label='f(x)')
for i, n in enumerate(n_plot):
    plt.plot(t, lag_opt_plot[n], color=colors[i], linestyle=styles[i], lw=2.5, label=f'Lopt_{n}')
plt.title('Лагранж: чебышёвские узлы')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# Ньютон
plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
plt.plot(t, f_vals, 'k-', lw=2.5, label='f(x)')
for i, n in enumerate(n_plot):
    plt.plot(t, newt_eq_plot[n], color=colors[i], linestyle=styles[i], lw=2.5, label=f'N_{n}')
plt.title('Ньютон: равноотстоящие узлы')
plt.grid(True, alpha=0.3)
plt.legend()
plt.subplot(1, 2, 2)
plt.plot(t, f_vals, 'k-', lw=2.5, label='f(x)')
for i, n in enumerate(n_plot):
    plt.plot(t, newt_opt_plot[n], color=colors[i], linestyle=styles[i], lw=2.5, label=f'Nopt_{n}')
plt.title('Ньютон: чебышёвские узлы')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()


# ЧАСТЬ 2. СПЛАЙНЫ

print("\n" + "=" * 80)
print("ЧАСТЬ 2. СПЛАЙНЫ")
print("=" * 80)

#---Линейный сплайн S1,0 (дефект 1)---
#кусочно-линейный сплайн, строим прямые между двумя точками 
def spline_linear(xn, yn, x):
    for i in range(len(xn) - 1):
        if xn[i] <= x <= xn[i + 1]:
            h = xn[i + 1] - xn[i]
            a1 = (yn[i + 1] - yn[i]) / h
            return a1 * x + (yn[i] - a1 * xn[i])
    return spline_linear(xn, yn, xn[-2])

def spline_linear_vec(xn, yn, t):
    return [spline_linear(xn, yn, x) for x in t]

#---Квадратичный сплайн S2,1 (естественный, дефект 1: q1'(x0)=0, т.е. задано ограничение на конце)---
#возвращает список кортежей (xi, xj, a2, a1, a0)
def build_quad_spline(xn, yn):
    segs = []
    d = 0.0 #естественное условие
    for i in range(len(xn) - 1):
        xi, xj = xn[i], xn[i + 1]
        yi, yj = yn[i], yn[i + 1]
        h = xj - xi
        a2 = ((yj - yi) / h - d) / h
        a1 = d - 2 * a2 * xi
        a0 = yi - a2 * xi * xi - a1 * xi
        segs.append((xi, xj, a2, a1, a0))
        d = 2 * a2 * xj + a1 #производная в правом конце - для следующего отрезка
    return segs

def spline_quad(segs, x):
    for xi, xj, a2, a1, a0 in segs:
        if xi <= x <= xj:
            return a2 * x * x + a1 * x + a0
    _, _, a2, a1, a0 = segs[-1]
    return a2 * x * x + a1 * x + a0

def spline_quad_vec(segs, t):
    return [spline_quad(segs, x) for x in t]

#---Кубический сплайн S3,2 (естественный, дефект 1: M0=Mn-1=0)---
#метод прогонки для решения треёхдиагональной СЛАУ, low, diag, up - нижняя, главная и верхняя диагонали. rhs- правая часть
def progonka(low, diag, up, rhs):
    n = len(diag)
    c, d = [0.] * n, [0.] * n
    c[0] = up[0] / diag[0]
    d[0] = rhs[0] / diag[0]
    for i in range(1, n):
        m = diag[i] - low[i] * c[i - 1]
        c[i] = up[i] / m if i < n - 1 else 0.
        d[i] = (rhs[i] - low[i] * d[i - 1]) / m
    x = [0.] * n
    x[-1] = d[-1]
    for i in range(n - 2, -1, -1):
        x[i] = d[i] - c[i] * x[i + 1]
    return x

#почтроение кубического сплайна с естественными граничными условиями. Используем метод вторых производных
def build_cubic_spline(xn, yn):
    n = len(xn)
    h = xn[1] - xn[0]  # шаг (равноотстоящие)
    m = [0.0] * n #массив вторых производных
    if n > 2:
        N = n - 2 #число внутренних узлов
        low = [h] * N
        diag = [4 * h] * N
        up = [h] * N
        low[0] = up[-1] = 0.0 #граничные условия
        gamma = [6 / h * (yn[i + 2] - 2 * yn[i + 1] + yn[i]) for i in range(N)]
        m_inner = progonka(low, diag, up, gamma)
        for i in range(N):
            m[i + 1] = m_inner[i]
    segs = []
    for i in range(n - 1):
        yp = (yn[i + 1] - yn[i]) / h - m[i + 1] * h / 6 - m[i] * h / 3
        segs.append((xn[i], m[i], m[i + 1], yn[i], yp, h))
    return segs

#вычисление значения кубического сплайна в точке x
def spline_cubic(segs, x):
    for xi, mi, mip1, yi, yip, h in segs:
        if xi <= x <= xi + h:
            dx = x - xi
            return ((mip1 - mi) / (6 * h)) * dx ** 3 + (mi / 2) * dx ** 2 + yip * dx + yi
    # fallback
    xi, mi, mip1, yi, yip, h = segs[0] if x < segs[0][0] else segs[-1]
    dx = x - xi
    return ((mip1 - mi) / (6 * h)) * dx ** 3 + (mi / 2) * dx ** 2 + yip * dx + yi

def spline_cubic_vec(segs, t):
    return [spline_cubic(segs, x) for x in t]

#----Таблица 3----
n_spline = [4, 6, 8, 10, 15, 20, 30]
print("\nТаблица 3. Максимальные отклонения сплайнов")
print("-" * 70)
print(f"{'n':>4} | {'k':>5} | {'RS1 (линейный)':>18} | {'RS2 (квадратич.)':>18} | {'RS3 (кубический)':>18}")
print("-" * 70)

for n in n_spline:
    xn = equidistant_nodes(n, A, B)
    yn = [f(x) for x in xn]
    s1 = spline_linear_vec(xn, yn, t)
    rs1 = max_err(t, f_vals, s1)
    segs2 = build_quad_spline(xn, yn)
    s2 = spline_quad_vec(segs2, t)
    rs2 = max_err(t, f_vals, s2)
    segs3 = build_cubic_spline(xn, yn)
    s3 = spline_cubic_vec(segs3, t)
    rs3 = max_err(t, f_vals, s3)
    print(f"{n:4} | {M:5} | {rs1:18.10e} | {rs2:18.10e} | {rs3:18.10e}")
print("-" * 70)

#----График сплайнов при n=10----
n_demo = 10
xn_d = equidistant_nodes(n_demo, A, B)
yn_d = [f(x) for x in xn_d]
segs2_d = build_quad_spline(xn_d, yn_d)
segs3_d = build_cubic_spline(xn_d, yn_d)

plt.figure(figsize=(10, 5))
plt.plot(t, f_vals, 'k-', lw=2.5, label='f(x)')
plt.plot(t, spline_linear_vec(xn_d, yn_d, t), '#1f77b4', linestyle='--', lw=2.5, label='S₁,₀')
plt.plot(t, spline_quad_vec(segs2_d, t), '#ff7f0e', linestyle='-.', lw=2.5, label='S₂,₁')
plt.plot(t, spline_cubic_vec(segs3_d, t), '#2ca02c', linestyle=':', lw=3.5, label='S₃,₂')
plt.plot(xn_d, yn_d, 'ko', markersize=5, label='узлы')
plt.title(f'Сплайны при n={n_demo}')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

#----График абсолютной погрешности: кубический сплайн vs полином Лагранжа (n=20)----
n_err = 20
xn_e = equidistant_nodes(n_err, A, B)
yn_e = [f(x) for x in xn_e]
L_err = lagrange_vec(xn_e, yn_e, t)
segs3_err = build_cubic_spline(xn_e, yn_e)
S_err = spline_cubic_vec(segs3_err, t)

err_L = [abs(fv - lv) for fv, lv in zip(f_vals, L_err)]
err_S = [abs(fv - sv) for fv, sv in zip(f_vals, S_err)]

plt.figure(figsize=(10, 4))
plt.plot(t, err_S, 'g-', lw=2.5, label=f'|f - S₃,₂|, n={n_err}')
plt.plot(t, err_L, 'r--', lw=2.5, label=f'|f - Lₙ|, n={n_err}')
plt.title('Абсолютная погрешность: кубический сплайн vs полином Лагранжа')
plt.xlabel('x')
plt.ylabel('Ошибка')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

