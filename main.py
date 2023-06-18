import json
import os
from rich import print
from rich.console import Console
from rich.table import Table
from queue import Queue, PriorityQueue
from collections import deque

"""
RP Calculator made by Gency for League of Legends

Currently only NA support.

Files to note:
    "raw_store.json" -> retrieved from the league client through the use of lcu_driver, needs to be installed as the LoL store updates periodically, unless someone can upload their own json.
    "parsed_store.json" -> created after retrieving purchasables from league client.
"""
console = Console()
purchaseRPLimit = 1 # How many times you want to be able to purchase RP? default
currLimit = 1
global operators

def update_parsed():
    with open('raw_store.json', 'r') as f:
        data = json.load(f)

    result = {}
    for item in data:
        if not item.get('prices') or item['prices'][0]['currency'] != 'RP' or item['prices'][0]['cost'] == 0:
            continue
        if item['sale'] is not None:
            cost = item['sale']['prices'][0]['cost']
            category = 'sale'
        else:
            cost = item['prices'][0]['cost']
            category = None

        if item['subInventoryType'] is not None:
            if category is not None:
                category += ', ' + item['subInventoryType']
            else:
                category = item['subInventoryType']
        else:
            if category is not None:
                category += ', ' + item['inventoryType']
            else:
                category = item['inventoryType']

        if cost in result:
            if category in result[cost]['category']:
                result[cost]['category_count'][category] += 1
            else:
                result[cost]['category'].add(category)
                result[cost]['category_count'][category] = 1
            if category in result[cost]['names']:
                result[cost]['names'][category].append(item['localizations']['en_US']['name'])
            else:
                result[cost]['names'][category] = [item['localizations']['en_US']['name']]
        else:
            if not item.get("localizations"):
                continue
            result[cost] = {'name': item['localizations']['en_US']['name'], 'category': {category}, 'category_count': {category: 1}, 'names': {category: [item['localizations']['en_US']['name']]}}
            
        # check if maxQuantity is 0 and update category_count, means infinite ;')
        if item['maxQuantity'] == 0: # can probably also add if TEAM_SKIN_PURCHASE aka aram boost to be infinite as well.
            result[cost]['category_count'][category] = 999

    for cost, values in result.items():
        values['category'] = list(values['category'])
        for category, count in values['category_count'].items():
            values['category_count'][category] = int(count)

    with open('parsed_store.json', 'w') as f:
        json.dump(result, f)

try:
    from lcu_driver import Connector
    console.print("Note: you need to be logged into league of legends.")
    retrieve = console.input("Would you like to retrieve the your current LoL store? [yes/no]\n")

    if retrieve == "yes":
        connector = Connector()


        async def grab_purchasables(connection):

            # make the request
            retrieve_req = await connection.request('GET' , " /lol-store/v1/catalog")

            if retrieve_req.status == 200:
                print("Retrieved the data.")
                f = open("raw_store.json", "w")
                f.write((str(json.dumps(await retrieve_req.json()))))
                f.close()
                update_parsed()
            else:
                print('Unknown problem, could not retrieve.')


        # fired when LCU API is ready to be used
        @connector.ready
        async def connect(connection):
            print('LCU API is ready to be used.')

            # check if the user is already logged into his account
            summoner = await connection.request('get', '/lol-summoner/v1/current-summoner/summoner-profile')
            if summoner.status != 200:
                print('Please login into your account to grab purchasables.')
            else:
                print('Grabbing purchasables...')
                await grab_purchasables(connection)

        @connector.close
        async def disconnect(_):
            print('The client have been closed!')

        # starts the connector
        connector.start()
    else:
        pass

except:
    console.print("You do not have lcu_driver installed, install it to update `raw_store.json`.")


with open('parsed_store.json', 'r') as f:
    result = json.load(f)

