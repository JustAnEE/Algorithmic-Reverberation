# -- Implementing the Algorithmic Reverb in the Notebook using FFT convolution to speed up results
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter


def clip_stomper(data, N, peak):

    no_clipped_data = data

    for n in range(0, N):

        # -- Important that abs is used. Audio files can have negative components.

        # -- First attempt at clipping reduction -- unlikely the best solution.
        if abs(data[n]) > peak:

            if data[n] < 0:

                no_clipped_data[n] = -peak

            if data[n] > 0:

                no_clipped_data[n] = peak

    return no_clipped_data


# -- Expects coefficients in ascending order
def schroeder_reverb_params(T, A, T_a1, T_a2, g_a):

    a_0 = 0.4

    # -- These coefficients are in ascending order wrt delays T
    T_1, T_2, T_3, T_4 = T[0], T[1], T[2], T[3]
    a_1, a_2, a_3, a_4 = A[0], A[1], A[2], A[3]

    M = np.amax(T)

    a = np.zeros(M+1, dtype=np.float32)
    b = np.zeros(M+1, dtype=np.float32)

    # -- These coefficients specify the 4 parallel comb filters and 2 series all pass filters all cascaded.
    b[0] = a_0 - g_a
    b[T_1] = a_1
    b[T_2] = a_2
    b[T_3] = a_3
    b[T_4] = a_4
    b[T_a1] = g_a
    b[T_a2] = g_a

    a[0] = 1
    a[T_a1] = -g_a
    a[T_a1] = -g_a

    return b, a


def schroeder_reverb(data, T, A, T_a1, T_a2, g_a):

    # -- Obtain filter parameters
    b, a = schroeder_reverb_params(T, A, T_a1, T_a2, g_a)

    # -- Apply filter to input data sequence
    reverbed_data = lfilter(b, a, data)
    reverbed_data = np.asarray(reverbed_data, dtype=np.float32)

    return reverbed_data


# -- Read input data/data length and convert to mono
fs, data = wavfile.read('githubsample.wav')
data = np.mean(data, axis=-1)
N = len(data)

# -- Find max volume in data
max_vol = np.amax(data)

# -- Define gain and delays for all pass filter component of schroeder filter
g_ap = 0.7
T_ap1 = 150
T_ap2 = 50

# -- Store an array of tuples of the form (T_i, a_i) where y(n) = a_0 x(n) + a_1 x(n-T_1) +...+
P = np.array([(200, 0.35), (800, 0.4), (1600, 0.4), (3200, 0.35)])

P = sorted(P, key=lambda tup: tup[0])  # Organize tuples by ascending order of phase shift with lambda magic

Q = np.array([P[0], P[1], P[2], P[3]])  # Make it a numpy array again

# -- Extract single arrays from multi-dimensional array to improve computational time and improve readability
T = np.array([Q[0][0], Q[1][0], Q[2][0], Q[3][0]], dtype=np.int32)
A = np.array([Q[0][1], Q[1][1], Q[2][1], Q[3][1]])

new_song = clip_stomper(schroeder_reverb(data, T, A, T_ap1, T_ap2, g_ap), N, max_vol)

# -- Optional: alpha is slowing factor. Pos -> speed up. Neg -> slow down. Ex: alpha = 0.15 means 15% slow.
alpha = 1
fs_slow = int(fs - alpha*fs)

wavfile.write("new_song.wav", fs_slow, new_song)
