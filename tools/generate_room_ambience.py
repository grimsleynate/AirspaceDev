"""Generate Quasar-owned placeholder ambience for room-effect prototypes."""

from array import array
import math
from pathlib import Path
import random
import wave


RATE = 16_000
DURATION = 12
OUTPUT = Path(__file__).resolve().parents[1] / "web" / "static" / "webclient" / "audio" / "ambience"


def _write(name, sampler):
    samples = array("h")
    for index in range(RATE * DURATION):
        t = index / RATE
        # A short equal-power edge fade removes sample-boundary clicks when
        # Howler loops these lightweight prototype beds.
        edge = min(1.0, t / 0.035, (DURATION - t) / 0.035)
        edge = math.sin(max(0.0, edge) * math.pi / 2) ** 2
        value = max(-1.0, min(1.0, sampler(t, index) * edge))
        samples.append(int(value * 32767))
    path = OUTPUT / name
    with wave.open(str(path), "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(RATE)
        target.writeframes(samples.tobytes())


def lamps():
    rng = random.Random(1138)
    dips = (0.92, 1.06, 3.38, 3.55, 8.91)

    def sample(t, _):
        envelope = 1.0
        for center in dips:
            envelope *= 1.0 - 0.82 * math.exp(-((t - center) / 0.025) ** 2)
        hum = math.sin(2 * math.pi * 60 * t) + 0.34 * math.sin(2 * math.pi * 120 * t)
        ballast = 0.07 * math.sin(2 * math.pi * 810 * t + 0.3 * math.sin(t * 3))
        return envelope * (0.12 * hum + ballast + rng.uniform(-0.008, 0.008))

    _write("wayhouse-lamps.wav", sample)


def wind():
    rng = random.Random(2718)
    state = 0.0

    def sample(t, _):
        nonlocal state
        state = state * 0.985 + rng.uniform(-1, 1) * 0.015
        gust = 0.35 + 0.28 * (1 + math.sin(2 * math.pi * t / 5.9)) / 2
        whistle = math.sin(2 * math.pi * (385 + 22 * math.sin(t * 0.7)) * t)
        whistle *= max(0, math.sin(2 * math.pi * t / 7.1)) ** 5
        return state * gust * 1.4 + whistle * 0.025

    _write("wayhouse-wind.wav", sample)


def insects():
    rng = random.Random(1618)
    starts = (0.8, 2.6, 2.82, 5.1, 7.4, 7.61, 10.25)

    def sample(t, _):
        value = rng.uniform(-0.002, 0.002)
        for start in starts:
            local = t - start
            if 0 <= local < 0.14:
                pulse = math.sin(math.pi * local / 0.14) ** 2
                tremolo = 0.35 + 0.65 * (math.sin(2 * math.pi * 38 * local) ** 2)
                frequency = 3_100 + 620 * (local / 0.14)
                value += 0.19 * pulse * tremolo * math.sin(2 * math.pi * frequency * local)
        return value

    _write("wayhouse-insects.wav", sample)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    lamps()
    wind()
    insects()
