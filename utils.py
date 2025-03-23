import os

class Utility:
    @staticmethod
    def clear_screen():
        """Clears the terminal screen."""
        os.system("cls")

    @staticmethod
    def display_header(title):
        """Displays a formatted header."""
        print("=" * 35)
        print(f"{title.center(35)}")
        print("=" * 35)

    @staticmethod
    def display_subheader(title):
        """Displays a formatted subheader using '-'."""
        print("-" * 35)
        print(f"{title.center(35)}")
        print("-" * 35)

    @staticmethod
    def divider():
        """Prints a divider line."""
        print("-" * 35)

    @staticmethod
    def display_menu(title=None, options=[], use_header=True):
        """
        Displays a menu with options.
        Args:
            title (str): The title of the menu.
            options (list): List of menu options.
            use_header (bool): If True, use `display_header`. If False, use `display_subheader`.
        """
        if title:  # Only display header if title is provided
            if use_header:
                Utility.display_header(title)  # Use header
            else:
                Utility.display_subheader(title)  # Use subheader
        
        for i, option in enumerate(options, 1):
            print(f"[{i}] {option}")
        Utility.divider()
        return input("Select an option: ")