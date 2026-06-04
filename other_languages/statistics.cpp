#include <iostream>
#include <fstream>
#include <cmath>
#include <locale>
using namespace std;

int main() 
{ 
    setlocale(LC_ALL, "RUS"); 
    int i, n; 
    float SRxy = 0, Mx, My, smx = 0, smy = 0, *x, *y, sum1 = 0, sum2 = 0, a0, a1; 
    double r, Sx, Sy; 
    
    ifstream in("C:\\Users\\User\\Downloads\\dat.txt");
    ofstream out("C:\\Users\\User\\Downloads\\output.txt");
    
    if (in.is_open()) 
    { 
        // Считываем данные файла 
        in >> n; 
        x = new float[n]; 
        y = new float[n]; 
        
        for (i = 0; i < n; i++) 
            in >> x[i]; 
        for (i = 0; i < n; i++) 
            in >> y[i]; 
            
        // Вычисление выборочного мат. ожидания 
        for (i = 0; i < n; i++) { 
            smx += x[i]; 
            smy += y[i]; 
        } 
        Mx = smx / n; 
        My = smy / n;
        
        // Вычисление стандартного отклонения 
        for (i = 0; i < n; i++) { 
            sum1 += (x[i] - Mx) * (x[i] - Mx); 
            sum2 += (y[i] - My) * (y[i] - My); 
        } 
        Sx = sqrt(sum1 / n); 
        Sy = sqrt(sum2 / n); 
        
        // Вычисление коэффициента корреляции 
        for (i = 0; i < n; i++) 
            SRxy += (x[i] - Mx) * (y[i] - My); 
        r = SRxy / (n * Sx * Sy); 
        
        if (r < 0.5) { 
            cout << "Нелинейная зависимость"; 
            return 1; 
        } 
        else {
            a0 = My - Sy / Sx * r * Mx; // вычисление коэффициентов линии регрессии 
            a1 = Sy / Sx * r; 
        }
        
        // Записываем результаты в файл 
        out << "Mx=" << Mx << " My=" << My << " Sx=" << Sx << " Sy=" << Sy << " r=" << r << "\n\n";
        out << "x:\n";
        for (i = 0; i < n; i++) 
            out << "x:" << x[i] << "\t y:" << y[i] << "\t yr:" << a0 + a1 * x[i] << "\n"; 
        out << "y=" << a0 << "+" << a1 << "*x\n"; 
        
        // Выводим на экран 
        cout << "Mx=" << Mx << " My=" << My << " Sx=" << Sx << " Sy=" << Sy << " r=" << r << "\n"; 
        cout << "Рост\t Вес\t Расчётный вес\n"; 
        for (i = 0; i < n; i++) 
            cout << "x:" << x[i] << "\t y:" << y[i] << "\t yr:" << a0 + a1 * x[i] << "\n"; 
        cout << "y=" << a0 << "+" << a1 << "*x\n"; 
        
    } 
    else {
        cout << "Возникла ошибка при открытии файла\n"; 
    }
    
    cout << "Нажмите Enter для выхода...";
    cin.get();
    return 0; 
}




