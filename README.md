0. Overview
This project implements a mass transit billing system in Python. It ingests user journey records and station zone mapping from CSV files, and outputs the total bill for each user.

1. File Directory 
```text
mass_transport_billing_design/
├── my_solution.py         # Main program
├── test_my_solution.py    # Automated test file (pytest)
├── zone_map.csv           # Example station-to-zone input file
├── journey_data.csv       # Example user journey input file
├── my_output.csv          # Output file (generated after running the program)
└── README.md              
```
2. How to Run
```bash
python my_solution.py zone_map.csv journey_data.csv my_output.csv
```
To run all automated tests:
```bash
pytest test_my_solution.py
```
3. Requirements

Python 3.7+ 
pytest (for running test_my_solution.py)