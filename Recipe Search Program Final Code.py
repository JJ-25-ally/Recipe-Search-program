import requests


def get_exclusions():
    """
    Ask the user if they want to exclude any ingredients from the search and collect those exclusions.
    """
    exclusions = []  # Create an empty list to store ingredients the user wants to exclude
    ask_restrictions = input("Do you want to exclude any ingredients from the search? yes/no ").strip().lower()

    if ask_restrictions == "yes":
        while True:
            exclusion = input("Please enter an ingredient you want to exclude: ")
            exclusions.append(exclusion)  # Add the excluded ingredient to the list
            add_more = input("Do you want to exclude another ingredient? yes/no ")
            if add_more != "yes":  # If the answer is not 'yes', stop asking for more exclusions
                break

    return exclusions  # Return the list of excluded ingredients


def get_cuisine_type():
    """
    Ask the user for their preferred cuisine type.
    """
    return input(
        "Enter a cuisine type (e.g., American, Chinese, Italian etc.) or "
        "leave blank for no preference: ").strip().lower()
    # Get the user's preferred cuisine type and convert it to lowercase for consistency


def get_calorie_range():
    """
    Ask the user for their preferred calorie range.
    """
    return input("Enter calorie range (e.g., 100-300) or leave blank for no preference: ").strip()


def recipe_search(ingredient, exclusions, cuisine, calories):
    """
    Search for recipes based on the user's criteria.
    """
    app_id = '2494b7d1'  # Your Edamam API app ID
    app_key = 'd2a8cae7c64ff1a4b653baf56db8f217'  # Your Edamam API key
    base_url = f'https://api.edamam.com/api/recipes/v2?type=public&q={ingredient}&app_id={app_id}&app_key={app_key}'

    # Add exclusions to the URL if there are any
    for exclusion in exclusions:
        base_url += f"&excluded={exclusion}"

    # Add cuisine type to the URL if provided
    if cuisine:
        base_url += f"&cuisineType={cuisine}"

    # Add calorie range to the URL if provided
    if calories:
        base_url += f"&calories={calories}"

    print(f"URL with all filters: {base_url}")  # Print the URL for debugging to see how it looks
    result = requests.get(base_url)  # Send a request to the API using the URL
    data = result.json()  # Convert the response from the API to a JSON format
    return data.get('hits', [])  # Return the list of recipes found


def filter_recipes(results, exclusions):
    """
    Filter out recipes that contain any of the excluded ingredients.
    """
    filtered_results = []

    exclusions = [exclusion.lower() for exclusion in exclusions]  # Convert all exclusions to lowercase

    # Check each recipe to see if it should be included
    for result in results:
        recipe = result['recipe']  # Get the recipe from the results
        should_include = True  # Assume the recipe should be included unless we find an exclusion

        # Get all ingredients from the recipe and convert them to lowercase
        recipe_ingredients = [ingredient['food'].lower() for ingredient in recipe['ingredients']]

        # Check if any excluded ingredient is in the recipe
        for exclusion in exclusions:
            if any(exclusion in ingredient for ingredient in recipe_ingredients):
                should_include = False  # If an exclusion is found, mark the recipe for exclusion
                break  # No need to check other exclusions

        # Add the recipe to the filtered list if it should be included
        if should_include:
            filtered_results.append(result)

    return filtered_results  # Return the list of recipes that do not contain excluded ingredients


def print_recipe_details(recipe, file):
    """
    Print details of a recipe, including title, URL, total time, servings, and ingredients.
    """
    file.write(f"Title: {recipe['label']}\n")
    file.write(f"URL: {recipe['url']}\n")

    total_time = recipe.get('totalTime')
    if total_time is not None:
        if total_time > 0:
            hours = total_time // 60  # Calculate hours from total minutes
            minutes = total_time % 60  # Calculate remaining minutes
            file.write(f"Total Time: {hours} hours and {minutes} minutes \n")
        else:
            file.write(f"Total Time: Not available\n")  # If total time is zero, state that it's not available
    else:
        file.write(f"Total Time: Not available\n")  # If no total time is provided, state that it's not available

    servings = recipe.get('yield')
    if servings is not None:
        file.write(f"Servings: {servings}\n")
    else:
        file.write(f"Servings: Not available\n")

    ingredients = recipe.get('ingredients', [])
    if ingredients:
        file.write(f'Shopping List: \n')  # Start the shopping list section
        for ingredient in ingredients:
            file.write(f"- {ingredient['food'].lower()}\n")  # Write each ingredient to the file in lowercase
    else:
        file.write(f"No ingredients found.\n")  # If no ingredients are found, state that,
        # - ideally this should not be the case.

    file.write('\n')  # Add a newline for separation between recipes


def run():
    """
    Main function to run the recipe search and display results.
    """
    ingredient = input('Enter an ingredient or several ingredients separated by comma: ')
    # Get the main ingredient(s) from the user
    exclusions = get_exclusions()  # Get the list of excluded ingredients from the user
    cuisine = get_cuisine_type()  # Get the preferred cuisine type from the user
    calories = get_calorie_range()  # Get the preferred calorie range from the user

    results = recipe_search(ingredient, exclusions, cuisine, calories)
    # Perform the recipe search with the user's criteria

    # Filter the recipes to exclude any with excluded ingredients
    filtered_results = filter_recipes(results, exclusions)

    if len(filtered_results) == 0:  # Check if no recipes match after filtering
        print("No results found. Please try again.")  # Notify the user that no recipes were found
    else:
        print(f'Found {len(filtered_results)} recipes matching your criteria. \n')  # Print the number of recipes found

        with open("recipes search.txt", "w", encoding="utf-8") as file:
            # The "encoding='utf-8'" part ensures that special characters
            # (like accents or non-English letters) are properly saved.
            for i, result in enumerate(filtered_results, start=1):  # Enumerate helps us to get both the index (i)
                # and the result (recipe) from the filtered results. 'start=1' means
                # the index starts from 1 instead of 0.
                recipe = result['recipe']  # Get the recipe from the filtered results
                file.write(f"Recipe {i}:\n")  # Write the recipe index to the file
                print_recipe_details(recipe, file)  # Write detailed recipe information to the file
        print("Results have been written to recipes search.txt")  # Notify the user that the results have been saved


run()  # Call the run function to start the program