import csv
import sys
import tempfile
import pytest
from datetime import datetime
from my_solution import (
    User,
    JourneyEvent,
    Constants,
    BillingSystem,
    main as billing_main
)

# ──────────────────────────────────────────────────────────────────────
# 1. 单元测试（Unit Tests）：核心算法与方法
# ──────────────────────────────────────────────────────────────────────

def test_zone_cost_valid():
    # 各分区增量费用
    assert User.zone_cost(1) == pytest.approx(0.80)
    assert User.zone_cost(2) == pytest.approx(0.50)
    assert User.zone_cost(5) == pytest.approx(0.30)
    assert User.zone_cost(999) == pytest.approx(0.10)

def test_zone_cost_errors():
    with pytest.raises(TypeError):
        User.zone_cost("not_int")
    with pytest.raises(ValueError):
        User.zone_cost(0)
    with pytest.raises(ValueError):
        User.zone_cost(-3)

@pytest.fixture
def simple_zone_map():
    return {"A":1, "B":2, "C":3, "D":4, "E":5, "F":6}

def mk_event(station, direction, time_str):
    return JourneyEvent(station, direction, datetime.fromisoformat(time_str))

def test_calculate_user_bill_round_trip(simple_zone_map):
    user = User("u1")
    user.add_event(mk_event("A","IN","2025-06-06T08:00:00"))
    user.add_event(mk_event("B","OUT","2025-06-06T08:30:00"))
    total = user.calculate_user_bill(
        station_zone_map=simple_zone_map,
        base_fee=Constants.BASE_FEE,
        penalty_fee=Constants.PENALTY_FEE,
        day_cap=Constants.DAY_CAP,
        month_cap=Constants.MONTH_CAP
    )
    # 2.00 + 0.80 + 0.50 = 3.30
    assert total == pytest.approx(3.30)

def test_calculate_user_bill_penalty(simple_zone_map):
    user = User("u2")
    user.add_event(mk_event("B","OUT","2025-06-06T09:00:00"))
    user.add_event(mk_event("C","IN","2025-06-06T09:30:00"))
    total = user.calculate_user_bill(
        station_zone_map=simple_zone_map,
        base_fee=Constants.BASE_FEE,
        penalty_fee=Constants.PENALTY_FEE,
        day_cap=Constants.DAY_CAP,
        month_cap=Constants.MONTH_CAP
    )
    # 两次罚款：5.00 + 5.00
    assert total == pytest.approx(10.00)

# ──────────────────────────────────────────────────────────────────────
# 2. 集成测试（Integration Tests）：模块间协作 + I/O
# ──────────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_zone_map_file(tmp_path):
    path = tmp_path / "zone_map.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["station","zone"])
        writer.writerows([["A","1"],["B","2"],["C","3"]])
    return str(path)

@pytest.fixture
def tmp_journey_file(tmp_path):
    path = tmp_path / "journey_data.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id","station","direction","time"])
        writer.writerows([
            ["userX","A","IN","2025-06-22T17:30:00"],
            ["userX","B","OUT","2025-06-22T17:40:00"],
            ["userY","A","OUT","2025-06-22T17:40:00"]
        ])
    return str(path)

def test_billing_system_load_and_generate(tmp_zone_map_file, tmp_journey_file):
    bs = BillingSystem(tmp_zone_map_file, tmp_journey_file)
    # 加载 CSV
    bs.load_zone_map()
    assert bs.station_zone_map == {"A":1,"B":2,"C":3}

    bs.load_journey_events()
    assert set(bs.users.keys()) == {"userX","userY"}
    assert len(bs.users["userX"].events) == 2
    # 生成账单
    bills = bs.generate_bills(
        Constants.BASE_FEE,
        Constants.PENALTY_FEE,
        Constants.DAY_CAP,
        Constants.MONTH_CAP
    )
    assert bills == {"userX": pytest.approx(3.30), "userY": pytest.approx(5.00)}

def test_billing_system_write(tmp_path):
    bills = {"uA":3.3, "uB":5.0}
    out = tmp_path / "out.csv"
    BillingSystem.write_bills_to_csv(bills, str(out))
    # 验证输出文件
    with open(out, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    mapping = {r["user_id"]: float(r["total_bill"]) for r in rows}
    assert mapping == {"uA": pytest.approx(3.30), "uB": pytest.approx(5.00)}

# ──────────────────────────────────────────────────────────────────────
# 3. 端到端系统测试（End-to-End/System Tests）：CLI 驱动
# ──────────────────────────────────────────────────────────────────────

def test_main_cli_end_to_end(tmp_zone_map_file, tmp_journey_file, tmp_path, monkeypatch, capsys):
    # 准备输出文件路径
    out_file = tmp_path / "bills_out.csv"
    # 模拟命令行参数
    monkeypatch.setattr(sys, "argv", [
        "my_solution.py",
        tmp_zone_map_file,
        tmp_journey_file,
        str(out_file)
    ])
    # 调用主入口
    billing_main()
    # 应该打印提示
    captured = capsys.readouterr()
    assert "[INFO] Billing results written to" in captured.out

    with open(out_file, newline="", encoding="utf-8") as f:
        data = f.read().strip().splitlines()

    # 如果存在表头行 user_id,total_bill，就跳过它
    if data and data[0].startswith("user_id"):
        data = data[1:]

    # 排序后与期望结果比对
    assert sorted(data) == sorted([
        "userX,3.3",
        "userY,5.0"
    ])

