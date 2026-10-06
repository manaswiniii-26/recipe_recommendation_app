import pandas as pd

def load_dataset(filepath="recipes.csv"):
    """
    Loads and validates the recipe dataset.
    Returns (DataFrame, error_message).
    """
    try:
        df = pd.read_csv(filepath)
        required_cols = [
            'name', 'cuisine', 'meal_type', 'diet', 
            'ingredients', 'cooking_time', 'difficulty', 
            'description', 'instructions'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return None, f"Dataset is missing required column(s): {', '.join(missing_cols)}"
        
        # Ensure proper data types
        df['cooking_time'] = pd.to_numeric(df['cooking_time'], errors='coerce').fillna(0)
        return df, None
    except FileNotFoundError:
        return None, f"Dataset file '{filepath}' was not found in the project root directory."
    except Exception as e:
        return None, f"An error occurred while loading the dataset: {str(e)}"


def extract_all_unique_ingredients(df):
    """
    Extracts a clean, sorted list of all unique ingredients across recipes.
    """
    all_ingredients = set()
    for row in df['ingredients'].dropna():
        # Split by semicolon as defined in recipes.csv
        items = [i.strip().lower() for i in str(row).split(';') if i.strip()]
        all_ingredients.update(items)
    return sorted(list(all_ingredients))


def match_and_rank_recipes(df, user_ingredients, diet="Any", cuisine="Any", 
                            meal_type="Any", max_time=120, difficulty="Any", 
                            search_query=""):
    """
    Filters recipes based on user preferences and calculates match score based on 
    matching ingredients vs total recipe ingredients.
    """
    filtered_df = df.copy()

    # 1. Apply Search Query Filter (name, ingredient, or cuisine)
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df['name'].str.lower().str.contains(q, na=False) |
            filtered_df['cuisine'].str.lower().str.contains(q, na=False) |
            filtered_df['ingredients'].str.lower().str.contains(q, na=False)
        ]

    # 2. Apply Categorical Filters
    if diet != "Any":
        filtered_df = filtered_df[filtered_df['diet'].str.lower() == diet.lower()]
        
    if cuisine != "Any":
        filtered_df = filtered_df[filtered_df['cuisine'].str.lower() == cuisine.lower()]
        
    if meal_type != "Any":
        filtered_df = filtered_df[filtered_df['meal_type'].str.lower() == meal_type.lower()]
        
    if difficulty != "Any":
        filtered_df = filtered_df[filtered_df['difficulty'].str.lower() == difficulty.lower()]
        
    filtered_df = filtered_df[filtered_df['cooking_time'] <= max_time]

    if filtered_df.empty:
        return pd.DataFrame()

    # 3. Calculate Content-Based Ingredient Match Score
    user_ing_set = set(ing.strip().lower() for ing in user_ingredients if ing.strip())

    results = []
    for idx, row in filtered_df.iterrows():
        recipe_ing_list = [i.strip().lower() for i in str(row['ingredients']).split(';') if i.strip()]
        recipe_ing_set = set(recipe_ing_list)
        
        if len(recipe_ing_set) == 0:
            match_score = 0.0
            matched_ing = []
            missing_ing = []
        else:
            matched_ing = sorted(list(recipe_ing_set.intersection(user_ing_set)))
            missing_ing = sorted(list(recipe_ing_set - user_ing_set))
            # Match Score = matching user ingredients / total recipe ingredients * 100
            match_score = round((len(matched_ing) / len(recipe_ing_set)) * 100, 1)

        row_dict = row.to_dict()
        row_dict['match_score'] = match_score
        row_dict['matched_ingredients'] = matched_ing
        row_dict['missing_ingredients'] = missing_ing
        row_dict['total_ingredients_count'] = len(recipe_ing_set)
        results.append(row_dict)

    result_df = pd.DataFrame(results)

    # If user provided ingredients, rank primarily by match_score, secondarily by cooking time
    if user_ing_set:
        result_df = result_df.sort_values(by=['match_score', 'cooking_time'], ascending=[False, True])
    else:
        result_df = result_df.sort_values(by=['cooking_time'], ascending=True)

    return result_df
