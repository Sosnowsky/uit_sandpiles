#include <iostream>
#include <vector>
#include <deque>
#include <chrono>
#include <fstream>
#include <utility>

using namespace std;
using namespace std::chrono;

vector<vector<int>> map;
const int SIZE = 2048;
const int STEPS = 2 * 1000 * 1000;
const int PRE_STEPS = 100 * 1000 * 1000;
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

deque<pair<int, int>> Step(deque<pair<int, int>> old_crits) {
  int grains_lost = 0;
  deque<pair<int, int>> crits; // Stores the positions of unstable guys

  for (auto &p : old_crits) {
    int i = p.first;
    int j = p.second;

    auto propagate = [&](int a, int b) {
      if (a >= 0 and a < SIZE and b >= 0 and b < SIZE) {
        if (++map[a][b] == 4) {
          crits.emplace_back(a, b);
        }
      } else
        ++grains_lost;
    };

    // Increment and store for all neighbors
    map[i][j] -= 4;
    propagate(i + 1, j);
    propagate(i - 1, j);
    propagate(i, j + 1);
    propagate(i, j - 1);
  }

  TOTAL_GRAINS -= grains_lost;
  return crits;
}

pair<int, int> AddGrain() {
  int i = rand() % SIZE;
  int j = rand() % SIZE;
  map[i][j]++;
  TOTAL_GRAINS++;
  return {i, j};
}

int main() {
  output.open("output.txt");
  output << "critical_cells,total_grains" << endl;
  InitializeMap();

  auto start = high_resolution_clock::now();

  // Used to output data only when we arrived to critical state, we consider that we arrived to critical state
  // if the average number of grains is over 2.11 per cell (not a very good identification, but good enough to reduce
  // the length of the time series).
  bool arrived_at_soc = false;

  deque<pair<int, int>> crits;
  for (int t = 0; t < STEPS + PRE_STEPS; t++) {
    if (!arrived_at_soc and float(TOTAL_GRAINS) / (SIZE * SIZE) > 2.14) {
      cout << "ARRIVED AT SOC!!!!" << endl;
      arrived_at_soc = true;
    }
    if (t % 100000 == 0) cout << "Done " << t << endl;
    if (arrived_at_soc and t > PRE_STEPS) SaveData(crits.size());

    if (crits.empty()) {
      pair<int, int> pos_added = AddGrain();
      if (map[pos_added.first][pos_added.second] >= 4)
        crits.emplace_back(pos_added.first, pos_added.second);
    } else
      crits = Step(crits);
  }

  auto stop = high_resolution_clock::now();
  auto duration = duration_cast<microseconds>(stop - start);

  cout << "Time: " << duration.count() << " us" << endl;

  return 0;
}
