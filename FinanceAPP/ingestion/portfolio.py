class portfolio():
    number_of_portfolio = 0

    def __init__(self, balance= 1000000):
        self.balance = balance
        portfolio.number_of_portfolio += 1
        self.id = portfolio.number_of_portfolio
        self.assets = {}

    def buy_asset(self,symbol, amount, price):
        if (amount*price > self.balance or amount < 0 or price < 0):
            return False
        self.balance -= amount*price
        if symbol in self.assets:
            current_amount = self.assets[symbol]["amount"]
            current_avg_price = self.assets[symbol]["avg_price"]
            new_amount = current_amount + amount
            new_avg_price = ((current_amount * current_avg_price) + amount*price) / new_amount
            self.assets[symbol]["amount"] = new_amount
            self.assets[symbol]["avg_price"] = new_avg_price
        else:
            self.assets[symbol] = {"amount": float(amount),"avg_price": float(price)}
        return True

    def sell_asset(self,symbol,amount,price):
        if (not symbol in self.assets.keys()):
            return False
        if (self.assets[symbol]["amount"] < amount or amount <= 0 or price < 0):
            return False
        self.balance += amount*price
        self.assets[symbol]["amount"] -= amount
        if (self.assets[symbol]["amount"] == 0):
            self.assets.pop(symbol)
        return True

    def total_value_of_porfolio(self, prices):
        s = self.balance
        for k in self.assets.keys():
            s += prices[k]*self.assets[k]["amount"]
        return s

