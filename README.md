# Smart Food & Recipe Recommendation System

A clean, explainable, content-based recipe recommendation web application built with **Streamlit** and **Pandas**. 

The system helps users reduce food waste and decide what to cook by matching ingredients available in their pantry against a recipe dataset.

---

## Key Features
- **Ingredient Matching Engine**: Uses a simple, mathematical content-based formula:
  $$\text{Match Score} = \frac{\text{Matching User Ingredients}}{\text{Total Recipe Ingredients}} \times 100$$
- **Smart Filtering**: Filter recipes by Dietary Preference, Cuisine, Meal Type, Difficulty, and Maximum Cooking Time.
- **Search Capability**: Instant search by recipe name, ingredient, or cuisine.
- **Recipe Cards**: Displays top 5 matching recipe cards with match score badges and visual tags for available vs missing ingredients.
- **Detailed Recipe Instructions**: Expandable step-by-step cooking guide.

---

## Step-by-Step Setup and Execution Instructions

### Step 1: Create Project Directory
Create a folder on your computer and place all project files inside it:
```bash
mkdir recipe_recommendation_app
cd recipe_recommendation_app
