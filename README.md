# Geedunk2

This is a very messy, first repository for learning and utility. 

I developed a snack bar point of sale computer system for my work that works on the honor system as most snack bars do.
It runs on a Raspberry Pi with a 7 inch touch screen, and allows users to log in to their repective accounts, select items
they wish to purchase, and save their purchase, effectively keeping track of everyone's bill easily, including functionality 
to record payments. Not only does this project include the functionality to represent purchases, but also create, edit, and delete 
user accounts with admin privileges (as well as SHA256 salted encryption for storing the 4 digit login pins), add, edit, and delete
menu items, as well as edit bills, including charging and crediting features. Most functions that require typing have an on-screen keyboardand numpad. Menu items are displayed on the menu in a custom sub-classed picture button format that allows dynamic creation of buttonsfrom the same SQL DB that stores the other app data just supplying arguments of name, price, and relative path to the PNG icon to be displayed on the button, which are all designated in a user-friendly fashion during the menu item creation in the admin options. The menu itself is a field of buttons in the center of the UI, and users can display the different categories of buttons by selecting which types they wish to view from food, drink and snack buttons at the top of the UI, which also function, when subsequentally pressed, to cycle through the pages of buttons in that category, since the design of the program was to be ablew to scale to an arbitrary number of items in each catergory. 
