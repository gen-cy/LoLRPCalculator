
# League of Legends RP Calculator
![Riot Games](https://img.shields.io/badge/riotgames-D32936.svg?style=for-the-badge&logo=riotgames&logoColor=white)


This is an RP Calculator made by me for League of Legends. It helps you calculate the number of RP purchases needed to reach a desired RP goal.

## Requirements

- Python 3.x
- `lcu_driver` library (Install with `pip install lcu_driver`)
- `rich` library (Install with `pip install rich`)

## Files

- `raw_store.json`: Contains the raw data retrieved from the League of Legends client using `lcu_driver`. This file needs to be updated periodically as the LoL store changes.
- `parsed_store.json`: Contains the parsed data extracted from `raw_store.json`.

## Usage

1. If you want to retrieve your current store, make sure you are logged into League of Legends. 
2. Run `main.py` and choose whether to retrieve the current LoL store. This will be asked if you have `lcu_driver` installed.
3. Enter your current RP amount and the desired RP goal.
4. Optionally, specify the number of times you want to purchase RP.
5. The script will calculate the path to reach the goal and display the RP amounts and categories involved.
6. You can ignore specific RP costs by entering the corresponding numbers. Example, to ignore 975 RP costs, type '-975'.
7. The script will continue recalculating the path until the goal is reached or no path is found.

## Features

- **Avoiding Specific Costs**: You can specify costs (e.g., -975) to be avoided in the RP calculation.
- **Viewing Sample Purchases**: The script displays sample purchases for each RP amount involved in the path.
- **Auto-Update Store Data**: The `raw_store.json` file can be updated by retrieving the current store data from the League of Legends client.
- **Path Optimization**: The script finds the shortest path by considering the number of RP purchases needed and the available RP options.


## How It Works

The script uses a graph traversal algorithm to find the shortest path from the current RP amount to the desired RP goal. It considers RP purchase options and their associated costs. The `raw_store.json` file is used to retrieve the purchasable RP options from the League of Legends client.



## TODO

- [ ] Add the ability to avoid specific categories during the RP calculation.
- [ ] Improve the display of sample purchases to make it easier to view and understand.
- [ ] Implement a command-line interface (CLI) with user-friendly prompts and options.
- [ ] Add error handling and input validation for user inputs.
- [ ] Implement unit tests to ensure the correctness of calculations and functionality.
- [ ] Optimize the RP path calculation algorithm for efficiency.
- [ ] Support multiple regions and currencies for RP calculations. Currently only supports NA
- [ ] Create a graphical user interface (GUI) for easier interaction. Could be turned into a website, but I would need to periodically update the json file. This would also not be custom for each user, for example, it will suggest to purchase something a user already owns.
