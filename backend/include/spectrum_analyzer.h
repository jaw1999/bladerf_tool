#ifndef SPECTRUM_ANALYZER_H
#define SPECTRUM_ANALYZER_H

#include <stdint.h>
#include <libbladeRF.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct SpectrumAnalyzer SpectrumAnalyzer;

SpectrumAnalyzer* sa_init(void);
void sa_close(SpectrumAnalyzer* sa);
int sa_set_frequency(SpectrumAnalyzer* sa, uint64_t freq);
int sa_set_sample_rate(SpectrumAnalyzer* sa, uint32_t rate);
int sa_set_bandwidth(SpectrumAnalyzer* sa, uint32_t bw);
int sa_set_gain(SpectrumAnalyzer* sa, int gain);
int sa_get_frequency(SpectrumAnalyzer* sa, uint64_t* freq);
int sa_get_sample_rate(SpectrumAnalyzer* sa, uint32_t* rate);
int sa_get_bandwidth(SpectrumAnalyzer* sa, uint32_t* bw);
int sa_get_gain(SpectrumAnalyzer* sa, int* gain);
int sa_get_fft(SpectrumAnalyzer* sa, float* fft_data, int fft_size);

#ifdef __cplusplus
}
#endif

#endif // SPECTRUM_ANALYZER_H