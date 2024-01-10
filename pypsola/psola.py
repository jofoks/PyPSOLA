from functools import partial

import numpy as np

from pypsola import auto_correlate_pitch_period, correlate_pitch_marks


def prep_marks(pitch_marks, chunk_size):
    periods = np.diff(pitch_marks)

    if pitch_marks[0] <= periods[0]:
        pitch_marks = pitch_marks[1:]
        periods = periods[1:]

    if pitch_marks[-1] + periods[-1] > chunk_size:
        pitch_marks = pitch_marks[:-1]
    else:
        periods = np.append(periods, periods[-1])
    return pitch_marks, periods


def get_output_slice(index: float, frame_length: int, output: np.array):
    out_start = round(index) - round(frame_length / 2)
    out_end = out_start + frame_length
    out_start = max(out_start, 0)
    output_segment_length = min(out_end, len(output)) - out_start

    # Fix rounding artifacts
    if output_segment_length == frame_length + 1:
        out_end -= 1
    elif output_segment_length == frame_length - 1:
        out_end += 1
    return slice(out_start, out_end)


def psola_pitch_shift(audio_chunk: np.array, pitch_marks: np.array, pitch_shift: float):
    pitch_marks, periods = prep_marks(pitch_marks, len(audio_chunk))
    output = np.zeros(int(np.ceil(len(audio_chunk))))

    current_mark = periods[0] + 1
    while round(current_mark) < len(output):
        pitch_index = np.argmin(np.abs(pitch_marks - current_mark))
        pitch_mark, period = pitch_marks[pitch_index], periods[pitch_index]

        frame_start = max(pitch_mark - period, 0)
        frame_end = min(pitch_mark + period, len(audio_chunk))
        frame = audio_chunk[frame_start:frame_end]

        # Trim first frame to fit if too large
        if (pitch_mark - len(frame) // 2) < 0:
            frame = frame[:(pitch_mark - round(len(frame) / 2)) + len(frame)]

        frame *= np.hanning(len(frame))

        output_slice = get_output_slice(current_mark, len(frame), output)
        if output_slice.stop > len(output):
            break

        output[output_slice] += frame
        current_mark += period / pitch_shift

    return output


def shift_pitch(audio_chunk: np.array,
                shift_factor: float,
                min_frequency: int = 80,
                max_frequency: int = 1000,
                frame_length: int = 512,
                sample_rate: int = 44100,
                threshold: float = 0.001):
    if np.sum(np.abs(audio_chunk)) < threshold * len(audio_chunk):
        return audio_chunk

    pitch_detector = partial(auto_correlate_pitch_period,
                             sample_rate=sample_rate,
                             min_frequency=min_frequency,
                             max_frequency=max_frequency)
    pitch_marks = correlate_pitch_marks(audio_chunk, frame_length, pitch_detector)
    return psola_pitch_shift(audio_chunk, pitch_marks, shift_factor)
