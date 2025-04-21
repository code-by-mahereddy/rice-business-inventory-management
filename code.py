import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global DataFrames
inventory_df = pd.DataFrame(columns=["ID", "Name", "Price", "Stock"])
sales_df = pd.DataFrame(columns=["SaleID", "RiceID", "BuyerName", "Phone", "Quantity", "TotalPrice", "Timestamp", "Money", "Status"])

# Helper Functions
def add_rice():
    global inventory_df
    name = name_var.get()
    price = price_var.get()
    stock = stock_var.get()
    if not all([name, price, stock]):
        messagebox.showerror("Input Error", "All fields are required.")
        return
    try:
        price = float(price)
        stock = int(stock)
        new_id = inventory_df["ID"].max() + 1 if not inventory_df.empty else 1
        new_row = {"ID": new_id, "Name": name, "Price": price, "Stock": stock}
        inventory_df.loc[len(inventory_df)] = new_row
        messagebox.showinfo("Success", f"Added {name} to inventory.")
        clear_fields([name_var, price_var, stock_var])
        view_inventory()
    except ValueError:
        messagebox.showerror("Input Error", "Invalid price or stock.")

def record_sale():
    global inventory_df, sales_df
    selected_item = inventory_table.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Select a rice type to sell.")
        return
    quantity = sale_quantity_var.get()
    buyer_name = sale_buyer_name_var.get()
    buyer_phone = sale_phone_var.get()
    paid_status = paid_var.get()
    if not quantity:
        messagebox.showerror("Input Error", "Enter quantity.")
        return
    try:
        quantity = int(quantity)
        rice_id = int(inventory_table.item(selected_item, "values")[0])
        rice_row = inventory_df[inventory_df["ID"] == rice_id]
        stock = rice_row["Stock"].values[0]
        if quantity > stock:
            messagebox.showerror("Stock Error", "Insufficient stock.")
            return
        price = rice_row["Price"].values[0]
        total_price = price * quantity
        timestamp = datetime.now()
        buyer_name = buyer_name if buyer_name else "Anonymous"
        buyer_phone = buyer_phone if buyer_phone else "N/A"
        # Update stock and record sale
        inventory_df.loc[inventory_df["ID"] == rice_id, "Stock"] -= quantity
        sale_id = sales_df["SaleID"].max() + 1 if not sales_df.empty else 1
        status = "Paid" if paid_status else "Unpaid"
        new_sale = {
            "SaleID": sale_id,
            "RiceID": rice_id,
            "BuyerName": buyer_name,
            "Phone": buyer_phone,
            "Quantity": quantity,
            "TotalPrice": total_price,
            "Timestamp": timestamp,
            "Money": total_price,  # Money owed by the customer
            "Status": status       # Payment status
        }
        sales_df.loc[len(sales_df)] = new_sale
        messagebox.showinfo("Success", f"Sold {quantity} bags of {rice_row['Name'].values[0]} to {buyer_name}. Total: ₹{total_price} ({status})")
        clear_fields([sale_quantity_var, sale_buyer_name_var, sale_phone_var])
        paid_var.set(False)  # Reset Paid checkbox
        view_inventory()
    except ValueError:
        messagebox.showerror("Input Error", "Invalid quantity.")

def delete_rice():
    global inventory_df
    selected_item = inventory_table.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Select a rice type to delete.")
        return
    rice_id = int(inventory_table.item(selected_item, "values")[0])
    inventory_df = inventory_df[inventory_df["ID"] != rice_id]
    messagebox.showinfo("Success", "Selected rice has been deleted.")
    view_inventory()

def update_price():
    global inventory_df
    selected_item = inventory_table.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Select a rice type to update price.")
        return
    new_price = update_price_var.get()
    if not new_price:
        messagebox.showerror("Input Error", "Enter new price.")
        return
    try:
        new_price = float(new_price)
        rice_id = int(inventory_table.item(selected_item, "values")[0])
        inventory_df.loc[inventory_df["ID"] == rice_id, "Price"] = new_price
        messagebox.showinfo("Success", "Price updated successfully.")
        clear_fields([update_price_var])
        view_inventory()
    except ValueError:
        messagebox.showerror("Input Error", "Invalid price.")