def search_avoid_double(start, goal):
    # queue for stuff that needs to be explored
    queue = PriorityQueue()
    queue.put((0, [start], [], {op: 0 for op, label, num_uses in operators if num_uses > 0}))
    # visited nodes
    visited = set()
    # loop until the queue is empty or goal
    while not queue.empty():
        # get the next node
        cost, path, ops, op_count = queue.get()
        node = path[-1]
        # check if the goal is reached
        if node == goal:
            return path, ops
        # Generate child nodes
        # valid_ops = [(op, label, num_uses) for op, label, num_uses in operators if num_uses <= 0 or op_count[op] < num_uses] broken
        valid_ops = [(op, label, num_uses) for op, label, num_uses in operators if num_uses > 0 and op_count[op] < num_uses]

        # print(valid_ops)

        for op, label, num_uses in valid_ops:
            child = node + op
            if child not in visited and child >= 0:
                # update operator count if necessary
                if num_uses > 0:
                    new_op_count = op_count.copy()
                    new_op_count[op] += 1
                else:
                    new_op_count = op_count
                # add the child node to the queue
                queue.put((cost + 1, path + [child], ops + [(op, label)], new_op_count))
                visited.add(child)
    # no path found
    return None, None

def print_names_for_cost(cost, num_names=None):
    if int(cost) < 0:
        return None
    if cost not in result:
        return f"No items found for cost {cost}"
    
    names_list = []
    for category in result[cost]['names']:
        names = result[cost]['names'][category]
        num_names_to_print = min(len(names), num_names) if num_names else len(names)
        names_to_print = ', '.join(names[:num_names_to_print])
        
        if num_names and len(names) > num_names:
            names_to_print += f", and {len(names) - num_names_to_print} more"
        
        names_list.append(f"{category}: {names_to_print}")
    
    return "\n".join(names_list)

while True:
    start = console.input("How much RP do you have?\n")
    goal = console.input("How much RP do you want to have?\n")
    purchaseRPLimitQuery = console.input("How many times would you like to purchase RP? Default is 1.\n")

    try:
        start = int(start)
        goal = int(goal)
        if purchaseRPLimitQuery != "":
            purchaseRPLimit = abs(int(purchaseRPLimitQuery))
        break
    except:
        print("Please input a number.")
        continue


operators = [(575, "$4.99 RP", purchaseRPLimit), 
             (1275+105, "$10.99 RP", purchaseRPLimit), 
             (2525+275, "$21.99 RP", purchaseRPLimit), 
             (4025+475,"$34.99 RP", purchaseRPLimit), 
             (5750+750,"$49.99 RP", purchaseRPLimit), 
             (11525+1975,"$99.99 RP", purchaseRPLimit)]


for cost, value in result.items():
    traversal_limit = 0
    categories = ', '.join(sorted(value['category']))
    for category, count in value['category_count'].items():
        traversal_limit += count
    operators.append((-int(cost), f"{categories}", traversal_limit))


operators.sort()
# print(operators)
# print(sorted(operators))

# ignore_the_following = {'BOOST', 'HEXTECH_BUNDLE', 'TFT_PASS'} # example: "sale, CHAMPION_SKIN" != "sale", "CHAMPION_SKIN"
ignore_the_following_category = []
ignore_the_following_cost = []

# ignore_the_following_category = {"BOOST"}
# ignore_the_following_cost = {-2821}
while True:
    
    # operators = [elem for elem in operators if elem[1] not in ignore_the_following_category]
    operators = [elem for elem in operators if elem[0] not in ignore_the_following_cost]
    operators.sort()
    if ((ignore_the_following_category)  or (ignore_the_following_cost)):
        console.print("Ignored costs: ", ignore_the_following_cost)
    path, ops = search_avoid_double(start, goal)
    if path is not None:
        # print the start and goal values
        console.print("Start RP: ", start)
        console.print("Goal RP: ", goal)
        # console.print("Path found:", path)

        # make table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Do")
        table.add_column("Category")
        table.add_column("SAMPLE")

        # populate table
        for op, label in ops:
            table.add_row(f"{op:+d}", f"({label})", "")
            names = print_names_for_cost(str(-int(op)), 3)
            if names:
                table.add_row("","", names)

        # table
        console.print(table)
        console.print(f"You will go from [green]{start} RP[/green] to [red]{goal} RP[/red].")
        # console.input("Would you like to remove a category?\n\
        #               Example: 'sale, CHAMPION_SKIN' != 'sale', 'CHAMPION_SKIN'")

    else:
        console.print("No path found")
        exit()
    try:
        costToIgnore = int(console.input("Input a number to ignore.\n\
        Example: '-975' to ignore skins that cost 975 RP\n"))
    except:
        console.log("Input a number please.")
        exit()
    ignore_the_following_cost.append(costToIgnore)