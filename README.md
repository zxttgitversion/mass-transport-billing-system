0. Overview
This project implements a mass transit billing system in Python. It ingests user journey records and station zone mapping from CSV files, and outputs the total bill for each user.

1. File Directory 
```text
mass_transport_billing_design/
├── src/
│   └── transit_billing/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── models.py           # Domain models: JourneyEvent, User
│       ├── fare_rules.py       # Fare constants and zone pricing
│       ├── parser.py           # CSV loading and time parsing
│       ├── billing_service.py  # BillingSystem orchestration service
│       └── exceptions.py       # Domain-specific exceptions
├── tests/
│   ├── conftest.py             # Adds src/ to import path for tests
│   ├── test_fare_rules.py      # Fare rule unit tests
│   ├── test_models.py          # Journey and user billing unit tests
│   ├── test_parser.py          # CSV and time parsing tests
│   ├── test_billing_service.py # CSV/service integration tests
│   └── test_cli.py             # CLI end-to-end tests
├── resources/
│   ├── zone_map.csv            # Example station-to-zone input file
│   ├── journey_data.csv        # Example user journey input file
│   └── my_output.csv           # Output file (generated after running the program)
└── README.md              
```
2. How to Run
Install development dependencies:
```bash
pip install -r requirements.txt
```

```bash
PYTHONPATH=src python -m transit_billing.cli resources/zone_map.csv resources/journey_data.csv resources/my_output.csv
```
On Windows PowerShell:
```powershell
$env:PYTHONPATH="src"; python -m transit_billing.cli resources/zone_map.csv resources/journey_data.csv resources/my_output.csv
```
To run all automated tests:
```bash
pytest
```
To run tests with coverage:
```bash
pytest --cov=transit_billing --cov-report=term-missing
```
3. Test Coverage

Current test suite:

- 27 pytest tests
- 96% total coverage with branch coverage enabled
- Covers fare rules, user billing logic, parser validation, service integration, and CLI flow

Latest coverage summary:

```text
Name                                     Stmts   Miss Branch BrPart  Cover
------------------------------------------------------------------------------------
src\transit_billing\billing_service.py      27      1      4      0    97%
src\transit_billing\cli.py                  19      2      4      2    83%
src\transit_billing\models.py               63      1     22      1    98%
src\transit_billing\parser.py               47      2     10      0    96%
------------------------------------------------------------------------------------
TOTAL                                      180      6     50      3    96%
```

4. Requirements

Python 3.7+ 
pytest and pytest-cov
