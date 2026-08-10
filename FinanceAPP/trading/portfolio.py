from common.DatabaseManager import DatabaseManager
class Portfolio():
    number_of_portfolio = 0

    def __init__(self,id=0, balance= 1000000):
        self.balance = balance
        self.db = DatabaseManager()

        if (id == 0):
            Portfolio.number_of_portfolio += 1
            self.id = Portfolio.number_of_portfolio
            self.assets = {}
        else:
            self.id = id
            raw_holdings = self.db.get_holdings(id)
            self.assets = {}
            for row in raw_holdings:
                symbol = str(row[1])
                avg_price = float(row[2])
                amount = float(row[3])
                self.assets[symbol] = {"amount": amount, "avg_price": avg_price}
            all_users = self.db.get_users()
            found_balance = None
            for u in all_users:
                if u[0] == self.id:
                    found_balance = u[3]
                    break
            if found_balance is not None:
                self.balance = float(found_balance)
            else:
                self.balance = balance

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
        self.db.update_holding(self.id, symbol, self.assets[symbol]["avg_price"], self.assets[symbol]["amount"])
        self.db.update_user_balance(self.id, self.balance)
        return True

    def sell_asset(self,symbol, price,amount):
        if (not symbol in self.assets.keys()):
            return False
        if (self.assets[symbol]["amount"] < amount or amount <= 0 or price < 0):
            return False
        self.balance += amount*price
        self.assets[symbol]["amount"] -= amount
        self.db.update_holding(self.id, symbol, self.assets[symbol]["avg_price"], self.assets[symbol]["amount"])
        if (self.assets[symbol]["amount"] == 0):
            self.assets.pop(symbol)
        self.db.save_transaction(self.id, "sell", symbol, price, amount)
        self.db.update_user_balance(self.id, self.balance)
        return True

    def total_value_of_portfolio(self, prices):
        s = self.balance
        for k in self.assets.keys():
            if prices.get(k) is not None:
                s += prices[k]*self.assets[k]["amount"]
        return s
