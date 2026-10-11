// Compiled twice: once against the baseline header, once against the candidate.
#include <cstdint>
#include VARIANT_HEADER
namespace ks = kartpad::semantics;
extern "C" void VARIANT_FN(int op, std::uint32_t fpscr, double a, double b, double c, bool single,
                           double* value, std::uint32_t* out_fpscr, std::uint32_t* exception, bool* write) {
  ks::ScalarFpResult r;
  switch (op) {
  case 0: r = ks::EvaluatePpcScalarBinary(fpscr, ks::ScalarFpBinaryOperation::Add, a, b, single); break;
  case 1: r = ks::EvaluatePpcScalarBinary(fpscr, ks::ScalarFpBinaryOperation::Subtract, a, b, single); break;
  case 2: r = ks::EvaluatePpcScalarBinary(fpscr, ks::ScalarFpBinaryOperation::Multiply, a, b, single); break;
  case 3: r = ks::EvaluatePpcScalarBinary(fpscr, ks::ScalarFpBinaryOperation::Divide, a, b, single); break;
  case 4: r = ks::EvaluatePpcSqrt(fpscr, a, single); break;
  case 5: r = ks::EvaluatePpcFused(fpscr, a, c, b, false, single, false); break;
  default: r = ks::EvaluatePpcFused(fpscr, a, c, b, true, single, true); break;
  }
  *value = r.value; *out_fpscr = r.fpscr; *exception = r.exception; *write = r.write_destination;
}
