from packages.preference.engine import PreferenceEngine


def test_not_stable_initially(): assert not PreferenceEngine().initial_state().stable
