from __future__ import annotations


def threshold_rule_id(kind: str) -> str:
    return f"{kind}_comment_coverage_below_threshold"


KIND_LABELS: dict[str, tuple[str, str]] = {
    "all": ("All public API", "all public API documentation"),
    "class": ("Classes", "class documentation"),
    "signal": ("Signals", "signal documentation"),
    "exported_property": ("Exported properties", "exported property documentation"),
    "public_func": ("Public functions", "public function documentation"),
    "constant": ("Constants", "constant documentation"),
}


def explain_threshold(kind: str) -> dict[str, str]:
    title_label, explanation_label = KIND_LABELS.get(
        kind,
        (kind.replace("_", " ").title(), f"{kind.replace('_', ' ')} comments"),
    )
    return {
        "title": f"{title_label} coverage below threshold",
        "explanation": (
            f"The configured minimum for {explanation_label} was not met, so public API documentation may drift."
        ),
    }


def catalog_for(kinds: set[str]) -> dict[str, dict[str, str]]:
    return {threshold_rule_id(kind): explain_threshold(kind) for kind in sorted(kinds)}
