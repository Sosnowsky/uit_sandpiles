#include "DynamicsFactory.h"
#include "BTWClassicalDynamics.h"
#include "BTWRandom2Dynamics.h"

std::unique_ptr<ModelDynamics> DynamicsFactory::BuildDynamics(
    ModelDynamics::dynamics dynamics) {
  switch (dynamics) {
    case ModelDynamics::classical:
      return std::unique_ptr<ModelDynamics>(new BTWClassicalDynamics());
    case ModelDynamics::random2:
      return std::unique_ptr<ModelDynamics>(new BTWRandom2Dynamics());
    default:
      throw std::invalid_argument("Unimplemented");
  }
}
