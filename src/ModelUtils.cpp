#include "ModelUtils.h"
#include <algorithm>

double ModelUtils::GetRandomDouble() { return float(rand() % 10000) / 10000; }

int ModelUtils::GetRandomInt() { return rand(); }
