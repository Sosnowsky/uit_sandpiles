#include "BTW3dModel.h"
#include "BTWModel.h"
#include "ForestFireModel.h"
#include "dynamics/DynamicsFactory.h"
#include <boost/program_options.hpp>
#include <chrono>
#include <iostream>
#include <memory>
#include <string>

using namespace std;
using namespace std::chrono;
using namespace boost::program_options;

int main(int ac, char *av[]) {
  options_description desc("Allowed options");
  desc.add_options()("help,h", "print usage message")(
      "grid_size,L", value<int>()->default_value(1024),
      "the side length of the grid")(
      "model,M", value<string>()->default_value("btw"),
      "Model to run, possible values btw, ff, btw3d")(
      "pre_steps,p", value<int>()->default_value(1),
      "number of steps run before writing output. Used in btw and btw3d "
      "models. For btw, any value > 0 will let the model run until it detects "
      "criticality")(
      "param1,A", value<int>()->default_value(0),
      "Used in the forest fire model to specify grow_trees_per_time_step. In "
      "the btw model, it specifies the mode of the model (0 -> classical, 1 -> "
      "random_2, 2 -> nnn)")(
      "steps,s", value<int>()->default_value(10000),
      "number of steps run writing output. Used in all models")(
      "frequency,f", value<double>()->default_value(-1),
      "frequency of added grains from running model. Used in all models.")(
      "output,o", value<string>()->default_value("output.txt"),
      "output file for main timeseries. Used in all models")(
      "stats", value<string>()->default_value("stats.txt"),
      "stats file. Not used.");

  variables_map vm;
  store(parse_command_line(ac, av, desc), vm);

  if (vm.count("help")) {
    cout << desc << "\n";
    return 0;
  }

  string model_to_run = vm["model"].as<string>();
  int size = vm["grid_size"].as<int>();
  int pre_steps = vm["pre_steps"].as<int>();
  int steps = vm["steps"].as<int>();
  int param1 = vm["param1"].as<int>();
  double frequency_grains = vm["frequency"].as<double>();
  string output = vm["output"].as<string>();
  string stats = vm["stats"].as<string>();

  if (model_to_run == "btw") {
    unique_ptr<BTWModel> model = std::make_unique<BTWModel>(BTWModel(
        output, stats, size,
        DynamicsFactory::BuildDynamics(ModelDynamics::dynamics(param1))));

    model->InitializeMap();
    auto start = high_resolution_clock::now();

    model->Run(pre_steps > 0, steps, frequency_grains);

    auto stop = high_resolution_clock::now();
    auto run_duration = duration_cast<microseconds>(stop - start);

    cout << "Total time: " << run_duration.count() << " us" << endl;
  }
  if (model_to_run == "ff") {
    unique_ptr<ForestFireModel> model =
        std::make_unique<ForestFireModel>(ForestFireModel(output, size));
    model->InitializeMap();

    model->Run(steps, frequency_grains, param1);
  }
  if (model_to_run == "btw3d") {
    unique_ptr<BTW3dModel> model =
        std::make_unique<BTW3dModel>(BTW3dModel(output, size));

    model->InitializeMap();
    auto start = high_resolution_clock::now();

    model->Run(pre_steps, steps, frequency_grains);

    auto stop = high_resolution_clock::now();
    auto run_duration = duration_cast<microseconds>(stop - start);

    cout << "Total time: " << run_duration.count() << " us" << endl;
  }

  return 0;
}
