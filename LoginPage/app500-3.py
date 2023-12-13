import streamlit as st
import requests
import html  # Importing the html library for decoding HTML entities
import time
import random
from account_helper import register_user, is_login_successful, query_all_table, query_delete, query_add  # Import custom library
from bs4 import BeautifulSoup

# ReCookify

# This Streamlit  app is designed to be a comprehensive kitchen management tool. It integrates with the Spoonacular API to provide recipe recommendations based on user-selected ingredients from their inventory. The app consists of multiple functionalities:

# 1. Custom CSS Integration: Enhances the visual aesthetics of the app using a local CSS file
# 2. Spoonacular API Integration: Utilizes the Spoonacular API to fetch recipes based on ingredients and detailed recipe information
# 3. Session State Management: Manages user data across different sessions, specifically for inventory and shopping list
# 4. Streamlit Interface: Uses Streamlit's framework for creating an interactive web application. It includes functionalities such as adding items to inventory, searching for recipes, and managing a shopping list
# 5. Error Handling: Implements error handling for API requests to ensure stability and user feedback on failures

# Overall, the app serves as a convenient platform for users to manage their kitchen inventory, discover new recipes, and efficiently plan their shopping activities – especially for students


# First we need to initialize the session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["uname"] = None

# Here you can define the login page
def show_login_page():
    st.title("Login")
    ###############################
    # Register & Login logic start
    ###############################
    # Define the text fields to enter username & password
    uname = st.text_input("Username", key="username_input")
    psword = st.text_input("Password", type="password", key="password_input")
    ###############################
    # Register logic
    ###############################
    # If the register button is pressed, the following code is executed
    if st.button("Register"):
        # We query PSQL to try to register a new user
        results = register_user(uname, psword)
        # Depending on the result from PSQL, we raise various errors or proceed with login
        if results == "fill_out_all":
            st.error("Enter a username and a password")
        elif results[0] == "already_exists":
            st.error("This username already exists. Please enter another one.")
        elif results[0] == "user_registered":
            st.session_state["logged_in"] = True
            st.session_state["uname"] = results[1]
            st.success("Registered successfully")
            time.sleep(3)
            st.rerun()  # st.experimental_rerun()
    ###############################
    # Login logic
    ###############################
    # If the login button is pressed, the following code is executed
    if st.button("Login"):
        # We query PSQL to check whether the username and password match
        results = is_login_successful(uname, psword)
        # Depending on the result from PSQL, we raise various errors or proceed with login
        if results == "fill_out_all":
            st.error("Enter your username and your password")
        elif results[0] == "username_not_found":
            st.error("Incorrect username")
        elif results[0] == "wrong_password":
            st.error("Incorrect password")
        elif results[0] == "correct_password":
            st.session_state["logged_in"] = True
            st.session_state["uname"] = results[1]
            st.success("Registered successfully")
            st.rerun()  # st.experimental_rerun()
    ###############################
    # Register & Login logic end
    ###############################
# Here you can define your main page
def show_main_app():
    st.title("Main Application")
    ###############################
    # Logout logic start
    ###############################
    # If the logout button is pressed, the following code is executed
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state["uname"] = None
        st.experimental_rerun()  # Use st.experimental_rerun() instead of st.rerun()
    ###############################
    # Logout logic end
    ###############################
    ###############################
    # Stored List logic start
    ###############################
    # Leverage the user variable from login
    user = st.session_state["uname"]
    # Make a personalized title
    st.title(f"{user}'s inventory")
    ###############################
    # Add items start
    ###############################
    # Check if the 'add_button_clicked' key exists in the session_state, if not, initialize it
    if "new_item" not in st.session_state:
        st.session_state["new_item"] = ""
    itemname = st.text_input("Item")
    # Only set the flag when the button is clicked
    if st.button("Add", key=st.session_state["new_item"]) and itemname != "":
        # Add the selected item for the user
        query_add(user, itemname)
        st.session_state["new_item"] = random.random()  # prevents a stupid streamlit bug (/feature)
        st.rerun()  # st.experimental_rerun()
    ###############################
    # Add items end
    ###############################
    ###############################
    # Display the whole list start
    ###############################
    # We query PSQL for all items stored for this user
    result = query_all_table(user)
    # We loop over all results and display them in a table
    items = []
    for item_index, item in enumerate(result[0]):
        items.append([item[2], result[1][item_index + 1]])
    # Create a table with buttons
    for item, item_index in items:
        col1, col2 = st.columns([3, 2])
        with col1:
            st.text(item)
        with col2:
            if st.button("Delete", key=item_index):
                # Delete the selected item from the user
                query_delete(item_index)
                st.rerun()  # st.experimental_rerun()
    ###############################
    # Display the whole list end
    ###############################
    ###############################
    # Stored List logic end
    ###############################

# Custom CSS to improve the look and feel of the app
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call the function to apply custom CSS
local_css("style.css")

# Function to get recipe recommendations from the Spoonacular API
def get_recipe_recommendations(api_key, ingredients):
    endpoint = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": api_key,
        "ingredients": ",".join(ingredients),
        "number": 3  # Number of recipes to retrieve
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return f"Error: {err}"

# Function to get detailed recipe information
def get_recipe_details(api_key, recipe_id):
    endpoint = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": api_key}
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return f"Error: {err}"

