#include <iostream>
#include <vector>
#include <chrono>
#include <fstream>
#include <utility>

using namespace std;
using namespace std::chrono;

vector<vector<int>> map;
int current_time = 0;
int SIZE;
long TOTAL_GRAINS = 0;
ofstream output;

void InitializeMap() {
  for (int i = 0; i < SIZE; i++) {
    vector<int> row;
    for (int j = 0; j < SIZE; j++) {
      int amount = rand() % 4;
      if (amount < 3) {
        if (rand() % 4 != 1)
          amount++;
      }
      TOTAL_GRAINS += amount;
      row.push_back(amount);
    }
    map.push_back(row);
  }
}

void PrintMap() {
  for (auto &i : map) {
    for (int j : i) {
      cout << j << " ";
    }
    cout << endl;
  }
  cout << endl;
}

void SaveData(int crits) {
  output << crits << "," << TOTAL_GRAINS << endl;
}

bool CheckCrits() {
  int grains_lost = 0;
  vector<pair<int, int>> crits_vec;
  for (int i = 0; i < SIZE; i++) {
    for (int j = 0; j < SIZE; j++) {
      if (map[i][j] >= 4) {
        crits_vec.emplace_back(i, j);
      }
    }
  }

  for (auto &p : crits_vec) {
    int i = p.first;
    int j = p.second;

    map[i][j] -= 4;
    if (i + 1 < SIZE)
      map[i + 1][j]++;
    else
      ++grains_lost;

    if (i - 1 >= 0)
      map[i - 1][j]++;
    else
      ++grains_lost;

    if (j + 1 < SIZE)
      map[i][j + 1]++;
    else
      ++grains_lost;

    if (j - 1 >= 0)
      map[i][j - 1]++;
    else
      ++grains_lost;
  }

  if (!crits_vec.empty())
    SaveData(crits_vec.size());
  TOTAL_GRAINS -= grains_lost;
  return !crits_vec.empty();
}

void Step() {
  current_time++;
  SaveData(0);
  int i = rand() % SIZE;
  int j = rand() % SIZE;
  map[i][j]++;
  TOTAL_GRAINS++;
  while (CheckCrits()) {
    current_time++;
    if (current_time % 10000 == 0) {
      cout << "Done " << current_time << endl;
    }
  }
}

int main() {
  output.open("output.txt");
  output << "critical_cells,total_grains" << endl;
  SIZE = 1000;
  int steps = 5000000;
  InitializeMap();

  auto start = high_resolution_clock::now();

  while (current_time < steps) {
    Step();
  }

  auto stop = high_resolution_clock::now();
  auto duration = duration_cast<microseconds>(stop - start);

  cout << "Time: " << duration.count() << " us" << endl;

  return 0;
}
