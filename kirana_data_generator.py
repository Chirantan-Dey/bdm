import os
import logging
from datetime import datetime, timedelta
import random
import pandas as pd
from faker import Faker

# Initialize Faker and logging
fake = Faker('en_IN')
logging.basicConfig(level=logging.INFO)

# Configuration
NUM_PRODUCTS = 100
DAILY_TRANSACTIONS_RANGE = (80, 120)
STAFF_COUNT = 5
OPERATING_HOURS = (8, 21)  # 8 AM to 9 PM

def generate_dates(start_date, end_date):
    """Generate business days considering Indian holidays"""
    holidays = [
        datetime(2024, 1, 26),  # Republic Day
        datetime(2024, 3, 25),  # Holi
        datetime(2024, 8, 15),  # Independence Day
        datetime(2024, 10, 2),  # Gandhi Jayanti
        datetime(2024, 10, 12), # Dussehra
        datetime(2024, 11, 1),  # Diwali
    ]
    
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 6 and current_date not in holidays:
            yield current_date
        current_date += timedelta(days=1)

def generate_products(num_products):
    """Generate kirana store product inventory"""
    categories = {
        'Staples': ['Rice', 'Wheat Flour', 'Dal', 'Salt', 'Sugar'],
        'Snacks': ['Biscuits', 'Chips', 'Chocolates', 'Namkeen'],
        'Beverages': ['Tea', 'Coffee', 'Juice', 'Soft Drinks'],
        'Personal Care': ['Soap', 'Shampoo', 'Toothpaste', 'Detergent'],
        'Groceries': ['Oil', 'Spices', 'Pulses', 'Masala']
    }
    
    products = []
    for i in range(num_products):
        category = random.choice(list(categories.keys()))
        base_name = random.choice(categories[category])
        brand = fake.company().split()[0]
        product_name = f"{brand} {base_name}"
        products.append({
            'S.No': i + 1,
            'product_name': product_name,
            'category': category,
            'mrp': round(random.uniform(10, 500), 2),
            'cost_price': round(random.uniform(5, 400), 2),
            'shelf_life_days': random.randint(30, 720)
        })
    return pd.DataFrame(products)

def generate_transactions(start_date, end_date, products):
    """Generate daily sales transactions with realistic patterns"""
    transactions = []
    sno = 1
    
    for date in generate_dates(start_date, end_date):
        is_weekend = date.weekday() >= 5
        base_transactions = random.randint(*DAILY_TRANSACTIONS_RANGE)
        multiplier = 1.3 if is_weekend else 1.0
        daily_transactions = int(base_transactions * multiplier)
        
        for _ in range(daily_transactions):
            product = random.choice(products['product_name'].tolist())
            product_data = products[products['product_name'] == product].iloc[0]
            qty = random.randint(1, 5)
            mrp = product_data['mrp']
            discount = random.choice([0, 0, 0, 0.05, 0.1])
            
            transactions.append({
                'S.No': sno,
                'date': date.strftime('%d-%m-%Y'),
                'time': fake.time_object(end_datetime=None).strftime('%H:%M'),
                'product_name': product,
                'quantity': qty,
                'unit_price': round(mrp * (1 - discount), 2),
                'total_amount': round(mrp * qty * (1 - discount), 2),
                'payment_mode': random.choice(['Cash', 'UPI', 'Credit']),
                'transaction_type': random.choices(
                    ['Walk-in', 'Phone Order', 'Delivery'],
                    weights=[0.7, 0.2, 0.1]
                )[0]
            })
            sno += 1
        
        logging.info(f"Generated {daily_transactions} transactions for {date.strftime('%d-%m-%Y')}")
    
    return pd.DataFrame(transactions)

def generate_expenses(start_date, end_date):
    """Generate business expenses according to their frequency"""
    expenses = []
    sno = 1
    
    # Define expense categories with their frequencies and amount ranges
    expense_categories = {
        'Rent': {'frequency': 'monthly', 'amount': (15000, 20000)},
        'Electricity': {'frequency': 'monthly', 'amount': (3000, 5000)},
        'Water': {'frequency': 'monthly', 'amount': (500, 800)},
        'Staff Salary': {'frequency': 'monthly', 'amount': (8000, 12000)},
        'Transportation': {'frequency': 'daily', 'amount': (100, 300)},
        'Cleaning': {'frequency': 'daily', 'amount': (50, 100)},
        'Maintenance': {'frequency': 'weekly', 'amount': (200, 500)},
        'Internet & Phone': {'frequency': 'monthly', 'amount': (1000, 1500)},
        'Packaging Material': {'frequency': 'weekly', 'amount': (500, 1000)},
        'Miscellaneous': {'frequency': 'daily', 'amount': (100, 300)}
    }
    
    for date in generate_dates(start_date, end_date):
        day_of_month = date.day
        day_of_week = date.weekday()
        
        for category, details in expense_categories.items():
            # Check if expense should be recorded based on frequency
            should_record = (
                details['frequency'] == 'daily' or
                (details['frequency'] == 'weekly' and day_of_week == 0) or
                (details['frequency'] == 'monthly' and day_of_month == 1)
            )
            
            if should_record:
                min_amount, max_amount = details['amount']
                amount = round(random.uniform(min_amount, max_amount), 2)
                
                expenses.append({
                    'S.No': sno,
                    'date': date.strftime('%d-%m-%Y'),
                    'category': category,
                    'amount': amount,
                    'frequency': details['frequency'],
                    'notes': f"Regular {details['frequency']} {category.lower()} expense"
                })
                sno += 1
    
    return pd.DataFrame(expenses)

def main():
    """Generate and save kirana store business data"""
    # Set date range for 3 months
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)
    
    # Create output directory
    output_dir = 'kirana_data'
    os.makedirs(output_dir, exist_ok=True)
    
    logging.info("Generating product catalog...")
    products = generate_products(NUM_PRODUCTS)
    products.to_csv(f"{output_dir}/products.csv", index=False)
    
    logging.info("Generating sales transactions...")
    transactions = generate_transactions(start_date, end_date, products)
    transactions.to_csv(f"{output_dir}/transactions.csv", index=False)
    
    logging.info("Generating expense records...")
    expenses = generate_expenses(start_date, end_date)
    expenses.to_csv(f"{output_dir}/expenses.csv", index=False)
    
    logging.info("Data generation completed successfully!")

if __name__ == "__main__":
    main()
