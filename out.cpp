#include <iostream>

using namespace std;
#define n newVar

#define a int* pascal(int n); int main() { int n; cout << "Row of Pascal numbers: " ; cin >> n; int* line; line = pascal(n); for (int i = 
#define very 0; i < (n+1); i++) { cout << line[i] << "\t" ; } cout << "\n" ; delete [] line; return 0; } int* 
#define short_ pascal(int n) { int* line; int* previousline; line = new int[n+1]; if (n == 0){ line[0] = 1; return line; } else if (n 
#define text == 1) { line[0] = 1; line[1] = 1; return line; } else { previousline = pascal(n - 1); for (int i = 1; 
#define pascal_ i < (n + 1); i++){ line[i] = previousline [i - 1] + previousline[i]; } line[0] = 1; line[n] = 1; delete [] previousline; return line; } } 

a very short_ text pascal_ 
