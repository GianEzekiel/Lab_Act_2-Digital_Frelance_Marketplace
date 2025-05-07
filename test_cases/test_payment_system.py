import unittest
from unittest.mock import patch, MagicMock
import os
import sys


# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from payment_system import Wallet, Payment  # assuming your code is in wallet.py


class TestWalletFunctionality(unittest.TestCase):


    @patch('payment_system.sqlite3.connect')
    def setUp(self, mock_connect):
        # Mock the database connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        mock_connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.mock_cursor.fetchone.return_value = (1000.0,)  # Mock initial balance
       
        self.wallet = Wallet(user_id=1)  # Initialize with mocked balance


    def test_get_balance_from_db(self):
        self.assertEqual(self.wallet.balance, 1000.0)
        self.mock_cursor.execute.assert_called_with("SELECT balance FROM wallet WHERE user_id = ?", (1,))


    @patch('payment_system.sqlite3.connect')
    def test_update_balance_positive(self, mock_connect):
        mock_connect.return_value = self.mock_conn
       
        self.wallet.update_balance(500.0)
        self.mock_cursor.execute.assert_called_with(
            "UPDATE wallet SET balance = balance + ? WHERE user_id = ?", (500.0, 1)
        )
        self.mock_conn.commit.assert_called_once()


    @patch('payment_system.sqlite3.connect')
    def test_update_balance_negative(self, mock_connect):
        mock_connect.return_value = self.mock_conn
       
        self.wallet.update_balance(-300.0)
        self.mock_cursor.execute.assert_called_with(
            "UPDATE wallet SET balance = balance + ? WHERE user_id = ?", (-300.0, 1)
        )
        self.mock_conn.commit.assert_called_once()


    @patch('payment_system.Wallet.update_balance')
    def test_deposit_valid_amount(self, mock_update_balance):
        self.wallet.deposit(200)
        mock_update_balance.assert_called_with(200)


    @patch('payment_system.Wallet.update_balance')
    def test_deposit_invalid_amount(self, mock_update_balance):
        self.wallet.deposit(-50)
        mock_update_balance.assert_not_called()


    @patch('payment_system.Wallet.update_balance')
    def test_withdraw_valid_amount(self, mock_update_balance):
        self.wallet.withdraw(300)
        mock_update_balance.assert_called_with(-300)


    @patch('payment_system.Wallet.update_balance')
    def test_withdraw_insufficient_funds(self, mock_update_balance):
        self.wallet.balance = 100  # set low balance
        self.wallet.withdraw(200)
        mock_update_balance.assert_not_called()


class TestPaymentFunctionality(unittest.TestCase):


    @patch('payment_system.Wallet.get_balance_from_db', return_value=1000)
    @patch('payment_system.Wallet.withdraw')
    @patch('payment_system.Wallet.deposit')
    def test_release_payment_successful(self, mock_deposit, mock_withdraw, mock_get_balance):
        employer_wallet = Wallet(user_id=1)
        freelancer_wallet = Wallet(user_id=2)
        payment = Payment(amount=500, milestone="Website Design")
       
        payment.release_payment(employer_wallet, freelancer_wallet)
       
        mock_withdraw.assert_called_with(500)
        mock_deposit.assert_called_with(500)
        self.assertEqual(payment.status, "Paid")


    @patch('payment_system.Wallet.get_balance_from_db', return_value=400)
    @patch('payment_system.Wallet.withdraw')
    @patch('payment_system.Wallet.deposit')
    def test_release_payment_insufficient_funds(self, mock_deposit, mock_withdraw, mock_get_balance):
        employer_wallet = Wallet(user_id=1)
        freelancer_wallet = Wallet(user_id=2)
        payment = Payment(amount=500, milestone="App Development")
       
        payment.release_payment(employer_wallet, freelancer_wallet)
       
        mock_withdraw.assert_not_called()
        mock_deposit.assert_not_called()
        self.assertEqual(payment.status, "Pending")


if __name__ == "__main__":
    unittest.main()