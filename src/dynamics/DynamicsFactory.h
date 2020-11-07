#ifndef BTWSIM_SRC_DYNAMICS_DYNAMICSFACTORY_H_
#define BTWSIM_SRC_DYNAMICS_DYNAMICSFACTORY_H_

#include <memory>
#include "ModelDynamics.h"

class DynamicsFactory {
 public:
  static std::unique_ptr<ModelDynamics> BuildDynamics(
      ModelDynamics::dynamics dynamics);
};

#endif  // BTWSIM_SRC_DYNAMICS_DYNAMICSFACTORY_H_
