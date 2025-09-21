# main.py
import tkinter as tk
from app import ChatApplication

def main():
    """تابع اصلی برنامه"""
    root = tk.Tk()
    app = ChatApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    