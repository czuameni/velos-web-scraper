import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel, Text
import webbrowser


DB_NAME = "opolskie_firms.db"

def clean_value(val):
    if val is None or str(val).lower() == "nan":
        return "brak"

    val = str(val)

    val = val.replace("\ue0c8", "")
    val = val.replace("\ue0b0", "")

    val = val.replace("\n", " ")

    val = " ".join(val.split())

    return val.strip()

def load_data():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS firms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        address TEXT,
        city TEXT,
        voivodeship TEXT,
        industry TEXT,
        phone TEXT,
        email TEXT,
        website TEXT
    )
    """)

    conn.commit()

    df = pd.read_sql_query(
        "SELECT id, name, address, city, voivodeship, phone, email, website FROM firms",
        conn
    )

    conn.close()

    df = df.drop(columns=["industry"], errors="ignore")

    return df


def export_csv(df):

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )

    if path:
        df.to_csv(path, index=False)
        messagebox.showinfo("Export", "CSV exported.")


def edit_cell(event):

    selected = table.focus()
    if not selected:
        return

    column = table.identify_column(event.x)
    col_index = int(column.replace("#", "")) - 1

    x, y, width, height = table.bbox(selected, column)

    value = table.item(selected)["values"][col_index]

    entry = tk.Entry(root)
    entry.place(x=x, y=y + 50, width=width)

    entry.insert(0, value)
    entry.focus()

    def save_edit(event):
        new_value = entry.get()

        values = list(table.item(selected)["values"])
        values[col_index] = new_value

        table.item(selected, values=values)
        entry.destroy()

    entry.bind("<Return>", save_edit)


def open_website(event):

    selected = table.focus()
    if not selected:
        return

    values = table.item(selected, "values")

    try:
        website_index = columns.index("website")
        website = values[website_index]

        if website and website.startswith("http"):
            webbrowser.open(website)

    except:
        pass


def copy_email(event):

    selected = table.focus()
    if not selected:
        return

    values = table.item(selected, "values")

    try:
        email_index = columns.index("email")
        email = values[email_index]

        if email and email != "brak":
            root.clipboard_clear()
            root.clipboard_append(email)
            root.update()

    except:
        pass


def refresh_table():

    df = load_data()

    if search_var.get():
        df = df[
            df["name"].str.contains(
                search_var.get(),
                case=False,
                na=False
            )
        ]

    if email_only.get():
        df = df[df["email"].notna()]

    if woj_filter.get():
        df = df[df["voivodeship"] == woj_filter.get()]

    if city_filter.get():
        df = df[df["city"] == city_filter.get()]

    table.delete(*table.get_children())

    for _, row in df.iterrows():

        clean_row = [clean_value(row[col]) for col in df.columns]

        tags = ()
        if row["email"] and str(row["email"]).lower() != "nan":
            tags = ("has_email",)

        table.insert(
            "",
            "end",
            values=clean_row,
            tags=tags
        )

    firms_count = len(df)
    emails_count = df["email"].notna().sum()

    coverage = (
        (emails_count / firms_count) * 100
        if firms_count > 0 else 0
    )

    stats_label.config(
        text=f"Firmy: {firms_count} | Maile: {emails_count} | Coverage: {coverage:.1f}%"
    )


root = tk.Tk()
root.iconbitmap("logo.ico")
root.title("Velos")
root.geometry("1200x600")


filter_frame = tk.Frame(root)
filter_frame.pack(fill="x", padx=10, pady=5)

search_var = tk.StringVar()
email_only = tk.BooleanVar()

tk.Label(filter_frame, text="Województwo").pack(side="left")
woj_filter = ttk.Combobox(filter_frame)
woj_filter.pack(side="left", padx=5)

tk.Label(filter_frame, text="Miasto").pack(side="left")
city_filter = ttk.Combobox(filter_frame)
city_filter.pack(side="left", padx=5)

tk.Label(filter_frame, text="Szukaj").pack(side="left")

search_entry = tk.Entry(filter_frame, textvariable=search_var, width=25)
search_entry.pack(side="left", padx=5)

tk.Checkbutton(
    filter_frame,
    text="Tylko z mailem",
    variable=email_only
).pack(side="left", padx=10)

tk.Button(
    filter_frame,
    text="Filtruj",
    command=refresh_table
).pack(side="left", padx=5)

tk.Button(
    filter_frame,
    text="Eksport CSV",
    command=lambda: export_csv(load_data())
).pack(side="right", padx=5)


df_init = load_data()

columns = list(df_init.columns)

table = ttk.Treeview(
    root,
    columns=columns,
    show="headings"
)

table["displaycolumns"] = columns
table.column("#0", width=0, stretch=False)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=150, anchor="w")

table.pack(fill="both", expand=True)

table.tag_configure("has_email", background="#d0ffd0")

# EVENTS
table.bind("<Double-1>", edit_cell)   # 🔥 NOWE
table.bind("<Button-3>", open_website)
table.bind("<Button-1>", copy_email)


stats_label = tk.Label(root, text="Firmy: 0")
stats_label.pack(pady=5)


woj_filter["values"] = sorted(
    df_init["voivodeship"].dropna().unique()
)

city_filter["values"] = sorted(
    df_init["city"].dropna().unique()
)

refresh_table()

root.mainloop()
