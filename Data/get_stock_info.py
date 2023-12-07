""" Retrieves stock information (like if it accepts fractional trades) for quick reference and stores it in stocks.json.
Entered as an arguement individually (get_stock_info.py -a ex1) in the terminal or as a list (get_stock_info.py -a 'ex1, ex2, etc...')."""
import requests
import sys
import os
import json
import ast
import argparse

# Get parent directory
path = os.path.dirname(__file__)
parent = os.path.abspath(os.path.join(path, os.pardir))
sys.path.append(parent)

from getKeys import getKeys

filename = os.path.join(path + os.sep + "stocks.json")

try:
    f = open(filename, "r")
except FileNotFoundError:
    f = open(filename, "x")
    f.write("[]")
finally:
    f.close()

with open(filename, "r") as f:
    stocks = json.load(f)

# create an argument parser
parser = argparse.ArgumentParser(
    prog="Get stock info",
    description="Retrieves stock information and stores it in stocks.json. Can be entered individually like 'MSFT' or in a series like 'MSFT, FCEL'.",
)

# add arguments
parser.add_argument("-a", "--add", help="Adds a stock(s) to stocks.json")
parser.add_argument("-rm", "--remove", help="Removes a stock(s) from stocks.json")
parser.add_argument(
    "-c", "--clear", help="Clears a stock(s) preference from stocks.json"
)
parser.add_argument("-rl", "--real", help="Sets a stock(s) preference to real")
parser.add_argument("-p", "--paper", help="Sets a stock(s) preference to paper")

# parse arguments
try:
    args = parser.parse_args()
except Exception as e:
    print(e)


class StockUpdater:
    def __init__(self, stocklist=[], write=True):
        # By default, stocks from the main list should be passed in.
        self.stocklist = stocklist
        # Added for testing purposes so it doesn't make changes.
        self.write = write

    def sort(self):
        list.sort(self.stocklist, key=lambda stock: stock["symbol"])

    def stockSplitter(self, assetList):
        # For adding new stocks. Determines if the input is an indicidual stock or list.
        if isinstance(assetList, list):
            self.Multistock(assetList)
        elif isinstance(assetList, str):
            self.updateStockInfo(self.getStockInfo(assetList))
        else:
            raise Exception(f"stockSplitter received wrong type {type(assetList)}")
        sorted(self.stocklist, key=lambda stock: stock["symbol"])
        self.writeStockInfo()

    def Multistock(self, assetList):
        # Parses a list of stocks and uses getSockInfo function to retrieve informaion.
        assets = []
        for item in assetList:
            assets.append(self.updateStockInfo(self.getStockInfo(item)))

        return assets

    def getStockInfo(self, asset):
        # Get individual stock information and store it in stocks.JSON in the Data directory.
        account = getKeys("paperTrading")
        url = "https://paper-api.alpaca.markets/v2/assets/" + asset.upper()

        headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": account["api_key"],
            "APCA-API-SECRET-KEY": account["secret_key"],
        }

        response = requests.get(url, headers=headers)
        return json.loads(response.text)

    def findStock(self, asset):
        for stock in self.stocklist:
            if asset.upper() == stock["symbol"]:
                return stock
        else:
            return None

    def updateStockInfo(self, asset):
        # Adds or updates one asset. Adds account key to asset dictionary for user account preference ("paper", "real"). Also updates the asset data if there are changes.
        print(f"Adding stock: {asset['symbol']}")
        for n, stock in enumerate(self.stocklist):
            if asset["symbol"] == stock["symbol"]:
                if not "account" in stock:
                    self.stocklist[n]["account"] = ""
                self.stocklist[n].update(asset)
                break
        else:
            asset["account"] = ""
            self.stocklist.append(asset)
        return

    def stockRemover(self, asset):
        # removes individual stocks or a list of stocks. Main app
        if isinstance(asset, list):
            for item in asset:
                self.removeStock(item)
        elif isinstance(asset, str):
            self.removeStock(asset)
        else:
            raise Exception(f"stockRemover received wrong type {type(asset)}")
        self.writeStockInfo()

    def removeStock(self, asset):
        # removes individual stocks (ex. "AAPL")
        asset = asset.upper()
        print(f"Removing stock: {asset}")
        for n, stock in enumerate(self.stocklist):
            if asset.upper() == stock["symbol"]:
                self.stocklist.pop(n)
                break
        else:
            print(f"Stock not found in stocks list to remove: {asset}")

    def writeStockInfo(self):
        if self.write:
            self.sort()
            with open(filename, "w+") as f:
                json.dump(self.stocklist, f, indent=4)

    def getAccountPreference(self):
        if self.stocklist == []:
            print("Empty stocks list")
            return
        self.sort()
        real = []
        paper = []
        neither = []
        for stock in self.stocklist:
            if stock["account"] == "":
                neither.append(stock["symbol"])
            elif stock["account"].upper() == "real".upper():
                real.append(stock["symbol"])
            elif stock["account"].upper() == "paper".upper():
                paper.append(stock["symbol"])
            else:
                print(
                    f'Problem found. Stock "{stock}" does not have account setting. Try removing and adding it again.'
                )
        print(f"No preference: {neither},\nreal: {real},\npaper: {paper}")

    def setAccountPreference(self, arg, accountPref):
        # Set or clear stock account preferences.
        changed = False
        if isinstance(arg, list):
            for stock in arg:
                stockPref = self.findStock(stock)
                if stockPref:
                    stockPref["account"] = accountPref
                    changed = True
                else:
                    print(f"Stock not found for: {stock}")
        elif isinstance(arg, str):
            stockPref = self.findStock(arg)
            if stockPref:
                stockPref["account"] = accountPref
                changed = True
            else:
                print(f"Stock not found for: {arg}")
                return
        else:
            raise Exception(f"setAccountPreference received wrong type {type(arg)}")
        if changed:
            self.writeStockInfo()


def getListOrString(arg1):
    # Detmine if argument is string or list
    try:
        inputList = ast.literal_eval(arg1)
        inputList = [stock.strip().upper() for stock in inputList]
    except ValueError:
        if "," in arg1:
            inputList = arg1.split(",")
            inputList = [stock.strip().upper() for stock in inputList]
        else:
            inputList = arg1.strip().upper()
    return inputList


if __name__ == "__main__":
    # Allows for adding, removing, and setting of stock preferences for account (paper/real)
    manualStock = StockUpdater(stocks)
    newArgs = ""
    if args.add:
        newArgs = getListOrString(args.add)
        manualStock.stockSplitter(newArgs)
    elif args.remove:
        newArgs = getListOrString(args.remove)
        manualStock.stockRemover(newArgs)
    elif args.clear:
        newArgs = getListOrString(args.clear)
        manualStock.setAccountPreference(newArgs, "")
    elif args.paper:
        newArgs = getListOrString(args.paper)
        manualStock.setAccountPreference(newArgs, "paper")
    elif args.real:
        newArgs = getListOrString(args.real)
        manualStock.setAccountPreference(newArgs, "real")
    else:
        # Print the list of stocks account preferences if no arguments are given.
        manualStock.getAccountPreference()