def view_inventory():
    global inventory_df
    for item in inventory_table.get_children():
        inventory_table.delete(item)
    for _, row in inventory_df.iterrows():
        inventory_table.insert("", "end", values=(row["ID"], row["Name"], row["Price"], row["Stock"]))

def view_data():
    global inventory_df, sales_df
    
    data_window = tk.Toplevel(root)
    data_window.title("View Data")
    data_window.geometry("800x600")
    
    notebook = ttk.Notebook(data_window)
    notebook.pack(fill="both", expand=True)
    
    # Inventory Data Tab
    inventory_tab = ttk.Frame(notebook)
    notebook.add(inventory_tab, text="Inventory Data")
    inventory_table_view = create_table(inventory_tab, ["ID", "Name", "Price", "Stock"])
    populate_table(inventory_table_view, inventory_df)
    # Sales Data Tab
    sales_tab = ttk.Frame(notebook)
    notebook.add(sales_tab, text="Sales Data")
    sales_columns = ["SaleID", "RiceID", "BuyerName", "Phone", "Quantity", "TotalPrice", "Timestamp", "Money", "Status"]
    sales_table_view = create_scrollable_table(sales_tab, sales_columns, height=10)  # Reduced height
    populate_table(sales_table_view, sales_df)
    # Analytics Tab
    analytics_tab = ttk.Frame(notebook)
    notebook.add(analytics_tab, text="Analytics")
    create_analytics_page_with_scrollbar(analytics_tab)

def create_table(parent, columns):
    table = ttk.Treeview(parent, columns=columns, show="headings")
    for col in columns:
        table.heading(col, text=col)
    table.pack(fill="both", expand=True)
    return table

def create_scrollable_table(parent, columns, height=10):
    # Create a frame to hold the Treeview and Scrollbars
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True)
    
    # Create Treeview with reduced height
    table = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=100, anchor="center")  # Set fixed column width
    
    # Add vertical scrollbar
    vsb = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    
    # Add horizontal scrollbar
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=table.xview)
    table.configure(xscrollcommand=hsb.set)
    hsb.pack(side="bottom", fill="x")
    
    table.pack(fill="both", expand=True)
    return table

def populate_table(table, data):
    for item in table.get_children():
        table.delete(item)
    for _, row in data.iterrows():
        table.insert("", "end", values=row.tolist())

def clear_fields(variables):
    for var in variables:
        var.set("")

def create_analytics_page_with_scrollbar(parent):
    # Create a Canvas and Scrollbar
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    # Configure the Canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the Canvas and Scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Add a Title Label
    ttk.Label(scrollable_frame, text="Analytics Dashboard", font=("Arial", 16, "bold")).pack(pady=10)

    # Total Sales Revenue Chart
    fig1, ax1 = plt.subplots(figsize=(8, 5))  # Larger chart size
    total_revenue = sales_df["TotalPrice"].sum()
    ax1.bar(["Total Revenue"], [total_revenue], color="green", edgecolor="black")
    ax1.set_title("Total Revenue", fontsize=14)
    ax1.set_ylabel("Revenue (₹)", fontsize=12)
    ax1.tick_params(axis='both', labelsize=10)
    canvas1 = FigureCanvasTkAgg(fig1, master=scrollable_frame)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill="both", expand=True, pady=10)

    # Rice Type vs Revenue Chart
    if not sales_df.empty:
        revenue_by_rice = sales_df.groupby("RiceID")["TotalPrice"].sum().reset_index()
        revenue_by_rice = revenue_by_rice.merge(inventory_df[["ID", "Name"]], left_on="RiceID", right_on="ID", how="left")
        revenue_by_rice = revenue_by_rice[["Name", "TotalPrice"]]
        
        fig2, ax2 = plt.subplots(figsize=(8, 5))  # Larger chart size
        ax2.bar(revenue_by_rice["Name"], revenue_by_rice["TotalPrice"], color="orange", edgecolor="black")
        ax2.set_title("Rice Type vs Revenue", fontsize=14)
        ax2.set_xlabel("Rice Type", fontsize=12)
        ax2.set_ylabel("Revenue (₹)", fontsize=12)
        ax2.tick_params(axis='x', rotation=45, labelsize=10)
        ax2.tick_params(axis='y', labelsize=10)
        canvas2 = FigureCanvasTkAgg(fig2, master=scrollable_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, pady=10)

