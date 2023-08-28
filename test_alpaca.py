from flasktest import AutomatedTrader, filePath
import unittest, os, json

paperTrading = {'api_key': os.environ.get('Alpaca_API_KEY'),
'secret_key': os.environ.get("Alpaca_SECRET_KEY"),
'paper': True}

realTrading = {'api_key': os.environ.get('Alpaca_API_KEY-real'),
'secret_key': os.environ.get("Alpaca_SECRET-real"),
'paper': False}

options = {
  # Enable/disable shorting. Not fully implemented yet. 
  # Alert(s) needs to say short and you have to close any long positions first.
  "short": False,
  # Hard set at the moment to 20% of the cash balance. Useful in paper testing if you have around 5 stock alerts you want to analyse.
  # Be careful, if more than one order is going through at the the same time, it may spend over the total cash available and go into margins. Mainly a problem in real money trading.
  # Behaves differently when testMode is enabled.
  "buyPerc": 0.2,
  # Balance is set in the function setBalance().
  "balance": 0,
  # Not used
  "buyBal": 0,
  # Gets open potisions to verify ordering. Multiple buys before selling not implemented yet.
  "positions": [],
  # Retrieves open orders is there are any for the symbol requested.
  "orders": [],
  # Gets all the open orders.
  "allOrders": [],
  # Testmode sets the balance to a predetermined amount set in createOrder.
  # Used to not factor in remaining balance * buyPerc after positions are opened.
  "testMode": True,
  # enabled will allow submission of orders.
  "enabled": True,
  # Not used?
  "req": "",
  # Setting to True will impose a predefined limit for trades
  "limit": True,
  # How much to limit the buy/sell price. Order not filled before sell will be canceled. Change to %
  "limitamt": 0.04,
  # limit percent for everything above a certain amount which is predefined for now below.
  "limitPerc": 0.0005
}

path = filePath()

market = {
  'Bull': "LDC Kernel Bullish \xe2\x96\xb2 | CLSK@4.015 | (1)",
  'Bear': "LDC Kernel Bearish \xe2\x96\xb2 | CLSK@4.015 | (1)",
  'Open': "LDC Open Long \xe2\x96\xb2 | MSFT@327.30 | (1)",
  'OpenCLSK': "LDC Open Long \xe2\x96\xb2 | CLSK@3.83 | (1)",
  'OpenFCEL': "LDC Open Long \xe2\x96\xb2 | FCEL@23.30 | (1)",
  'Close': "LDC Close Short \xe2\x96\xb2 | CLSK@4.015 | (1)",
  'Short': "LDC Open Short \xe2\x96\xb2 | CLSK@4.015 | (1)",
  'ShortFCEL': "LDC Open Short \xe2\x96\xb2 | FCEL@2.47 | (1)",
  'ShortMSFT': "LDC Open Short \xe2\x96\xb2 | MSFT@327.30 | (1)",
  'Long': "LDC Close Long \xe2\x96\xb2 | CLSK@4.015 | (1)",
  'LongFCEL': "LDC Close Long \xe2\x96\xb2 | FCEL@23.30 | (1)",
  'Position': "LDC Open Position \xe2\x96\xb2 | CLSK@4.015 | (1)",
  'CPositionNVDA': "LDC Close Position  \xe2\x96\xb2\xe2\x96\xbc | NVDA@[386.78] | (1)",
  }

