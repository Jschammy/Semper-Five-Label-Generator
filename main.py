import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

# Database setup
def initialize_database():
    conn = sqlite3.connect("labels.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS LabelHistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serial_number TEXT NOT NULL,
        wood TEXT NOT NULL,
        length TEXT NOT NULL,
        weight TEXT NOT NULL,
        bracelet TEXT NOT NULL,
        wrap TEXT NOT NULL,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    return conn, cursor

# Get the next serial number
def get_next_serial(cursor):
    cursor.execute("SELECT serial_number FROM LabelHistory ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    if result:
        last_serial = result[0]
        prefix = last_serial[:2]  # 'PS'
        num = int(last_serial[2:]) + 1
        return f"{prefix}{num:06d}"  # Ensure 6 digits with leading zeros
    else:
        return "PS000001"  # Start value

# Insert a new label into the database
def insert_label(cursor, conn, serial_number, wood, length, weight, bracelet, wrap):
    cursor.execute("""
    INSERT INTO LabelHistory (serial_number, wood, length, weight, bracelet, wrap)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (serial_number, wood, length, weight, bracelet, wrap))
    conn.commit()

# Generate a single label
def generate_label():
    serial_number = get_next_serial(cursor)
    wood = wood_var.get()
    length = length_var.get()
    weight = weight_var.get()
    bracelet = bracelet_var.get()
    wrap = wrap_var.get()

    if not (wood and length and weight and bracelet and wrap):
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    # Insert into database
    insert_label(cursor, conn, serial_number, wood, length, weight, bracelet, wrap)

    # Display the generated label
    label_output = f"""
    Semper Five LLC.
    S/N: {serial_number}
    Wood: {wood}
    Length: {length}
    Weight: {weight}
    Bracelet: {bracelet}
    Wrap: {wrap}
    """
    messagebox.showinfo("Label Generated", label_output)

# Generate bulk labels
def generate_bulk_labels():
    try:
        quantity = int(bulk_quantity_var.get())
        if quantity <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid positive number for quantity.")
        return

    prefix, next_num = get_next_serial(cursor)[:2], int(get_next_serial(cursor)[2:])

    wood = wood_var.get()
    length = length_var.get()
    weight = weight_var.get()
    bracelet = bracelet_var.get()
    wrap = wrap_var.get()

    if not (wood and length and weight and bracelet and wrap):
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    for i in range(quantity):
        serial_number = f"{prefix}{next_num:06d}"
        insert_label(cursor, conn, serial_number, wood, length, weight, bracelet, wrap)
        next_num += 1

    messagebox.showinfo("Bulk Labels Generated", f"{quantity} labels successfully generated!")

# View historical labels
def view_history():
    cursor.execute("SELECT * FROM LabelHistory")
    rows = cursor.fetchall()
    history_window = Toplevel(root)
    history_window.title("Label History")
    history_window.geometry("600x400")

    # Display historical data in a treeview
    tree = ttk.Treeview(history_window, columns=("ID", "Serial Number", "Wood", "Length", "Weight", "Bracelet", "Wrap", "Date"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Serial Number", text="Serial Number")
    tree.heading("Wood", text="Wood")
    tree.heading("Length", text="Length")
    tree.heading("Weight", text="Weight")
    tree.heading("Bracelet", text="Bracelet")
    tree.heading("Wrap", text="Wrap")
    tree.heading("Date", text="Date Created")

    for row in rows:
        tree.insert("", END, values=row)

    tree.pack(fill=BOTH, expand=True)

# Initialize GUI application
root = Tk()
root.title("Label Generator")
root.geometry("500x400")

# Database initialization
conn, cursor = initialize_database()

# Input fields
wood_var = StringVar()
length_var = StringVar()
weight_var = StringVar()
bracelet_var = StringVar()
wrap_var = StringVar()
bulk_quantity_var = StringVar()

Label(root, text="Wood:").pack()
Entry(root, textvariable=wood_var).pack()

Label(root, text="Length:").pack()
Entry(root, textvariable=length_var).pack()

Label(root, text="Weight:").pack()
Entry(root, textvariable=weight_var).pack()

Label(root, text="Bracelet:").pack()
Entry(root, textvariable=bracelet_var).pack()

Label(root, text="Wrap:").pack()
Entry(root, textvariable=wrap_var).pack()

# Bulk generation input
Label(root, text="Bulk Quantity (optional):").pack()
Entry(root, textvariable=bulk_quantity_var).pack()

# Buttons
Button(root, text="Generate Single Label", command=generate_label).pack(pady=5)
Button(root, text="Generate Bulk Labels", command=generate_bulk_labels).pack(pady=5)
Button(root, text="View Label History", command=view_history).pack(pady=5)

# Start GUI loop
root.mainloop()

conn.close()