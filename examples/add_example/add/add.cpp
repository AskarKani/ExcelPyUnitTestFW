
#include <iostream>
#include <cmath>

#include "add.hpp"

float add(float a, float b)
{
    float value = (int)((a+b) * 10 + .5);
    value = value / 10;
    return(value);
}
