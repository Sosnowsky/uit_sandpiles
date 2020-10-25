#include <boost/program_options.hpp>
#include <chrono>
#include <iostream>
#include <memory>
#include <string>
#include "BTWModel.h"

using namespace std;
using namespace std::chrono;
using namespace boost::program_options;

int main(int ac, char *av[]) {
  options_description desc("Allowed options");
  desc.add_options()("help,h", "print usage message")(
      "grid_size,L", value<int>()->default_value(1024), "the size of the grid")(
      "pre_steps,p", value<int>()->default_value(0),
      "number of steps run before writing output")(
      "steps,s", value<int>()->default_value(10000),
      "number of steps run writing output")(
      "output,o", value<string>()->default_value("output.txt"), "output file")(
      "stats", value<string>()->default_value("stats.txt"), "stats file");

  variables_map vm;
  store(parse_command_line(ac, av, desc), vm);

  if (vm.count("help")) {
    cout << desc << "\n";
    return 0;
  }

  int size = vm["grid_size"].as<int>();
  int pre_steps = vm["pre_steps"].as<int>();
  int steps = vm["steps"].as<int>();
  string output = vm["output"].as<string>();
  string stats = vm["stats"].as<string>();
  unique_ptr<BTWModel> model =
      std::make_unique<BTWModel>(BTWModel(output, stats, size));

  model->InitializeMap();
  auto start = high_resolution_clock::now();

  model->Run(pre_steps, steps);

  auto stop = high_resolution_clock::now();
  auto run_duration = duration_cast<microseconds>(stop - start);

  cout << "Total time: " << run_duration.count() << " us" << endl;

  return 0;
}
