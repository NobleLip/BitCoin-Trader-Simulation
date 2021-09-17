import requests
import time
import sqlite3
import json
import datetime

#Conecta DB
conn = sqlite3.connect('CarteiraCript.db')
c = conn.cursor()
#
Crypto = {}

def AdicionarValores():
	url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
	parameters = {
		'convert':'EUR'
	}
	headers = {
		'Accepts':'application/json',
		'X-CMC_PRO_API_KEY': 'XXX'
	}
	R = requests.get(url, params = parameters, headers =headers)
	BitCoin = (R.json())


	for Dta in BitCoin['data']:
		Crypt = {'id' : Dta['id'] , 'Price' : Dta['quote']['EUR']['price']}
		Crypto[Dta['symbol']] = Crypt

AdicionarValores()

try:
	c.execute('''CREATE TABLE Carteira ([Coin] TEXT NOT NULL UNIQUE ,[Quantidade] FLOAT NOT NULL,[Lucros] FLOAT)''')
	conn.commit()
	c.execute('''CREATE TABLE Log ([Data] TEXT NOT NULL ,[Coin] TEXT NOT NULL,[Quantidade] FLOAT NOT NULL, [Gastos] FLOAT)''')
	conn.commit()
	c.execute('''INSERT INTO Carteira(Coin, Quantidade) VALUES('Eur', 10000)''')
	conn.commit()

	for Moeda in Crypto:
		c.execute('''INSERT INTO Carteira(Coin, Quantidade, Lucros) VALUES(?, ?, ?)''', [Moeda, 0, 0])
		conn.commit()
	print('[+]Wallet created')

except:
	print('[+]Connection to Data Base Done')


def VerificarSaldo():
	Euros = c.execute('''SELECT * FROM Carteira WHERE Coin = 'Eur' ''')
	for i in Euros:
		Euros = i[1]
	print('[+]Saldo : '+ str(Euros))

def InvestirMoeda(Moeda, Eur):
	Euros = c.execute('''SELECT * FROM Carteira WHERE Coin = 'Eur' ''')
	for i in Euros:
		Euros = i[1]
	if float(Euros) < float(Eur) and float(Eur) >= 0:
		return print('[+]Impossible to invest more than what you have!')
	else:
		QuantidadeMoeda = c.execute('''SELECT * FROM Carteira WHERE Coin = ?''', [Moeda])
		for Quantidade in QuantidadeMoeda:
			Lucro = Quantidade[2]
			QuantidadeMoeda = Quantidade[1]
		MoedasCompradas = Eur / Crypto[Moeda]['Price']
		Lucro = Lucro - Eur
		print('[+]Buyed '+ str(MoedasCompradas) + ' Coins of '+ str(Moeda))
		QuantidadeMoeda = QuantidadeMoeda + MoedasCompradas
		Euros = Euros - Eur
		c.execute('''UPDATE Carteira SET Coin=?, Quantidade=?, Lucros=? WHERE Coin=?''', [Moeda, QuantidadeMoeda, Lucro ,Moeda])
		conn.commit()
		c.execute('''UPDATE Carteira SET Coin=?, Quantidade=? WHERE Coin=?''', ['Eur', Euros, 'Eur'])
		conn.commit()
		c.execute('''INSERT INTO Log(Data, Coin, Quantidade, Gastos) Values(?,?,?,?)''', [(datetime.datetime.today().date()), Moeda,MoedasCompradas, Lucro])
		conn.commit()

def VerificarLogs():
	Logs = c.execute('''SELECT * FROM Log''')

	for Log in Logs:
			print('[+]Data: '+ str(Log[0])+'  Coin: '+ str(Log[1])+ ' Quantity: '+ str(Log[2])+ ' Wins: '+ str(Log[3]))

def VerificarLucros():
	Carteira = c.execute('''SELECT * FROM Carteira''')
	for Moeda in Carteira:
		if Moeda[1] > 0 and Moeda[0] != 'Eur':
			print('[+]Coin '+ str(Moeda[0]) + ' : ' + str(Moeda[1]) + '   Total Spent: ' + str(Moeda[2]))
			print('		Wins : ' + str( (Moeda[1] * Crypto[Moeda[0]]['Price']) + Moeda[2]) + ' €')