# Initialize session state for inventory and shopping list
if 'inventory' not in st.session_state:
    st.session_state['inventory'] = {}
if 'shopping_list' not in st.session_state:
    st.session_state['shopping_list'] = []

def update_inventory_with_bought_item(item_name):
    if item_name not in st.session_state['inventory']:
        st.session_state['inventory'][item_name] = item_name

# Check if the user is logged in
if st.session_state["logged_in"]:

    # Streamlit app layout
    st.title('ReC🍳okify')

    # Sidebar navigation
    page = st.sidebar.radio('Navigate to', ['Home', 'Inventory', 'Recipes', 'Shopping List'])

    api_key = '8f6828d3c3714e5d847cab14a9b57fb1'

    if page == 'Home':
        st.header('🏠 Welcome to our App!')
        st.markdown('Are you tired of forgetting what is in your storage or pantry? Look no further! Our user-friendly app is designed to help you effortlessly manage and keep track of all your items.')

        st.markdown('**Key Features:**')
        st.markdown('✅ User-Friendly Interface: Intuitive design for easy navigation.')
        st.markdown('✅ Secure Registration: Create an account with us to safeguard your data.')
        st.markdown('✅ Effortless Login: Access your inventory with a breeze.')
        st.markdown('✅ Organize Your Items: Add, delete, and query your items hassle-free.')
        st.markdown('✅ Password Security: Your data is safe with us - we use state-of-the-art encryption.')

        st.markdown('Whether you want to organize your kitchen, garage, or office supplies, our app has got you covered. Take control of your inventory like never before.')

    elif page == 'Inventory':
        st.header('🥦 Your Inventory')
        item_name = st.text_input('Add an item to your inventory:')
        if st.button('Add to Inventory') and item_name:
            st.session_state['inventory'][item_name] = item_name
        st.subheader("Inventory Items")
        st.write(', '.join(st.session_state['inventory'].keys()))

    elif page == 'Recipes':
        st.header('🍲 Find Recipes')
        inventory_items = list(st.session_state['inventory'].keys())
        selected_items = st.multiselect('Select items from your inventory for recipes:', inventory_items)

        if st.button('Find Recipes with Selected Ingredients'):
            if selected_items:
                recipes = get_recipe_recommendations(api_key, selected_items)
                if recipes and isinstance(recipes, list):
                    for recipe in recipes:
                        st.subheader(recipe['title'])
                        st.image(recipe['image'])

                        recipe_details = get_recipe_details(api_key, recipe['id'])
                        if recipe_details:
                            ingredients = [ingredient['name'] for ingredient in recipe_details['extendedIngredients']]
                            st.write("**Ingredients**: ", ', '.join(ingredients))

                            # Decode HTML entities in instructions
                            instructions = html.unescape(recipe_details['instructions']) if 'instructions' in recipe_details else "Not available"
                            st.write("**Instructions**: ", instructions)

                            # Display cooking time if available
                            if 'readyInMinutes' in recipe_details:
                                st.write(f"**Cooking Time**: {recipe_details['readyInMinutes']} minutes")

                            missing_ingredients = [ingredient for ingredient in ingredients if ingredient not in st.session_state['inventory']]
                            st.session_state['shopping_list'].extend(missing_ingredients)

                            # Function to clean HTML tags
                            def clean_html(html_string):
                                soup = BeautifulSoup(html_string, 'html.parser')
                                return soup.get_text(separator='\n')

                            # Display recipe details with cleaned instructions
                            st.title(recipe_details['title'])
                            cleaned_instructions = clean_html(recipe_details['instructions'])
                            st.write(f"**Instructions:**\n{cleaned_instructions}")

    elif page == 'Shopping List':
        st.header('🛒 Your Shopping List')
        # Use enumerate to get both the index and the item
        for index, item in enumerate(st.session_state['shopping_list']):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"- {item}")
            with col2:
                # Unique key using both the item name and its index
                if st.button(f"Mark as bought", key=f"bought_{item}_{index}"):
                    st.session_state['shopping_list'].remove(item)
                    update_inventory_with_bought_item(item)
else:
    # If the user is not logged in, he sees the login page
    show_login_page()
    
# Styling and other layout improvements
st.markdown("""
    <style>
    .main {background-color: #ADD8E6;}
    </style>
    """, unsafe_allow_html=True)
    
 
# Disclaimer:

# The Streamlit app code provided above was developed independently, and its functionality and structure were not directly influenced by ChatGPT
# However, ChatGPT has played a role in several supportive and ancillary capacities, including:

# 1. Code Explanation: ChatGPT has been used to provide detailed explanations and comments within the code
# These comments aim to clarify the purpose and functionality of various code segments, making the code more understandable, especially for those who are new to Python or Streamlit.

# 2. Debugging and Troubleshooting: ChatGPT may have been consulted for debugging the code, identifying potential issues, and suggesting solutions to improve code efficiency and resolve errors

# 3. Educational Support: ChatGPT has likely served as an educational tool, providing insights into best practices in Python programming, API integration, and Streamlit application development

# It's important to note that ChatGPT's role is purely advisory and supportive
# The actual coding, design decisions, and implementation were carried out by the developers of the application, independent of ChatGPT's AI capabilities.