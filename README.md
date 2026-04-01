# SDG 13 Climate Action: CO2 Emission Analysis

Setup and Installation Guide

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8 or higher** – [Download Python](https://www.python.org/downloads/)
- **pip** (Python package manager) – comes with Python

### Check if Python is installed:
```bash
python3 --version
```

---

## Step-by-Step Installation & Setup

### Step 1: Navigate to the Project Directory

```bash
cd co2emissionProject
```

Or, if the project is in a different location:

```bash
cd /path/to/co2emissionProject
```

### Step 2: Create a Virtual Environment (Recommended)

A virtual environment isolates project dependencies from your system Python.

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

**Note:** You should see `(.venv)` at the beginning of your terminal prompt when activated.

### Step 3: Install Required Dependencies

The project requires several Python packages. Install them using pip:

```bash
pip install --upgrade pip
pip install pandas numpy plotly jupyter
```

**Individual package descriptions:**
- **pandas** – Data manipulation and analysis
- **numpy** – Numerical computing
- **plotly** – Interactive visualizations
- **jupyter** – Jupyter Notebook environment

### Step 4: Verify Installation

```bash
python3 -c "import pandas, numpy, plotly, jupyter; print('All packages installed successfully!')"
```

---

## Running the Notebook

### Option 1: Launch Jupyter Notebook (Interactive)

This is the recommended approach for step-by-step execution and viewing outputs.

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Start Jupyter Notebook
jupyter notebook
```

**What happens next:**
1. Jupyter will start and open in your default browser (usually at `http://localhost:8888`)
2. Navigate to `notebook.ipynb` in the file browser
3. Click to open the notebook

**Running cells in the notebook:**
- Click a cell to select it
- Press `Shift + Enter` to run the cell
- Or use the "Run" button in the toolbar
- Run cells sequentially from top to bottom

### Option 2: Run the Entire Notebook from Terminal

```bash
source .venv/bin/activate
jupyter nbconvert --to notebook --execute notebook.ipynb --output notebook_executed.ipynb
```

This will execute all cells and save results to a new file `notebook_executed.ipynb`.

---

## Running the Streamlit App 

### Step 1: Install Streamlit

```bash
source .venv/bin/activate
pip install streamlit
```

### Step 2: Run the Streamlit Application

```bash
source .venv/bin/activate
streamlit run app.py
```

**What happens next:**
1. Streamlit will start and automatically open in your default browser (usually at `http://localhost:8501`)
2. The app provides an interactive dashboard for exploring the CO2 emission analysis
3. You can interact with charts, filter by country/region, and view key metrics

**Stopping the Streamlit app:**
- Press `Ctrl + C` in the terminal where Streamlit is running

---

## Project Structure

```
co2emissionProject/
├── notebook.ipynb                          # Main Jupyter Notebook
├── app.py                                  # Streamlit app 
├── README.md                               # This file
├── owid-co2-data.csv                       # CO2 emissions data
├── global-data-on-sustainable-energy (1).csv  # Energy transition data
├── owid-co2-codebook.csv                   # Data dictionary
├── .venv/                                  # Virtual environment
└── __pycache__/                            # Python cache files
```
