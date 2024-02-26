# Bezrealitky Analysis App

## Overview
This project is my bachelor's thesis focusing on a machine learning analysis of real estate data. The data is scraped from the online platform [Bezrealitky.cz](https://www.bezrealitky.cz) using a custom scraper located in the app folder. The project employs the CRISP-DM methodology for data analysis, including stages like data collection, data description, data quality verification, data exploration, data visualization, and modeling. Modeling techniques include regression, classification, and clustering. The analysis is performed using Python with libraries such as Selenium, Pandas, NumPy, Matplotlib, Seaborn, and Scikit-learn.

## Demo

- **Google colab:** [https://colab.research.google.com/drive/1O2qQCN4eIV-nNOV7UG9vyc8XvXUYcrFh?usp=sharing](https://colab.research.google.com/drive/1O2qQCN4eIV-nNOV7UG9vyc8XvXUYcrFh?usp=sharing)

## Libraries Used

- **Selenium**
- **Pandas**
- **NumPy**
- **Matplotlib**
- **Seaborn**
- **Scikit-learn**

## How to Run

### Prerequisites
- Python 3
- pip

### Setup and Activation
1. Clone the repository to your local machine.

   ```bash
   git clone https://github.com/ViktorSivek/Bezrealitky_analysis_app

2. Create a virtual environment:
   
   ```shell
   python -m venv myenv

3. Activate the virtual environment:
   
   Windows:
   ```shell
   python -m venv myenv
   ```
   macOS/Linux:
   ```shell
   source myenv/bin/activate

4. Install the required dependencies:

   ```shell
   pip install -r requirements.txt

5. Download the latest version of Chromedriver:

   - **Link** [https://chromedriver.storage.googleapis.com/index.html?path=114.0.5735.90/](https://chromedriver.storage.googleapis.com/index.html?path=114.0.5735.90/)

6. In main.py, update the path to the chromedriver.exe and the URL you wish to scrape:
   
   ```shell
   chromedriver_path = "path/to/your/chromedriver.exe"
   url = "https://www.bezrealitky.cz/vypis/nabidka-pronajem/"

7. Run the scraper:
    
   ```shell
   python app/main.py

