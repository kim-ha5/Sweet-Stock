# SweetStock

This is a bakery management and inventory system intended for small bakeries to keep track of their inventory and orders as well as provide a platform for customers to order goods. Owners (admins) can keep track of their inventory as well as monitor order fulfillment progression. Employees have a central system to view all of the open orders, stock, and recipes. Customers can browse available products and place orders.

## DBMS
The database for this project is created with sqlite

## Requirements

- Python 3.10 or newer
- Node.js

## Setup

Follow the following steps to setup the dependencies:

### macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Windows (PowerShell):
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

If PowerShell blocks the activation script, use Command Prompt instead:
```bat
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r backend/requirements.txt
```


Recreate the database from `schema.sql` and `insert_data.sql`:

```bash
flask --app backend.app init-db
```

The backend uses `bakery_management.db`

## Run

### Backend
Start the backend in one terminal from the root folder:
```bash
flask --app backend.app run --debug
```

### Frontend

Start the frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Sample Accounts

1. Customer

    Username: athomas@example.com
    Password: pass1

2. Employee

    Username: drew.smith@example.com
    Password: pass7

3. Admin

    Username: robin.garcia@example.com
    Password: pass8


## Operations

1. Search or Browse Data:

    Customers can search for a specific product in the search bar under the Shop tab. This is defined under the products route of the backend API.

2. Display Related Data:

    Employees and admins can view the ingredients needed for each product. The Products, Recipes, Recipe_Indgredients, and Ingredients tables are joined to do so. This is defined under the `recipes` route of the backend API.

3. Add Data:

    Customer and Employee accounts can be created on the initial login screen. This is defined under the `auth/register` route of the backend API

4. Update or Delete Data:

    Admin users can update the price of products. This is defined under one of the products routes in the backend API.

5. Summary or Report:

    Employees and admins can view summaries of sales and order under the Reports tab. This includes total sales amount and the number of orders in each status. This is defined in the backend API under multiple routes under the reports route.

6. Additional Operation:

    When a customer places an order, multiple tables are updated. New records are added to the Orders and Order_Items tables. Recipes and Ingredients are joined to update the ingredients stock amount accounting for each item in the order.

## Limitations
- Customers can't edit their information directly
- There isn't an account deletion that the user can request within the application
- The availability of a product is dependent on ingredient stock but the user doesn't know that until they go to place the order and get an error message