class TestAlpaca(unittest.TestCase):
  
  # realClient = AutomatedTrader(**realTrading, newOptions={})
  # paperClient = AutomatedTrader(**paperTrading, newOptions={})
  def test_settings(self):
    # Verify settings file can be loaded properly
    with open(path+os.sep + 'settings.json') as f:
      settings = json.load(f)
    self.assertEqual(type(settings['testMode']), bool)
    self.assertEqual(type(settings['orders']), list)
    self.assertEqual(type(settings['buyPerc']), float)
  def test_extraOptions(self):
    # Test for typos in newOptions which would have unintended effects.
    with self.assertRaises(Exception):
      AutomatedTrader(**paperTrading, req='order sell | MSFT@337.57 | ', newOptions={'enabled': True, 'newVal': True})
  def test_failsafe(self):
    # Test failsafe that prevents trading if testMode is enabled when using real money. testMode uses a default cash amount which can cause real problems if not using a paper account.
    with self.assertRaises(Exception):
      AutomatedTrader(**realTrading, req='', newOptions={'enabled': True, 'testMode': True})
  def test_getAccout(self):
    # Verifies a few aspect of the paper account work.
    result = AutomatedTrader(**paperTrading, newOptions={'enabled': False})
    account = result.client.get_account()
    self.assertFalse(account.account_blocked)
    self.assertFalse(account.trade_suspended_by_user)
    self.assertFalse(account.trading_blocked)
    self.assertFalse(account.transfers_blocked)
  def test_data1(self):
    # Testing of the different predefined alert types.
    result = AutomatedTrader(**paperTrading, req='order sell | MSFT@337.57 | ', newOptions={'enabled': False})
    result.setData()
    self.assertEqual(result.data['action'], 'sell')
    self.assertEqual(result.data['position'], None)
    self.assertEqual(result.data['stock'], 'MSFT')
    self.assertEqual(result.data['price'], 337.57)
  def test_data2(self):
    result = AutomatedTrader(**paperTrading, req='order buy | MSFT@337.57 | ', newOptions={'enabled': False})
    result.setData()
    self.assertEqual(result.data['action'], 'buy')
    self.assertEqual(result.data['position'], None)
    self.assertEqual(result.data['stock'], 'MSFT')
    self.assertEqual(result.data['price'], 337.57)
  def test_data3(self):
    result = AutomatedTrader(**paperTrading, req=market['Bear'], newOptions={'enabled': False})
    result.setData()
    self.assertEqual(result.data['action'], 'Bear')
    self.assertEqual(result.data['position'], None)
    self.assertEqual(result.data['stock'], 'CLSK')
    self.assertEqual(result.data['price'], 4.015)
  def test_data4(self):
    result = AutomatedTrader(**paperTrading, req=market['Bull'], newOptions={'enabled': False})
    result.setData()
    self.assertEqual(result.data['action'], 'Bull')
    self.assertEqual(result.data['position'], None)
    self.assertEqual(result.data['stock'], 'CLSK')
    self.assertEqual(result.data['price'], 4.015)
  def test_data5(self):
    result = AutomatedTrader(**paperTrading, req=market['Open'], newOptions={'enabled': False})
    result.setData()
    self.assertEqual(result.data['action'], 'Open')
    self.assertEqual(result.data['position'], 'Long')
    self.assertEqual(result.data['stock'], 'MSFT')
    self.assertEqual(result.data['price'], 327.3)
  def test_data6(self):
    result = AutomatedTrader(**paperTrading, req=market['Long'], newOptions={'enabled': False})
    result.setData()
    self.assertEqual(result.data['action'], 'Close')
    self.assertEqual(result.data['position'], 'Long')
    self.assertEqual(result.data['stock'], 'CLSK')
    self.assertEqual(result.data['price'], 4.015)
  def test_data7(self):
    result = AutomatedTrader(**paperTrading, req=market['Short'], newOptions={'enabled': False})
    result.setData()
    self.assertEqual(result.data['action'], 'Open')
    self.assertEqual(result.data['position'], 'Short')
    self.assertEqual(result.data['stock'], 'CLSK')
    self.assertEqual(result.data['price'], 4.015)
  def test_data8(self):
    result = AutomatedTrader(**paperTrading, req=market['Close'], newOptions={'enabled': False})
    result.setData()
    self.assertEqual(result.data['action'], 'Close')
    self.assertEqual(result.data['position'], 'Short')
    self.assertEqual(result.data['stock'], 'CLSK')
    self.assertEqual(result.data['price'], 4.015)
  # def test_orders(self):
  #   self.result.setOrders()

  # def test_positions(self):
  #   self.result.setPosition()

  # def test_balance(self):
  #   self.result.setBalance()

  # def test_createOrder(self):
  #   self.result.createOrder()
    
if __name__ == '__main__':
  unittest.main()