def VenderMoeda(Moeda, Quantidade, Tudo):
	#Não esquecer dar update nos lucros
	Euros = c.execute('''SELECT * FROM Carteira WHERE Coin = ?''', ['Eur'])
	for i in Euros:
		Euros = i[1]
	Quant = c.execute('''SELECT * FROM Carteira WHERE Coin = ?''', [Moeda])
	for i in Quant:
		Quant = i[1]
		Lucros = i[2]
	if Tudo == 1 and Quant > 0:
		Euros = Euros + Quant * Crypto[Moeda]['Price']
		Lucros = Lucros + Quant * Crypto[Moeda]['Price']
		c.execute('''UPDATE Carteira SET Coin=?, Quantidade=? WHERE Coin=?''', ['Eur', Euros, 'Eur'])
		conn.commit()
		c.execute('''UPDATE Carteira SET Coin=?, Quantidade=?, Lucros=? WHERE Coin=?''', [Moeda, 0, Lucros, Moeda])
		conn.commit()
		print('[+]Sold all the Coins '+ str(Moeda) + ' For ' + str(Lucros) + ' €')
		c.execute('''INSERT INTO Log(Data, Coin, Quantidade, Gastos) Values(?,?,?,?)''', [(datetime.datetime.today().date()), Moeda , -Quant, Lucros])
		conn.commit()
	else:
		if Quantidade <= Quant and Quant > 0:
			Euros = Euros + Quantidade * Crypto[Moeda]['Price']
			Lucros = Lucros + Quantidade * Crypto[Moeda]['Price']
			Quant = Quant - Quantidade
			c.execute('''UPDATE Carteira SET Coin=?, Quantidade=? WHERE Coin=?''', ['Eur', Euros, 'Eur'])
			conn.commit()
			c.execute('''UPDATE Carteira SET Coin=?, Quantidade=?, Lucros=? WHERE Coin=?''', [Moeda, Quant, Lucros, Moeda])
			conn.commit()
			print('[+]Sold '+ str(Moeda) + ' for ' + str(Quantidade * Crypto[Moeda]['Price']) + ' €')
			c.execute('''INSERT INTO Log(Data, Coin, Quantidade, Gastos) Values(?,?,?,?)''', [(datetime.datetime.today().date()), Moeda, -Quantidade, Lucros])
			conn.commit()
		else:
			print('[+]Not Enough Coins')

def AtualizaValores():
	Crypto = {}
	AdicionarValores()

def ListarMoedas():
	for Moeda in Crypto:
		print('[+]Coin:' + str(Moeda) + ' Price per Coin: ' + str(Crypto[Moeda]['Price']) + ' €')

Run = 1

while Run:
	opcao = 0
	VerificarSaldo()
	opcao = int(input('[+]1 - Invest in Cripto\n[+]2 - Sell Cripto\n[+]3 - Update Values\n[+]4 - List Cripto Coins\n[+]5 - Verify Current Wins\n[+]6 - Verify Logs\n[+]7 - Exit\n'))

	if opcao == 1:
		Coin = input('[+]Say what coin do you whant to invest , exemple : BTC\n')
		Quantidade = int(input('[+]How many Euros to investe?\n'))
		try:
			Crypto[Coin]
			InvestirMoeda(Coin, Quantidade)
		except:
			print('[+]Coin no Available')
	elif opcao == 2:
		Coin = input('[+]Say what coin do you whant to Sell , exemple : BTC\n')
		Tudo = int(input('[+]Sell all the coins? 1-yes 0-no\n'))
		if Tudo:
			VenderMoeda(Coin, 0 ,Tudo)
		elif Tudo == 0:
			Quantidade = float(input('[+]How many coins do you whant to sell?\n'))
			VenderMoeda(Coin, Quantidade,Tudo)
	elif opcao == 3:
		AtualizaValores()
	elif opcao == 4:
		ListarMoedas()
	elif opcao == 5:
		VerificarLucros()
	elif opcao == 6:
		VerificarLogs()
	elif opcao == 7:
		Run = 0