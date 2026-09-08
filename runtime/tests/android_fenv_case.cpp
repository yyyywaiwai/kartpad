#include "android_fenv_case.h"
#include <kartpad/semantics/ppc_semantics.h>
extern "C" AndroidFpCaseResult TEST_ENTRY(unsigned op, std::uint32_t fpscr, double a, double b, double c) {
  using namespace kartpad::semantics;
  ScalarFpResult result;
  switch (op) {
#define BINARY(index, kind, single) case index: result = EvaluatePpcScalarBinary(fpscr, ScalarFpBinaryOperation::kind, a, b, single); break
  BINARY(0, Add, false); BINARY(1, Subtract, false);
  BINARY(2, Multiply, false); BINARY(3, Divide, false);
  BINARY(4, Add, true); BINARY(5, Subtract, true);
  BINARY(6, Multiply, true); BINARY(7, Divide, true);
#undef BINARY
  case 8: result = EvaluatePpcSqrt(fpscr, a, false); break;
  case 9: result = EvaluatePpcSqrt(fpscr, a, true); break;
  case 10: result = EvaluatePpcFused(fpscr, a, c, b, false, true, false); break;
  case 11: result = EvaluatePpcFused(fpscr, a, c, b, true, true, true); break;
  default: result = EvaluatePpcFused(fpscr, a, c, b, true, false, true); break;
  }
  return {std::bit_cast<std::uint64_t>(result.value), result.fpscr,
          result.exception, result.write_destination, std::fetestexcept(FE_ALL_EXCEPT)};
}
