import numpy as np


def auto_correlate_pitch_period(audio_chunk: np.array, sample_rate, min_frequency=80, max_frequency=1000) -> int:
    chunk_normalized = audio_chunk - np.mean(audio_chunk)
    max_lag = int(sample_rate / min_frequency)
    min_lag = int(sample_rate / max_frequency)

    corr = np.correlate(chunk_normalized, chunk_normalized, mode='full')
    corr_half = corr[corr.size // 2:]

    if min_lag >= max_lag or len(corr_half[min_lag:max_lag]) == 0:
        return 0

    return np.argmax(corr_half[min_lag:max_lag]) + min_lag


def auto_correlate_pitch_marks(
        audio_chunk: np.array, frame_length, sample_rate, min_frequency=80, max_frequency=1000
) -> np.array:
    pitch_marks = []
    index = 0
    while index < len(audio_chunk):
        frame_end = min(index + frame_length, len(audio_chunk))
        frame = audio_chunk[index:frame_end]

        period = auto_correlate_pitch_period(frame, sample_rate, min_frequency, max_frequency)
        if period:
            pitch_marks.append(index)
            index += period  # Move to the next period
        else:
            index += 1  # Move only one sample forward in case of no detection

    return np.array(pitch_marks, dtype=int)
