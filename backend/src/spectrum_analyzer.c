#include "spectrum_analyzer.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <fftw3.h>

struct SpectrumAnalyzer {
    struct bladerf *dev;
    fftwf_plan fft_plan;
    fftwf_complex *fft_in;
    fftwf_complex *fft_out;
    int fft_size;
    uint64_t center_freq;
    uint32_t sample_rate;
    uint32_t bandwidth;
    int gain;
};

SpectrumAnalyzer* sa_init(void) {
    SpectrumAnalyzer* sa = malloc(sizeof(SpectrumAnalyzer));
    if (!sa) return NULL;

    int status;

    status = bladerf_open(&sa->dev, NULL);
    if (status != 0) {
        fprintf(stderr, "Unable to open device: %s\n", bladerf_strerror(status));
        free(sa);
        return NULL;
    }

    sa->fft_size = 1024;  // Default FFT size
    sa->fft_in = fftwf_alloc_complex(sa->fft_size);
    sa->fft_out = fftwf_alloc_complex(sa->fft_size);
    sa->fft_plan = fftwf_plan_dft_1d(sa->fft_size, sa->fft_in, sa->fft_out, FFTW_FORWARD, FFTW_MEASURE);

    sa->center_freq = 915000000;  // Default to 915 MHz
    sa->sample_rate = 10000000;   // 10 MHz sample rate
    sa->bandwidth = 10000000;     // 10 MHz bandwidth
    sa->gain = 30;                // 30 dB gain

    status = bladerf_set_frequency(sa->dev, BLADERF_CHANNEL_RX(0), sa->center_freq);
    if (status != 0) {
        fprintf(stderr, "Failed to set frequency: %s\n", bladerf_strerror(status));
        sa_close(sa);
        return NULL;
    }

    status = bladerf_set_sample_rate(sa->dev, BLADERF_CHANNEL_RX(0), sa->sample_rate, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set sample rate: %s\n", bladerf_strerror(status));
        sa_close(sa);
        return NULL;
    }

    status = bladerf_set_bandwidth(sa->dev, BLADERF_CHANNEL_RX(0), sa->bandwidth, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set bandwidth: %s\n", bladerf_strerror(status));
        sa_close(sa);
        return NULL;
    }

    status = bladerf_set_gain(sa->dev, BLADERF_CHANNEL_RX(0), sa->gain);
    if (status != 0) {
        fprintf(stderr, "Failed to set gain: %s\n", bladerf_strerror(status));
        sa_close(sa);
        return NULL;
    }

    status = bladerf_sync_config(sa->dev, BLADERF_RX_X1, BLADERF_FORMAT_SC16_Q11, 
                                 64, 16384, 16, 10000);
    if (status != 0) {
        fprintf(stderr, "Failed to configure sync interface: %s\n", bladerf_strerror(status));
        sa_close(sa);
        return NULL;
    }

    status = bladerf_enable_module(sa->dev, BLADERF_CHANNEL_RX(0), true);
    if (status != 0) {
        fprintf(stderr, "Failed to enable RX channel: %s\n", bladerf_strerror(status));
        sa_close(sa);
        return NULL;
    }

    return sa;
}

void sa_close(SpectrumAnalyzer* sa) {
    if (!sa) return;
    bladerf_enable_module(sa->dev, BLADERF_CHANNEL_RX(0), false);
    bladerf_close(sa->dev);
    fftwf_destroy_plan(sa->fft_plan);
    fftwf_free(sa->fft_in);
    fftwf_free(sa->fft_out);
    free(sa);
}

int sa_set_frequency(SpectrumAnalyzer* sa, uint64_t freq) {
    int status = bladerf_set_frequency(sa->dev, BLADERF_CHANNEL_RX(0), freq);
    if (status == 0) sa->center_freq = freq;
    return status;
}

int sa_set_sample_rate(SpectrumAnalyzer* sa, uint32_t rate) {
    int status = bladerf_set_sample_rate(sa->dev, BLADERF_CHANNEL_RX(0), rate, NULL);
    if (status == 0) sa->sample_rate = rate;
    return status;
}

int sa_set_bandwidth(SpectrumAnalyzer* sa, uint32_t bw) {
    int status = bladerf_set_bandwidth(sa->dev, BLADERF_CHANNEL_RX(0), bw, NULL);
    if (status == 0) sa->bandwidth = bw;
    return status;
}

int sa_set_gain(SpectrumAnalyzer* sa, int gain) {
    int status = bladerf_set_gain(sa->dev, BLADERF_CHANNEL_RX(0), gain);
    if (status == 0) sa->gain = gain;
    return status;
}

int sa_get_frequency(SpectrumAnalyzer* sa, uint64_t* freq) {
    *freq = sa->center_freq;
    return 0;
}

int sa_get_sample_rate(SpectrumAnalyzer* sa, uint32_t* rate) {
    *rate = sa->sample_rate;
    return 0;
}

int sa_get_bandwidth(SpectrumAnalyzer* sa, uint32_t* bw) {
    *bw = sa->bandwidth;
    return 0;
}

int sa_get_gain(SpectrumAnalyzer* sa, int* gain) {
    *gain = sa->gain;
    return 0;
}

int sa_get_fft(SpectrumAnalyzer* sa, float* fft_data, int fft_size) {
    if (fft_size != sa->fft_size) {
        fftwf_destroy_plan(sa->fft_plan);
        fftwf_free(sa->fft_in);
        fftwf_free(sa->fft_out);
        
        sa->fft_size = fft_size;
        sa->fft_in = fftwf_alloc_complex(sa->fft_size);
        sa->fft_out = fftwf_alloc_complex(sa->fft_size);
        sa->fft_plan = fftwf_plan_dft_1d(sa->fft_size, sa->fft_in, sa->fft_out, FFTW_FORWARD, FFTW_MEASURE);
    }

    int16_t *samples = malloc(2 * sa->fft_size * sizeof(int16_t));
    if (!samples) return -1;

    if (bladerf_sync_rx(sa->dev, samples, sa->fft_size, NULL, 5000) != 0) {
        free(samples);
        return -1;
    }

    for (int i = 0; i < sa->fft_size; i++) {
        sa->fft_in[i][0] = samples[2*i] / 2048.0f;
        sa->fft_in[i][1] = samples[2*i+1] / 2048.0f;
    }

    free(samples);

    fftwf_execute(sa->fft_plan);

    for (int i = 0; i < sa->fft_size; i++) {
        int j = (i + sa->fft_size/2) % sa->fft_size;
        float mag = sa->fft_out[j][0] * sa->fft_out[j][0] + sa->fft_out[j][1] * sa->fft_out[j][1];
        fft_data[i] = 10 * log10f(mag + 1e-20);
    }

    return 0;
}