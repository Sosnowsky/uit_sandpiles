#include <iostream>
#include <vector>
#include <deque>
#include <chrono>
#include <string>
#include <fstream>
#include <utility>
//#include <boost/program_options.hpp>

using namespace std;
using namespace std::chrono;
//using namespace boost::program_options;

vector<vector<int>> grid;
const int SIZE = 50;
const int STEPS = 10 * 1000 * 1000;
const int PRE_STEPS = 1 * 1000 * 1000;
long TOTAL_GRAINS = 0;
ofstream output;
ofstream stats;

int treshold = 63;
long durations = 0;
long area = 0;
long quiet = 0;

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
    grid.push_back(row);
  }
}

void CheckStatsAndWriteIfNecessary(long crits) {
  if (crits > treshold) {
    if (quiet != 0) {
      stats << durations << "," << area << "," << quiet << endl;
      quiet = 0;
      durations = 0;
      area = 0;
    }
    durations++;
    area += crits;
  } else {
    quiet++;
  }
}

void PrintMap() {
  for (auto &i : grid) {
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
        if (++grid[a][b] == 4) {
          crits.emplace_back(a, b);
        }
      } else
        ++grains_lost;
    };

    // Increment and store for all neighbors
    grid[i][j] -= 4;
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
  grid[i][j]++;
  TOTAL_GRAINS++;
  return {i, j};
}

int main(int ac, char *av[]) {
  /**
  options_description desc("Allowed options");
  desc.add_options()
      ("help,h", "print usage message")
      ("grid_size,L", value<int>()->default_value(1024), "the size of the  grid")
      ("pre_steps,p", value<int>()->default_value(0), "number of steps run before writing output")
      ("steps,p", value<int>()->default_value(10000), "number of steps run writing output")
      ("output,o", value<string>()->default_value("output.txt"), "output file")
      ("stats,s", value<string>()->default_value("stats.txt"), "stats file");

  variables_map vm;
  store(parse_command_line(ac, av, desc), vm);

  if (vm.count("help")) {
    cout << desc << "\n";
    return 0;
  }
   */

  output.open("output.txt");
  stats.open("stats.txt");
  output << "critical_cells,total_grains" << endl;
  stats << "duration,area,quiet" << endl;
  InitializeMap();

  auto start = high_resolution_clock::now();

  // Used to output data only when we arrived to critical state, we consider that we arrived to critical state
  // if the average number of grains is over 2.11 per cell (not a very good identification, but good enough to reduce
  // the length of the time series).
  bool arrived_at_soc = true;

  deque<pair<int, int>> crits;

  for (int t = 0; t < STEPS + PRE_STEPS; t++) {
    if (!arrived_at_soc and float(TOTAL_GRAINS) / (SIZE * SIZE) > 2.14) {
      cout << "ARRIVED AT SOC!!!!" << endl;
      arrived_at_soc = true;
    }
    if (t % 100000 == 0) cout << "Done " << t << endl;

    if (crits.empty()) {
      pair<int, int> pos_added = AddGrain();
      if (grid[pos_added.first][pos_added.second] >= 4)
        crits.emplace_back(pos_added.first, pos_added.second);
    } else
      crits = Step(crits);

    if (arrived_at_soc and t > PRE_STEPS) {
      SaveData(crits.size());
      CheckStatsAndWriteIfNecessary(crits.size());
    }
  }

  auto stop = high_resolution_clock::now();
  auto run_duration = duration_cast<microseconds>(stop - start);

  cout << "Total time: " << run_duration.count() << " us" << endl;

  return 0;
}
