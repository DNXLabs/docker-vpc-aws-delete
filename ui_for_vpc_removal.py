import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

def save_credentials_and_run_script():
    aws_account_number = account_number_entry.get("1.0", "end-1c")
    aws_region = region_entry.get()
    role_arn = role_arn_entry.get()
    aws_credentials = credentials_text.get("1.0", "end-1c")

    # Prepare the content for .env.auth file
    content = f"""AWS_ACCOUNT_NUMBER={aws_account_number}
        AWS_REGION={aws_region}
        ROLE_ARN={role_arn}
        {aws_credentials}
        """

    # Write to .env.auth file
    with open(".env.auth", "w") as file:
        file.write(content)

    # Run the script
    try:
        subprocess.run(["python", "remove_vpc.py"], check=True)
        messagebox.showinfo("Success", "The script executed successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Set up the UI
root = tk.Tk()
root.title("AWS VPC Removal Tool")

tk.Label(root, text="AWS Account Number (comma-separated if multiple):").grid(row=0, column=0, sticky="w")
account_number_entry = scrolledtext.ScrolledText(root, height=4, width=50)
account_number_entry.grid(row=1, column=0, padx=5, pady=5)

tk.Label(root, text="AWS Region:").grid(row=2, column=0, sticky="w")
region_entry = tk.Entry(root)
region_entry.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

tk.Label(root, text="Role ARN:").grid(row=4, column=0, sticky="w")
role_arn_entry = tk.Entry(root)
role_arn_entry.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

tk.Label(root, text="AWS Credentials:").grid(row=6, column=0, sticky="w")
credentials_text = scrolledtext.ScrolledText(root, height=6, width=50)
credentials_text.grid(row=7, column=0, padx=5, pady=5)

run_button = tk.Button(root, text="Delete Default VPCs", command=save_credentials_and_run_script)
run_button.grid(row=8, column=0, padx=5, pady=5, sticky="ew")

root.mainloop()