# GUI Setup
root = tk.Tk()
root.title("Rice Business App")
root.geometry("800x600")

# Add Rice Frame
add_frame = ttk.LabelFrame(root, text="Add Rice to Inventory")
add_frame.pack(fill="x", padx=10, pady=5)
name_var = tk.StringVar()
price_var = tk.StringVar()
stock_var = tk.StringVar()
ttk.Label(add_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
ttk.Entry(add_frame, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)
ttk.Label(add_frame, text="Price/bag:").grid(row=0, column=2, padx=5, pady=5)
ttk.Entry(add_frame, textvariable=price_var).grid(row=0, column=3, padx=5, pady=5)
ttk.Label(add_frame, text="Stock (bags):").grid(row=0, column=4, padx=5, pady=5)
ttk.Entry(add_frame, textvariable=stock_var).grid(row=0, column=5, padx=5, pady=5)
ttk.Button(add_frame, text="Add Rice", command=add_rice).grid(row=0, column=6, padx=5, pady=5)

# Inventory Frame
inventory_frame = ttk.LabelFrame(root, text="Rice Inventory")
inventory_frame.pack(fill="both", expand=True, padx=10, pady=5)
inventory_table = create_table(inventory_frame, ["ID", "Name", "Price", "Stock"])

# Sales Frame
sales_frame = ttk.LabelFrame(root, text="Record a Sale")
sales_frame.pack(fill="x", padx=10, pady=5)
sale_quantity_var = tk.StringVar()
sale_buyer_name_var = tk.StringVar()
sale_phone_var = tk.StringVar()
paid_var = tk.BooleanVar(value=False)
ttk.Label(sales_frame, text="Quantity (bags):").grid(row=0, column=0, padx=5, pady=5)
ttk.Entry(sales_frame, textvariable=sale_quantity_var).grid(row=0, column=1, padx=5, pady=5)
ttk.Label(sales_frame, text="Buyer Name (Optional):").grid(row=0, column=2, padx=5, pady=5)
ttk.Entry(sales_frame, textvariable=sale_buyer_name_var).grid(row=0, column=3, padx=5, pady=5)
ttk.Label(sales_frame, text="Phone (Optional):").grid(row=0, column=4, padx=5, pady=5)
ttk.Entry(sales_frame, textvariable=sale_phone_var).grid(row=0, column=5, padx=5, pady=5)
ttk.Checkbutton(sales_frame, text="Paid", variable=paid_var).grid(row=0, column=6, padx=5, pady=5)
ttk.Button(sales_frame, text="Record Sale", command=record_sale).grid(row=0, column=7, padx=5, pady=5)

# Update/Delete Frame
update_delete_frame = ttk.LabelFrame(root, text="Update/Delete Rice")
update_delete_frame.pack(fill="x", padx=10, pady=5)
update_price_var = tk.StringVar()
ttk.Label(update_delete_frame, text="New Price/bag:").grid(row=0, column=0, padx=5, pady=5)
ttk.Entry(update_delete_frame, textvariable=update_price_var).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(update_delete_frame, text="Update Price", command=update_price).grid(row=0, column=2, padx=5, pady=5)
ttk.Button(update_delete_frame, text="Delete Rice", command=delete_rice).grid(row=0, column=3, padx=5, pady=5)

# Navigation Buttons
ttk.Button(root, text="View Data", command=view_data).pack(pady=5)

# Run App
root.mainloop()