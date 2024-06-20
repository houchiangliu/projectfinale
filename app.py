from flask import Flask, render_template, request, redirect, url_for, flash, session ,jsonify

import pyodbc
import datetime

import matplotlib
matplotlib.use('agg')  # Set non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'hou'

# Database connection configuration
server = 'case2projectsvr.database.windows.net'
driver='ODBC Driver 17 for SQL Server'
database='Inventory_DB'
username = 'houchiangliu123'  # Add your SQL Server username
password = 'Kolkata@1234'  # Add your SQL Server password

# Function to establish database connection
def connect_to_database():
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    return pyodbc.connect(connection_string)

@app.route('/')
def home():
    if 'Manager_email' in session:
        return render_template('home.html', Manager_email=session['Manager_email'])
    else:
        return render_template('home.html')

# Route for sign-in page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Manager_email = request.form['Manager_email']
        Manager_pass = request.form['Manager_pass']

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute('SELECT Manager_email, Manager_pass FROM Inventory_Manager WHERE Manager_email = ? AND Manager_pass = ?', (Manager_email, Manager_pass))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if user:
            session['Manager_email'] = user[0]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid Credentials')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'Manager_email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        Manager_name = request.form['Manager_name']
        Manager_email = request.form['Manager_email']
        Manager_pass = request.form['Manager_pass']

        conn = connect_to_database()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO Inventory_Manager (Manager_name, Manager_email, Manager_pass, Created_at, Updated_at) VALUES (?, ?, ?, ?, ?)', 
                           (Manager_name, Manager_email, Manager_pass, datetime.date.today(), datetime.date.today()))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
        except Exception as e:
            return f'Error: {str(e)}'

    return render_template('register.html')

