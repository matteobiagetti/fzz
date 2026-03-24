#ifndef _PYFZZ_H_
#define _PYFZZ_H_

#include "../fzz.h"

namespace FZZ {

class PyFastZigzag : public FastZigzag {
public:
    std::vector<std::tuple<Integer, Integer, Integer>> compute_zigzag(
        const std::vector<std::tuple<char, std::vector<int>>>& filt_simp);
};

} // namespace FZZ

#endif // _PYFZZ_H_