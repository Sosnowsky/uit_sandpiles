#ifndef BTWSIM_SRC_MODELUTILS_H_
#define BTWSIM_SRC_MODELUTILS_H_

#endif  // BTWSIM_SRC_MODELUTILS_H_

class ModelUtils {
 public:
  /**
   * Used to get realizations of uniformly distributed random variables. Return
   * value is in [0, 1)
   */
  static double GetRandomDouble();

  /**
   * Used to get random point in a grid. Return value is in [0, maxint].
   */
  static int GetRandomInt();
};