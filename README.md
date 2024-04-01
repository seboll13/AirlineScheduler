## Automatic Airline Scheduler
_Project in progress, to take with a grain of salt ..._

### Overview
The goal of this project is to provide an automatic system that allows one to schedule flights for an entire fleet of aeroplanes.
Flights are assigned based on a demand calculated using real world data. The system is designed to be flexible and can be used to schedule flights for any number of aeroplanes and airports.

### Features
- **Automatic Scheduling**: Automatically schedules flights for a fleet of aeroplanes based on demand.
- **Demand Estimation**: Estimates demand for first, business and economy flight classes using a series of personalised algorithms.
- **Data Integration**: Incorporates real-world data from various sources to model economic indicators, population matrics, and tourism statistics.
- **Route Analysis**: Evaluates and suggests optimal routes based on calculated passenger demand and other factors.

### Tools Used
- **Programming Language**: Python 3.11+
- **Database Management**: MySQL
- **Code Formatting**: Black and Ruff
- **External APIs**: World Bank API for real-world economic and population data as well as geonames.org for city data.
- **Libraries**: Numpy, Scipy, MySQL Connector.

### Personal Work Disclaimer
All work and algorithms presented in this project are personal and created as part of an independent simulation exercise. While the algorithms are inspired by real-world data and scenarios, they are tailored for theoretical modeling and analysis within this project's context. This work is not affiliated with any official or commercial airline management software or system.

### Usage
1. Clone the repository to your local machine.
2. Setup a virtual environment with Python 3.11+.
3. Install the required dependencies using `pip install -r requirements.txt`.
4. ```cd``` to the code directory and run the main script using `python main.py`.
5. Demand will be calculated and flights will be scheduled automatically.

Make sure to download the GlobalAirportDatabase from [here](https://www.partow.net/miscellaneous/airportdatabase/index.html#Downloads) before running the script.

### License
This project is licensed under the MIT License. You are free to use, modify, and distribute the code as you see fit. For more information, please refer to the LICENSE file in the repository.