import sys

from transit_billing.cli import main as billing_main


def test_main_cli_end_to_end(tmp_zone_map_file, tmp_journey_file, tmp_path, monkeypatch, capsys):
    out_file = tmp_path / "bills_out.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        ["my_solution.py", tmp_zone_map_file, tmp_journey_file, str(out_file)],
    )

    billing_main()

    captured = capsys.readouterr()
    assert "[INFO] Billing results written to" in captured.out

    with open(out_file, newline="", encoding="utf-8") as f:
        data = f.read().strip().splitlines()

    if data and data[0].startswith("user_id"):
        data = data[1:]

    assert sorted(data) == sorted(
        [
            "userX,3.3",
            "userY,5.0",
        ]
    )
