#include <gtest/gtest.h>
#include "../src/ModelUtils.h"

class ModelUtilsTest : public ::testing::Test {
 protected:
  ModelUtilsTest() = default;
  ~ModelUtilsTest() override = default;
};

TEST_F(ModelUtilsTest, Random) {
  std::vector<int> count(10, 0);
  for (int i = 0; i < 100; i++) {
    int rnd = ModelUtils::GetRandomInt() % 10;
    count[rnd]++;
  }
  for (auto c : count) {
    // Can fail randomly
    ASSERT_FALSE(c == 0);
  }
}