@app.route('/back')
def back():
    if 'Manager_email' in session:
        return render_template('home.html', Manager_email=session['Manager_email'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('Manager_email', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/Orders_Table', methods=['GET', 'POST'])
def Orders_Table():
    if request.method == 'POST':
        try:
            Order_id = request.form.get('Order_id')
            Product_id = request.form.get('Product_id')
            Quantity = request.form.get('Quantity')
            Date = datetime.date.today()
            Created_at = datetime.date.today()
            Updated_at = datetime.date.today()

            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Orders_Table (Product_id, Quantity, Date, Created_at, Updated_at) VALUES (?, ?, ?, ?, ?)', 
                           (Product_id, Quantity, Date, Created_at, Updated_at))
            
            conn.commit()
            cursor.close()
            conn.close()

            flash('Order added successfully!', 'success')
            return redirect(url_for('Orders_Table'))
        except pyodbc.IntegrityError as e:
            if 'FOREIGN KEY constraint' in str(e):
                flash('Product ID does not exist. Please enter a valid Product ID.', 'error')
            else:
                flash('An error occurred. Please try again.', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        
    return render_template('dashboard.html')


@app.route('/Stockmovement', methods=['GET','POST'])
def Stockmovement():
    if request.method == 'POST':
        try:
            Product_id = request.form.get('Product_id')
            Movement_date = datetime.date.today()
            Quantity_changed = request.form.get('Quantity_changed')
            Reason = request.form.get('Reason')
            Created_at = datetime.date.today()
            Updated_at = datetime.date.today()

            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Stock_Movement ( Product_id, Movement_date, Quantity_changed, Reason, Created_at, Updated_at) VALUES ( ?, ?, ?, ?, ?, ?)', 
                           ( Product_id, Movement_date, Quantity_changed, Reason, Created_at, Updated_at))
            
            conn.commit()
            cursor.close()
            conn.close()

            flash('Stock movement recorded successfully!', 'success')
            return redirect(url_for('Stockmovement'))
        except pyodbc.IntegrityError as e:
            if 'FOREIGN KEY constraint' in str(e):
                flash('Product ID does not exist. Please enter a valid Product ID.', 'error')
            else:
                flash('An error occurred. Please try again.', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('dashboard.html')

def is_product_id_valid(product_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('SELECT Product_id FROM Inventory_Table WHERE Product_id = ?', (product_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row is not None

@app.route('/Product_Table', methods=['GET', 'POST'])
def Product_Table():
    if request.method == 'POST':
        try:
            Product_id = request.form.get('Product_id')
            Product_name = request.form.get('Product_name')
            Product_category = request.form.get('Product_category')
            Supplier_id = request.form.get('Supplier_id')
            quantity = request.form.get('quantity')
            reorder_level = 1
            reason = 'Restock'
            Movement_date = datetime.date.today()
            Created_at = datetime.date.today()
            Updated_at = datetime.date.today()

            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Product_Table (Product_id, Product_name, Product_category, Supplier_id, Created_at, Updated_at) VALUES (?, ?, ?, ?, ?, ?)', 
                           (Product_id, Product_name, Product_category, Supplier_id, Created_at, Updated_at))
            cursor.execute('INSERT INTO Inventory_Table (Product_id, Stock_quantity, Reorder_level, Created_at, Updated_at) VALUES (?, ?, ?, ?, ?)', 
                           (Product_id, quantity, reorder_level, Created_at, Updated_at))
            cursor.execute('INSERT INTO Stock_Movement (Product_id, Movement_date, Quantity_changed, Reason, Created_at, Updated_at) VALUES (?, ?, ?, ?, ?, ?)', 
                           (Product_id, Movement_date, quantity, reason, Created_at, Updated_at))
            
            conn.commit()
            cursor.close()
            conn.close()

            flash('Product added successfully!', 'success')
            return redirect(url_for('Product_Table'))
        except pyodbc.IntegrityError as e:
            if 'FOREIGN KEY constraint' in str(e):
                flash('Supplier ID does not exist. Please enter a valid Supplier ID.', 'error')
            else:
                flash('An error occurred. Please try again.', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('dashboard.html')

@app.route('/Supplier_Table', methods=['GET', 'POST'])
def Supplier_Table():
    if request.method == 'POST':
        try:
            Supplier_id = request.form.get('Supplier_id')
            Supplier_name = request.form.get('Supplier_name')
            Location = request.form.get('Location')
            Created_at = datetime.date.today()
            Updated_at = datetime.date.today()

            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Supplier_Table (Supplier_id, Supplier_name, Location, Created_at, Updated_at) VALUES (?, ?, ?, ?, ?)', 
                           (Supplier_id, Supplier_name, Location, Created_at, Updated_at))
            
            conn.commit()
            cursor.close()
            conn.close()


            flash('Supplier added successfully!', 'success')
            return redirect(url_for('Supplier_Table'))
        
        except pyodbc.IntegrityError as e:
            if 'Violation of PRIMARY KEY constraint' in str(e):
                flash('Supplier ID already exists. Please enter a different Supplier ID.', 'error')
            else:
                flash('An error occurred. Please try again.', 'error')
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('dashboard.html')



@app.route('/View_Inventory_Table', methods=['GET', 'POST'])
def View_Inventory_Table():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        Product_id=request.form.get("Product_id")
        cursor.execute('SELECT * FROM Inventory_Table WHERE Product_id=?',Product_id)
        Inventory = cursor.fetchall()
        Inventory_data=[{'Inventory_id': row[0], 'Product_id': row[1], 'Stock_quantity': row[2], 'Reorder_level': row[3], 'Created_at': row[4], 'Updated_at': row[5]} for row in Inventory]
        cursor.close()
        conn.close()
        return render_template('View_Inventory_Table.html', data=Inventory_data)
    except Exception as e:
        return f'Error: {str(e)}'
   
@app.route('/View_Inventory_Table_All', methods=['GET', 'POST'])
def View_Inventory_Table_All():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Inventory_Table')
        Inventory = cursor.fetchall()
        Inventory_data=[{'Inventory_id': row[0], 'Product_id': row[1], 'Stock_quantity': row[2], 'Reorder_level': row[3], 'Created_at': row[4], 'Updated_at': row[5]} for row in Inventory]
        cursor.close()
        conn.close()
        return render_template('View_Inventory_Table_All.html', data=Inventory_data)
    except Exception as e:
        return f'Error: {str(e)}'
   
@app.route('/View_Supplier_Table', methods=['GET', 'POST'])
def View_Supplier_Table():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Supplier_Table')
        Supplier = cursor.fetchall()
        Supplier_data=[{'Supplier_id': row[0], 'Supplier_name': row[1], 'Location': row[2], 'Created_at': row[3], 'Updated_at': row[4]} for row in Supplier]
        cursor.close()
        conn.close()
        return render_template('View_Supplier_Table.html', data=Supplier_data)
    except Exception as e:
        return f'Error: {str(e)}'
   
@app.route('/View_Product_Table', methods=['GET', 'POST'])
def View_Product_Table():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Product_Table')
        Product = cursor.fetchall()
        Product_data=[{'Product_id': row[0], 'Product_name': row[1], 'Product_category': row[2], 'Supplier_id': row[3], 'Created_at': row[4], 'Updated_at': row[5]} for row in Product]
        cursor.close()
        conn.close()
        return render_template('View_Product_Table.html', data=Product_data)
    except Exception as e:
        return f'Error: {str(e)}'
 
 
@app.route('/View_Orders_Table', methods=['GET', 'POST'])
def View_Orders_Table():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Orders_Table')
        Orders = cursor.fetchall()
        Orders_data=[{'Orders_id': row[0], 'Product_id': row[1], 'Quantity': row[2], 'Date': row[3], 'Created_at': row[4], 'Updated_at': row[5]} for row in Orders]
        cursor.close()
        conn.close()
        return render_template('View_Orders_Table.html', data=Orders_data)
    except Exception as e:
        return f'Error: {str(e)}'
   
 
@app.route('/View_Stock_Movement', methods=['GET', 'POST'])
def View_Stock_Movement():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Stock_Movement')
        Stock = cursor.fetchall()
        Stock_data=[{'Movement_id': row[0], 'Product_id': row[1], 'Movement_date': row[2], 'Quantity_changed': row[3], 'Reason': row[4], 'Created_at': row[5], 'Updated_at': row[6]} for row in Stock]
        cursor.close()
        conn.close()
        return render_template('View_Stock_Movement.html', data=Stock_data)
    except Exception as e:
        return f'Error: {str(e)}'
    

@app.route('/view')
def Home():
    return render_template('viewmain.html')

@app.route('/low_stock_data')
def low_stock_data():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
 
        query = 'SELECT Inventory_id, Product_id, Stock_quantity, Reorder_level FROM Inventory_Table WHERE Stock_quantity < 20'
        cursor.execute(query)
        low_stock_items = cursor.fetchall()
 
        low_stock_list = []
        for item in low_stock_items:
            low_stock_list.append({
                'Inventory_id': item.Inventory_id,
                'Product_id': item.Product_id,
                'Stock_quantity': item.Stock_quantity,
                'Reorder_level': item.Reorder_level
            })
 
        cursor.close()
        conn.close()
 
        return jsonify(low_stock_list)
    except Exception as e:
        return jsonify({'error': str(e)})
 
@app.route('/top_sell_products')
def top_sell_products():
    try:
        num_of_row = request.args.get("num_of_row", type=int)
        conn = connect_to_database()
        cursor = conn.cursor()
 
        query = f'''SELECT TOP {num_of_row} p.Product_id, p.Product_name, SUM(sm.Quantity_changed) AS total_sales
                    FROM Stock_Movement sm
                    JOIN Product_Table p ON sm.Product_id = p.Product_id
                    WHERE sm.reason = 'Sale'
                    GROUP BY p.Product_id, p.Product_name
                    ORDER BY total_sales ASC'''
        cursor.execute(query)
        product_list = []
        for row in cursor.fetchall():
            product_list.append({
                "Product_id": row.Product_id,
                "Product_name": row.Product_name,
                "total_sales": -row.total_sales
            })
 
        cursor.close()
        conn.close()
 
        return jsonify(product_list)
    except Exception as e:
        return jsonify({'error': str(e)})
 
@app.route('/get_sales_data', methods=['GET'])
def get_sales_data():
    try:
        product_id = request.args.get('product_id')
        year = request.args.get('year')
 
        # Query database for seasonal sales data based on product_id and year
        cnxn = connect_to_database()
        cursor = cnxn.cursor()
        query = f'''
            SELECT
                CASE
                    WHEN DATEPART(month, Movement_date) IN (12, 1, 2) THEN 'Winter'
                    WHEN DATEPART(month, Movement_date) IN (3, 4, 5) THEN 'Spring'
                    WHEN DATEPART(month, Movement_date) IN (6, 7, 8) THEN 'Summer'
                    WHEN DATEPART(month, Movement_date) IN (9, 10, 11) THEN 'Autumn'
                END AS season,
                SUM(Quantity_changed) AS total_sales
            FROM Stock_Movement
            WHERE Product_id = {product_id} AND YEAR(Movement_date) = {year} AND Reason = 'Sale'
            GROUP BY
                CASE
                    WHEN DATEPART(month, Movement_date) IN (12, 1, 2) THEN 'Winter'
                    WHEN DATEPART(month, Movement_date) IN (3, 4, 5) THEN 'Spring'
                    WHEN DATEPART(month, Movement_date) IN (6, 7, 8) THEN 'Summer'
                    WHEN DATEPART(month, Movement_date) IN (9, 10, 11) THEN 'Autumn'
                END
        '''
        cursor.execute(query)
        sales_data = cursor.fetchall()
        cursor.close()
        cnxn.close()
 
        # Prepare data for plotting
        seasons = ['Winter', 'Spring', 'Summer', 'Autumn']
        total_sales = [0, 0, 0, 0]  # Initialize sales for each season
 
        for row in sales_data:
            if row.season in seasons:
                index = seasons.index(row.season)
                total_sales[index] += -row.total_sales
 
        # Generate plot
        plt.figure(figsize=(10, 6))
        plt.bar(seasons, total_sales, color='blue')
        plt.xlabel('Season')
        plt.ylabel('Total Sales')
        plt.title(f'Seasonal Sales Data for Product ID {product_id} in Year {year}')
 
        # Save plot to a BytesIO object
        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)
        plot_img = base64.b64encode(image_stream.getvalue()).decode('utf-8')
        plt.close()
 
        return jsonify({'plot_img': plot_img})
 
    except Exception as e:
        return jsonify({'error': str(e)})
 
@app.route('/insights')
def index():
    return render_template('trend.html')

@app.route('/raise_ticket')
def raise_ticket():
    return render_template('raise_ticket.html')
 
@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    issue = request.form['issue']
    issue_date = datetime.date.today()
   
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
       
        query = 'INSERT INTO Tickets (Issue, Issue_Date) VALUES (?, ?)'
        cursor.execute(query, (issue, issue_date))
        conn.commit()
       
        cursor.close()
        conn.close()
       
        return redirect(url_for('success'))
    except Exception as e:
        return f'An error occurred: {e}'
 
@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088, debug=True)
