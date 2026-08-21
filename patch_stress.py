import re

with open("apps/api/tests/test_stress_adversarial.py", "r") as f:
    content = f.read()

# Replace class TestPriceAudit: with a setup that monkeypatches the env
replacement = """import pytest

class TestPriceAudit:
    @pytest.fixture(autouse=True)
    def setup_static_price_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app.config import get_settings
        monkeypatch.setenv("PRICE_SOURCE_MODE", "static")
        get_settings.cache_clear()
"""

content = re.sub(r"class TestPriceAudit:", replacement, content)

with open("apps/api/tests/test_stress_adversarial.py", "w") as f:
    f.write(content)
