#include "pyfzz.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>

namespace py = pybind11;

namespace FZZ {

std::vector<std::tuple<Integer, Integer, Integer>> PyFastZigzag::compute_zigzag(
    const std::vector<std::tuple<char, std::vector<int>>>& filt_simp) {

    std::vector<Simplex> filt_simp_lin;
    std::vector<bool> filt_op;
    filt_simp_lin.reserve(filt_simp.size());
    filt_op.reserve(filt_simp.size());

    for (std::size_t i = 0; i < filt_simp.size(); ++i) {
        char op = std::get<0>(filt_simp[i]);
        const auto& simp = std::get<1>(filt_simp[i]);

        if (op == 'i') {
            filt_op.push_back(true);
        } else if (op == 'd') {
            filt_op.push_back(false);
        } else {
            throw std::invalid_argument(
                std::string("Invalid operation '") + op +
                "' at index " + std::to_string(i) +
                ". Must be 'i' (insert) or 'd' (delete).");
        }

        filt_simp_lin.emplace_back(simp.begin(), simp.end());
    }

    std::vector<std::tuple<Integer, Integer, Integer>> persistence;
    FastZigzag fzz;
    fzz.compute(filt_simp_lin, filt_op, &persistence);
    return persistence;
}

} // namespace FZZ

PYBIND11_MODULE(_fzz_core, m) {
    m.doc() = "Fast zigzag persistence computation (C++ core)";
    py::class_<FZZ::PyFastZigzag>(m, "FastZigzag")
        .def(py::init<>())
        .def("compute_zigzag", &FZZ::PyFastZigzag::compute_zigzag,
             py::arg("filtration"),
             "Compute zigzag persistence barcode.\n\n"
             "Args:\n"
             "    filtration: List of (op, simplex) tuples where op is 'i' or 'd'\n"
             "                and simplex is a list of vertex indices (sorted ascending).\n\n"
             "Returns:\n"
             "    List of (birth, death, dimension) tuples.");
}


