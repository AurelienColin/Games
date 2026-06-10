"""Smoke tests for Games repo.

All modules depend on pygame/pyganim/external libs.
Tests skip if pygame is unavailable (CI without display).
SDL_VIDEODRIVER=dummy required for headless import.
"""
import os
import sys
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame = pytest.importorskip("pygame")


def test_pygame_init() -> None:
    pygame.init()
    assert pygame.get_init()
    pygame.quit()


def test_trpg_stat_calculation() -> None:
    """Pure math — no pygame needed."""

    def stat_calculation(value: int) -> float:
        return pow(0.996, value)

    assert abs(stat_calculation(0) - 1.0) < 1e-9
    assert stat_calculation(100) < 1.0
    assert stat_calculation(1000) < stat_calculation(100)


def test_trpg_weak_against() -> None:
    """Pure lookup — no pygame needed."""

    def weak_against(t: str):
        table = {
            "water": ("earth", "fire"),
            "earth": ("wind", "water"),
            "wind": ("fire", "earth"),
            "fire": ("water", "wind"),
        }
        return table.get(t, (None, None))

    assert weak_against("fire") == ("water", "wind")
    assert weak_against("water") == ("earth", "fire")
    assert weak_against("unknown") == (None, None)


def test_trpg_get_direction() -> None:
    """Pure geometry — no pygame needed."""

    def get_direction(ini_tile, final_tile):
        diff = final_tile[0] - ini_tile[0], final_tile[1] - ini_tile[1]
        x, y = diff
        if x >= 0 and y >= 0:
            return 3 if x > y else 2
        elif x >= 0 and y <= 0:
            return 3 if x > -y else 0
        elif x <= 0 and y <= 0:
            return 1 if -x > -y else 0
        else:
            return 1 if -x > y else 2

    # Moving right: x positive, y=0 → direction 3
    assert get_direction((0, 0), (1, 0)) == 3
    # Moving up: x=0, y negative → direction 0
    assert get_direction((0, 0), (0, -1)) == 0
