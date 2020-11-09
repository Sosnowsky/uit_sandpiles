#include "DynamicsFactory.h"
#include "BTWClassicalDynamics.h"
#include "BTWDeterministicNNN.h"
#include "BTWRandom2Dynamics.h"

std::unique_ptr<ModelDynamics> DynamicsFactory::BuildDynamics(
    ModelDynamics::dynamics dynamics) {
  switch (dynamics) {
    case ModelDynamics::classical:
      return std::unique_ptr<ModelDynamics>(new BTWClassicalDynamics());
    case ModelDynamics::random2:
      return std::unique_ptr<ModelDynamics>(new BTWRandom2Dynamics());
    case ModelDynamics::nnn:
      return std::unique_ptr<ModelDynamics>(new BTWDeterministicNNN());
    default:
      throw std::invalid_argument("Unimplemented");
  }
}
