import streamlit as st
import pandas as pd
from utils import load_dataset, extract_all_unique_ingredients, match_and_rank_recipes

# Page Configuration
st.set_page_config(
    page_title="Smart Food & Recipe Recommendation System",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Light mode, soft warm food accents, rounded cards)
st.markdown("""
<style>
    /* Main Background and Styling */
    .stApp {
        background-color: #FAFAFA;
        color: #2D3748;
    }
    
    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #FFF5F5 0%, #FFFAF0 100%);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #FEEBC8;
        margin-bottom: 2rem;
        text-align: center;
    }
    .header-title {
        color: #DD6B20;
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .header-subtitle {
        color: #718096;
        font-size: 1.05rem;
    }

    /* Recipe Card Styling */
    .recipe-card {
        background-color: #FFFFFF;
        border-radius: 14px;
        padding: 1.4rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
    }
    
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
    }
    .badge-cuisine { background-color: #EBF8FF; color: #2B6CB0; }
    .badge-meal { background-color: #EDF2F7; color: #4A5568; }
    .badge-diet { background-color: #F0FFF4; color: #276749; }
    .badge-diff { background-color: #FAF5FF; color: #6B46C1; }
    
    /* Ingredient Tag Styling */
    .ing-tag-have {
        color: #22543D;
        background-color: #C6F6D5;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 2px;
    }
    .ing-tag-miss {
        color: #742A2A;
        background-color: #FED7D7;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Load Dataset
    df, error_msg = load_dataset("recipes.csv")
    
    if error_msg:
        st.error(f"⚠️ {error_msg}")
        st.info("Please verify that `recipes.csv` is present in the app root directory and contains all necessary columns.")
        return

    all_ingredients = extract_all_unique_ingredients(df)

    # ---------------- HEADER ----------------
    st.markdown("""
    <div class="header-banner">
        <div class="header-title">🍳 Smart Food & Recipe Recommendation System</div>
        <div class="header-subtitle">Discover delicios recipes you can cook with ingredients already in your pantry!</div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- SIDEBAR: FILTERS ----------------
    st.sidebar.header("🔍 Filters & Preferences")
    
    # Search Query
    search_query = st.sidebar.text_input("🔎 Search Recipe, Ingredient, or Cuisine", value="", placeholder="e.g. Paneer, Pasta, Indian")

    # Dietary Preference
    diet_options = ["Any"] + sorted(list(df['diet'].dropna().unique()))
    selected_diet = st.sidebar.selectbox("🥗 Dietary Preference", diet_options)

    # Cuisine
    cuisine_options = ["Any"] + sorted(list(df['cuisine'].dropna().unique()))
    selected_cuisine = st.sidebar.selectbox("🌍 Cuisine", cuisine_options)

    # Meal Type
    meal_options = ["Any"] + sorted(list(df['meal_type'].dropna().unique()))
    selected_meal = st.sidebar.selectbox("🍽️ Meal Type", meal_options)

    # Difficulty
    diff_options = ["Any"] + sorted(list(df['difficulty'].dropna().unique()))
    selected_diff = st.sidebar.selectbox("⚡ Difficulty", diff_options)

    # Maximum Cooking Time
    max_time_possible = int(df['cooking_time'].max())
    min_time_possible = int(df['cooking_time'].min())
    selected_max_time = st.sidebar.slider("⏱️ Max Cooking Time (mins)", min_value=min_time_possible, max_value=max_time_possible, value=max_time_possible, step=5)

    # Reset Filters Button
    if st.sidebar.button("🔄 Reset Filters"):
        st.rerun()

    # ---------------- MAIN CONTENT: INGREDIENTS INPUT ----------------
    st.subheader("🛒 What ingredients do you currently have?")
    
    selected_user_ingredients = st.multiselect(
        "Select ingredients from list or type to search (select multiple):",
        options=all_ingredients,
        help="Select the ingredients you have at home to see what recipes you can prepare!"
    )

    # Option to manually type additional custom ingredients separated by comma
    custom_ing_input = st.text_input("Or enter additional ingredients (comma-separated):", placeholder="e.g. garlic, chili flakes, butter")
    
    if custom_ing_input.strip():
        extra_ings = [i.strip().lower() for i in custom_ing_input.split(",") if i.strip()]
        # Combine without duplicates
        user_ingredients = list(set(selected_user_ingredients + extra_ings))
    else:
        user_ingredients = selected_user_ingredients

    # ---------------- RECOMMENDATION LOGIC ----------------
    recommendations = match_and_rank_recipes(
        df=df,
        user_ingredients=user_ingredients,
        diet=selected_diet,
        cuisine=selected_cuisine,
        meal_type=selected_meal,
        max_time=selected_max_time,
        difficulty=selected_diff,
        search_query=search_query
    )

    st.markdown("---")

    # ---------------- DISPLAY RECOMMENDATIONS ----------------
    if recommendations.empty:
        st.warning("🏷️ No exact recipe matches found with the current filters and ingredients.")
        st.info("💡 **Suggestions to get results:**\n"
                "- Try relaxing some filters (e.g., set Dietary Preference, Cuisine, or Difficulty to 'Any')\n"
                "- Increase the Max Cooking Time slider\n"
                "- Clear or broaden your search term\n"
                "- Add more common ingredients you have on hand")
    else:
        top_5 = recommendations.head(5)
        st.markdown(f"### 🌟 Top Recommended Recipes ({len(top_5)} showing)")

        for idx, row in top_5.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="recipe-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; color: #1A202C;">{row['name']}</h3>
                        <span style="background-color: #FEFCBF; color: #744210; padding: 0.4rem 0.8rem; border-radius: 20px; font-weight: bold; font-size: 0.95rem;">
                            🎯 {row['match_score']}% Match
                        </span>
                    </div>
                    <div style="margin-top: 0.5rem; margin-bottom: 0.8rem;">
                        <span class="badge badge-cuisine">🌍 {row['cuisine']}</span>
                        <span class="badge badge-meal">🍽️ {row['meal_type']}</span>
                        <span class="badge badge-diet">🥗 {row['diet']}</span>
                        <span class="badge badge-diff">⚡ {row['difficulty']}</span>
                        <span style="font-size: 0.85rem; color: #4A5568; margin-left: 0.4rem;">⏱️ {int(row['cooking_time'])} mins</span>
                    </div>
                    <p style="color: #4A5568; font-size: 0.95rem; margin-bottom: 0.8rem;">{row['description']}</p>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Ingredients You Have:**")
                    if row['matched_ingredients']:
                        tags_html = "".join([f'<span class="ing-tag-have">✓ {ing}</span>' for ing in row['matched_ingredients']])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    else:
                        st.caption("None of your selected ingredients match this recipe directly.")

                with col2:
                    st.markdown("**Missing Ingredients:**")
                    if row['missing_ingredients']:
                        tags_html = "".join([f'<span class="ing-tag-miss">✗ {ing}</span>' for ing in row['missing_ingredients']])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color: #2F855A; font-weight: bold;'>🎉 You have all ingredients!</span>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # View Detailed Recipe Modal / Expander
                with st.expander(f"📖 View Recipe Details & Cooking Instructions for {row['name']}"):
                    st.markdown(f"#### {row['name']}")
                    st.markdown(f"**Description:** {row['description']}")
                    
                    st.markdown("---")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**Complete List of Ingredients:**")
                        full_ing_list = [i.strip() for i in str(row['ingredients']).split(';') if i.strip()]
                        for item in full_ing_list:
                            status = "✅" if item.lower() in [u.lower() for u in user_ingredients] else "🛒"
                            st.write(f"{status} {item.capitalize()}")

                    with col_b:
                        st.markdown("**Recipe Overview:**")
                        st.write(f"• **Cuisine:** {row['cuisine']}")
                        st.write(f"• **Meal Type:** {row['meal_type']}")
                        st.write(f"• **Dietary Type:** {row['diet']}")
                        st.write(f"• **Cooking Time:** {int(row['cooking_time'])} minutes")
                        st.write(f"• **Difficulty:** {row['difficulty']}")

                    st.markdown("---")
                    st.markdown("**👨‍🍳 Step-by-Step Cooking Instructions:**")
                    # Split instructions by pipe symbol '|' if present
                    instructions_steps = str(row['instructions']).split('|')
                    for step_num, step_text in enumerate(instructions_steps, 1):
                        st.write(f"**Step {step_num}:** {step_text.strip()}")

                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
