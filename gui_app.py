import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel, Text
import webbrowser


DB_NAME = "opolskie_firms.db"


# ==============================
# LOAD DATA
# ==============================

def load_data():

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        "SELECT * FROM firms",
        conn
    )

    conn.close()

    return df


# ==============================
# EXPORT CSV
# ==============================

def export_csv(df):

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )

    if path:
        df.to_csv(path, index=False)
        messagebox.showinfo("Export", "CSV exported.")


# ==============================
# SHOW DETAILS POPUP
# ==============================

def show_details(event):

    selected = table.focus()

    if not selected:
        return

    values = table.item(selected, "values")

    details = ""

    for col, val in zip(columns, values):
        details += f"{col}: {val}\n\n"

    popup = Toplevel(root)
    popup.title("Szczegóły firmy")
    popup.geometry("600x400")

    text = Text(popup, wrap="word")
    text.insert("1.0", details)
    text.config(state="disabled")
    text.pack(fill="both", expand=True)


# ==============================
# OPEN WEBSITE (PPM)
# ==============================

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


# ==============================
# COPY EMAIL TO CLIPBOARD
# ==============================

def copy_email(event):

    selected = table.focus()

    if not selected:
        return

    values = table.item(selected, "values")

    try:
        email_index = columns.index("email")
        email = values[email_index]

        if email:
            root.clipboard_clear()
            root.clipboard_append(email)
            root.update()

            print(f"Copied: {email}")

    except:
        pass


# ==============================
# REFRESH TABLE
# ==============================

def refresh_table():

    df = load_data()

    # SEARCH
    if search_var.get():
        df = df[
            df["name"].str.contains(
                search_var.get(),
                case=False,
                na=False
            )
        ]

    # EMAIL ONLY
    if email_only.get():
        df = df[df["email"].notna()]

    # WOJ FILTER
    if woj_filter.get():
        df = df[df["voivodeship"] == woj_filter.get()]

    # CITY FILTER
    if city_filter.get():
        df = df[df["city"] == city_filter.get()]

    table.delete(*table.get_children())

    for _, row in df.iterrows():

        tags = ()

        if pd.notna(row["email"]):
            tags = ("has_email",)

        table.insert(
            "",
            "end",
            values=list(row),
            tags=tags
        )

    # ==============================
    # COVERAGE STATS (TU MUSI BYĆ)
    # ==============================

    firms_count = len(df)

    emails_count = df["email"].notna().sum()

    coverage = (
        (emails_count / firms_count) * 100
        if firms_count > 0 else 0
    )

    stats_label.config(
        text=f"Firmy: {firms_count} | Maile: {emails_count} | Coverage: {coverage:.1f}%"
    )


# ==============================
# GUI ROOT
# ==============================

root = tk.Tk()

root.iconbitmap("logo.ico")

root.title("Velos")
root.geometry("1200x600")


# ==============================
# FILTER FRAME
# ==============================

filter_frame = tk.Frame(root)
filter_frame.pack(fill="x", padx=10, pady=5)


# SEARCH VAR (MUSI BYĆ TU)
search_var = tk.StringVar()
email_only = tk.BooleanVar()


# WOJ
tk.Label(filter_frame, text="Województwo").pack(side="left")

woj_filter = ttk.Combobox(filter_frame)
woj_filter.pack(side="left", padx=5)


# CITY
tk.Label(filter_frame, text="Miasto").pack(side="left")

city_filter = ttk.Combobox(filter_frame)
city_filter.pack(side="left", padx=5)


# SEARCH
tk.Label(filter_frame, text="Szukaj").pack(side="left")

search_entry = tk.Entry(
    filter_frame,
    textvariable=search_var,
    width=25
)

search_entry.pack(side="left", padx=5)


# EMAIL ONLY
tk.Checkbutton(
    filter_frame,
    text="Tylko z mailem",
    variable=email_only
).pack(side="left", padx=10)


# FILTER BUTTON
tk.Button(
    filter_frame,
    text="Filtruj",
    command=refresh_table
).pack(side="left", padx=5)


# EXPORT
tk.Button(
    filter_frame,
    text="Eksport CSV",
    command=lambda: export_csv(load_data())
).pack(side="right", padx=5)


# ==============================
# TABLE
# ==============================

df_init = load_data()

columns = list(df_init.columns)

table = ttk.Treeview(
    root,
    columns=columns,
    show="headings"
)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=140)

table.pack(fill="both", expand=True)

# COLOR EMAIL ROWS
table.tag_configure(
    "has_email",
    background="#d0ffd0"
)

# EVENTS
table.bind("<Double-1>", show_details)
table.bind("<Button-3>", open_website)
table.bind("<Button-1>", copy_email)


# ==============================
# STATS
# ==============================

stats_label = tk.Label(root, text="Firmy: 0")
stats_label.pack(pady=5)


# ==============================
# INIT DATA
# ==============================

woj_filter["values"] = sorted(
    df_init["voivodeship"].dropna().unique()
)

city_filter["values"] = sorted(
    df_init["city"].dropna().unique()
)

refresh_table()


root.mainloop()
