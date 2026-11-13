# Starbucks vs McDonald's Snack Analysis

A PySpark project starter for comparing the nutritional information of Starbucks and McDonald's menu items.

## Project status

This ZIP contains the project structure, dependency list, and a PySpark smoke test. The restaurant datasets are stored as CSV files in `dataset/raw/`.

Dataset folder: https://drive.google.com/drive/folders/15oTNsPitK_wXZMYILs3uchgY1LytMtI1

## Requirements

- Windows 10/11
- Python 3.10 or 3.11 (Python 3.11 recommended)
- Java JDK 17
- VS Code with the Microsoft Python extension

## Setup in VS Code (PowerShell)

Open this folder in VS Code, then open Terminal > New Terminal.

```powershell
python --version
java -version
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks environment activation, run this for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

In VS Code, press `Ctrl+Shift+P`, choose **Python: Select Interpreter**, and select the Python executable in `venv`.

## Test PySpark

```powershell
python main.py
```

The script creates a tiny in-memory sample solely to verify that Spark starts. These rows are illustrative and are not real menu data.

## Add the real datasets

Download the CSV files from the assignment Drive folder and put them in:

- `dataset/raw/starbucks_drinkMenu_expanded.csv`
- `dataset/raw/menu.csv`

The raw folder also contains separate Starbucks food and drink nutrition files. The entry point currently compares the expanded Starbucks drinks dataset with the McDonald's menu dataset.

## Run the project

```powershell
python main.py
```

Once the CSV files are added, the starter loader will inspect and print their schemas and first rows. The full nutritional comparison and final report will be developed in subsequent steps.

## Current folder structure

```text
Starbucks_McDonalds_Snack_Analysis/
├── dataset/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── analysis.py
│   └── visualization.py
├── output/
│   └── charts/
├── reports/
├── main.py
├── requirements.txt
└── README.md
```
