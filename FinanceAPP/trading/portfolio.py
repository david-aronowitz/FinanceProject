from common.DatabaseManager import DatabaseManager
class Portfolio():
    number_of_portfolio = 0

    def __init__(self, balance= 1000000):
        self.balance = balance
        Portfolio.number_of_portfolio += 1
        self.id = Portfolio.number_of_portfolio
        self.assets = {}
        self.db = DatabaseManager()

    def buy_asset(self, symbol, price, amount):
        if (amount * price > self.balance or amount <= 0 or price <= 0):
            return False
        self.balance -= amount * price
        if symbol in self.assets:
            current_amount = self.assets[symbol]["amount"]
            current_avg_price = self.assets[symbol]["avg_price"]
            new_amount = current_amount + amount
            new_avg_price = ((current_amount * current_avg_price) + (amount * price)) / new_amount
            self.assets[symbol]["amount"] = new_amount
            self.assets[symbol]["avg_price"] = new_avg_price
        else:
            self.assets[symbol] = {"amount": float(amount), "avg_price": float(price)}
        self.db.save_transaction(self.id, "buy", symbol, price, amount)
        self.db.update_holding(symbol, price, self.assets[symbol]["amount"])
        return True

    def sell_asset(self,symbol, price,amount):
        if (not symbol in self.assets.keys()):
            return False
        if (self.assets[symbol]["amount"] < amount or amount <= 0 or price < 0):
            return False
        self.balance += amount*price
        self.assets[symbol]["amount"] -= amount
        self.db.update_holding(symbol,price,self.assets[symbol]["amount"])
        if (self.assets[symbol]["amount"] == 0):
            self.assets.pop(symbol)
        self.db.save_transaction(self.id, "sell", symbol, price, amount)
        return True

    def total_value_of_portfolio(self, prices):
        s = self.balance
        for k in self.assets.keys():
            s += prices[k]*self.assets[k]["amount"]
        return s

