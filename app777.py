import streamlit as st
import requests
import html  # Importing the html library for decoding HTML entities
import time
import random
from account_helper import register_user, is_login_successful, query_all_table, query_delete, query_add  # Import custom library
from bs4 import BeautifulSoup
import re

# ReCookify

# This Streamlit  app is designed to be a comprehensive kitchen management tool. It integrates with the Spoonacular API to provide recipe recommendations based on user-selected ingredients from their inventory. The app consists of multiple functionalities:

# 1. Custom CSS Integration: Enhances the visual aesthetics of the app using a local CSS file
# 2. Spoonacular API Integration: Utilizes the Spoonacular API to fetch recipes based on ingredients and detailed recipe information
# 3. Session State Management: Manages user data across different sessions, specifically for inventory and shopping list
# 4. Streamlit Interface: Uses Streamlit's framework for creating an interactive web application. It includes functionalities such as adding items to inventory, searching for recipes, and managing a shopping list
# 5. Error Handling: Implements error handling for API requests to ensure stability and user feedback on failures

# Overall, the app serves as a convenient platform for users to manage their kitchen inventory, discover new recipes, and efficiently plan their shopping activities – especially for students


# Here you can define the login page
def show_login_page():
    st.title("Sign In & Sign Up")
    ###############################
    # Register & Login logic start
    ###############################
    # Define the text fields to enter username & password
    uname = st.text_input("Username", key="username_input")
    psword = st.text_input("Password", type="password", key="password_input")
    colu1, colu2 = st.columns([1, 1])
    ###############################
    # Register logic
    ###############################
    # If the register button is pressed, the following code is executed
    with colu2:
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
                st.rerun()  # st.experimental_rerun()
    ###############################
    # Login logic
    ###############################
    # If the login button is pressed, the following code is executed
    with colu1:
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
                st.rerun()  # st.experimental_rerun()
    ###############################
    # Register & Login logic end
    ###############################

# Custom CSS to improve the look and feel of the app
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call the function to apply custom CSS
local_css("style.css")

# Function to clean HTML tags, defined outside the loop
def clean_html(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    return soup.get_text(separator='\n')

# Function to remove HTML tags from text
def remove_html_tags(text):
    # Regular expression for finding HTML tags
    pattern = r'<[^>]+>'
    # Replace HTML tags with an empty string
    return re.sub(pattern, ' ', text)

# Function to get recipe recommendations from the Spoonacular API
def get_recipe_recommendations(api_key, ingredients):
    endpoint = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": api_key,
        "ingredients": ",".join(ingredients),
        "number": 1  # Number of recipes to retrieve
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
        recipe_details = response.json()

        # Clean the HTML content from the instructions
        if 'instructions' in recipe_details:
            recipe_details['instructions'] = remove_html_tags(recipe_details['instructions'])

        return recipe_details
    except requests.exceptions.RequestException as err:
        return f"Error: {err}"

def update_inventory_with_bought_item(item_name, user):
    result = query_all_table(user)
    inventory_items_y = []
    for item in result[0]:
        inventory_items_y.append(item[2])
    if item_name not in inventory_items_y:
        query_add(user, item_name)


def show_main_app():

    # Streamlit app layout
    st.title('ReC🍳okify')

    # Sidebar navigation
    page = st.sidebar.radio('Navigate to', ['Home', 'Inventory', 'Recipes', 'Shopping List', 'Logout'])

    api_key = '5bb998eadc274a599d9732e71f03a378'

    ###############################
    # Logout logic start
    ###############################
    # If the logout button is pressed, the following code is executed
    if page == 'Logout':
        st.session_state['logged_in'] = False
        st.session_state["uname"] = None
        st.session_state['shopping_list'] = []
        st.experimental_rerun()  # Use st.experimental_rerun() instead of st.rerun()
    ###############################
    # Logout logic end
    ###############################

    # Leverage the user variable from login
    user = st.session_state["uname"]

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

        ###############################
        # Add items start
        ###############################
        # Check if the 'add_button_clicked' key exists in the session_state, if not, initialize it
        if "new_item" not in st.session_state:
            st.session_state["new_item"] = ""
        itemname = st.text_input('Add an item to your inventory:')
        # Only set the flag when the button is clicked
        if st.button('Add to Inventory', key=st.session_state["new_item"]) and itemname != "":
            result = query_all_table(user)
            inventory_items_x = []
            for item in result[0]:
                inventory_items_x.append(item[2])
            # Add the selected item for the user
            if itemname not in inventory_items_x:
                query_add(user, itemname)
                st.session_state["new_item"] = random.random()  # prevents a stupid streamlit bug (/feature)
            st.rerun()  # st.experimental_rerun()
        ###############################
        # Add items end
        ###############################

        st.subheader("Inventory Items")
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

    elif page == 'Recipes':
        st.header('🍲 Find Recipes')
        result = query_all_table(user)
        inventory_items = []
        for item in result[0]:
            inventory_items.append(item[2])
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

                            # Decode HTML entities in instructions and clean HTML tags
                            instructions = html.unescape(recipe_details['instructions']) if 'instructions' in recipe_details else "Not available"
                            cleaned_instructions = clean_html(instructions)

                            st.write("**Instructions**: ", cleaned_instructions)

                            # Display cooking time if available
                            if 'readyInMinutes' in recipe_details:
                                st.write(f"**Cooking Time**: {recipe_details['readyInMinutes']} minutes")

                            missing_ingredients = [ingredient for ingredient in ingredients if ingredient not in inventory_items]
                            st.session_state['shopping_list'].extend(missing_ingredients)

    # The shopping list is not persistent, and thus does not need a delete button.
    # Just select your recipe, buy the things and mark them as bought. If you
    # log out in between you need to search for the recipe again and your
    # shopping list is updated dynamically.
    elif page == 'Shopping List':
        st.session_state['shopping_list'] = list(set(st.session_state['shopping_list']))
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
                    update_inventory_with_bought_item(item, user)
                    st.rerun()  # st.experimental_rerun()


# First we need to initialize the session states for login, inventory and shopping list
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["uname"] = None
if 'shopping_list' not in st.session_state:
    st.session_state['shopping_list'] = []

# Check if the user is logged in
if st.session_state["logged_in"]:
    show_main_app()
else:
    # If the user is not logged in, he sees the login page
    show_login_page()




# Styling and other layout improvements
st.markdown("""
    <style>
    .main {background-color: #ffffff;}
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
