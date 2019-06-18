import urllib, json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from urllib.request import urlopen
from urls import urls
from tabulate import tabulate
from collections import defaultdict

class Parser(object):
	def __init__(self, date=False):
		self.date = date

	def read_url(self):
		if self.date: 
			url = urls["by_date"] % self.date
		else:
			url = urls["today"]
		return url

	def load_data(self):
		response = urlopen(self.read_url())
		return response

	def parse_data(self):
		data = json.loads((self.load_data()).read().decode("utf-8"))
		return data

	def get_data(self):
		return self.parse_data()

class Data(object):
	def __init__(self):
		self.parser = Parser()
		self.data = self.parser.get_data()

	def print_data(self):
		for dic in self.data:
			out = {"Currency": dic["txt"], "Rate": str(dic["rate"])}
			dict_df = pd.DataFrame(out, index=[0])
			print(tabulate(dict_df, headers='keys', tablefmt='psql'))

	### still doesn't work properly, gotta fix soon
	def print_graph(self, first_date, last_date): # YYYYMMDD format 
		ax = plt.gca()
		dd = defaultdict(list)
		# colors = ('#E52B50', '#FFBF00', '#9966CC')
		for dates in range(first_date, last_date + 1):
			local_parser = Parser(str(dates))
			local_data = local_parser.get_data()
			txt = pd.DataFrame(local_data, columns = ['txt'])
			df = pd.DataFrame(local_data, columns = ['rate'])
			dict_from_df = df.to_dict(orient='dict')

			for keys in dict_from_df["rate"]:
				dd[keys].append(dict_from_df["rate"][keys])

		series = pd.Series(dd)
		plot = pd.DataFrame(series)

		dates_list = []
		for dates in range(first_date, last_date + 1):
			dates_list.append(dates)

		for rate in plot[0]:
			plt.plot(dates_list, rate)

		legend_dict = txt.to_dict(orient='list')
		patchList = []
		for key in legend_dict["txt"]:
			data_key = mpatches.Patch(label=key)
			patchList.append(data_key)

		# plt.legend(handles=patchList) # this is broken so far
		plt.show()

	def convert(self, currency, currency_amount): #three capital letters for currency code and a num for currency amount
		current_rates = self.data
		best_rate = 0
		current_rate = 0
		dateof_best_rate = 0

		for rates in current_rates:
			if rates["cc"] == currency:
				current_rate = rates["rate"]

		for dates in range(20180101, 20181202, 100): #gonna change 100 to 1 for day by day comparison instead of months later
			local_parser = Parser(str(dates))
			local_data = local_parser.get_data()
			for curr in local_data:
				if curr["cc"] == currency:
					rate = curr["rate"]
					if rate > best_rate:
						best_rate = rate
						dateof_best_rate = curr["exchangedate"] 

		total_current_amount = current_rate * currency_amount
		best_amount = best_rate * currency_amount
		ratio = total_current_amount / best_amount * 100 #per cents of uah you're getting today comparing to the best last year's rate; more than 100 means you win
		###i'm tired of beautiful prints
		return ("Comparing to rate on " + str(dateof_best_rate) + ", " + str(best_amount) + ", today you gain " + str(ratio) + " per cent of it, which is " + str(total_current_amount))
