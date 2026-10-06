import streamlit as st
import pandas as pd
from utils import load_dataset, extract_all_unique_ingredients, match_and_rank_recipes

# Page Configuration
st.set_page_config(
    page_title="Smart Food & Recipe Recommendation System",
    page_icon="🍽️",
    layout="wide"
)

# Custom Premium CSS (Inline Filters, Warm Food Palette, No Emojis in Badges)
st.markdown("""
<style>
    /* App Background */
    .stApp {
        background-color: #FAFAFA;
        color: #2D3748;
    }
    
    /* Hero Banner */
    .hero-card {
        background-color: #FFF5EE;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #FFE4D6;
        margin-bottom: 2rem;
    }
    .hero-title {
        color: #FF6B35;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        color: #718096;
        font-size: 1rem;
    }

    /* Recipe Card */
    .recipe-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }

    /* Status Tags */
    .tag-have {
        color: #22543D;
        background-color: #C6F6D5;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
    }
    .tag-miss {
        color: #742A2A;
        background-color: #FED7D7;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Load Dataset
    df, error_msg = load_dataset("recipes.csv")
    
    if error_msg:
        st.error(f"Error: {error_msg}")
        return

    all_ingredients = extract_all_unique_ingredients(df)

    # ---------------- HERO BANNER WITH IMAGE ----------------
    col_hero_text, col_hero_img = st.columns([3, 2])
    
    with col_hero_text:
        st.markdown("""
        <div class="hero-card">
            <div class="hero-title">Smart Food & Recipe Recommender</div>
            <div class="hero-subtitle">Discover delicious recipes you can cook with ingredients already available in your kitchen.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_hero_img:
        st.image(
            "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80",
            use_container_width=True
        )

    # ---------------- PANTRY INGREDIENTS INPUT ----------------
    st.subheader("Pantry Ingredients")
    
    selected_user_ingredients = st.multiselect(
        "Select ingredients currently available in your kitchen:",
        options=all_ingredients,
        help="Select ingredients to calculate matching recipes."
    )

    custom_ing_input = st.text_input("Add additional custom ingredients (comma-separated):", placeholder="e.g. garlic, chili flakes, butter")
    
    if custom_ing_input.strip():
        extra_ings = [i.strip().lower() for i in custom_ing_input.split(",") if i.strip()]
        user_ingredients = list(set(selected_user_ingredients + extra_ings))
    else:
        user_ingredients = selected_user_ingredients

    st.markdown("---")

    # ---------------- INLINE FILTERS (INSIDE DASHBOARD) ----------------
    st.subheader("Filter Recipes")
    
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    with f_col1:
        search_query = st.text_input("Search", value="", placeholder="Recipe or ingredient...")
        selected_diet = st.selectbox("Dietary Preference", ["Any"] + sorted(list(df['diet'].dropna().unique())))

    with f_col2:
        selected_cuisine = st.selectbox("Cuisine", ["Any"] + sorted(list(df['cuisine'].dropna().unique())))
        selected_meal = st.selectbox("Meal Type", ["Any"] + sorted(list(df['meal_type'].dropna().unique())))

    with f_col3:
        selected_diff = st.selectbox("Difficulty", ["Any"] + sorted(list(df['difficulty'].dropna().unique())))
        max_time_possible = int(df['cooking_time'].max())
        min_time_possible = int(df['cooking_time'].min())
        selected_max_time = st.slider("Max Cooking Time (mins)", min_value=min_time_possible, max_value=max_time_possible, value=max_time_possible, step=5)

    with f_col4:
        st.write("")
        st.write("")
        if st.button("Reset All Filters", use_container_width=True):
            st.rerun()

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
        st.info("No matching recipes found with the current filter settings. Try adjusting your search or filter criteria.")
    else:
        top_5 = recommendations.head(5)
        st.subheader(f"Recommended Recipes ({len(top_5)})")

        for idx, row in top_5.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="recipe-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; color: #1A202C;">{row['name']}</h3>
                        <span style="background-color: #FF6B35; color: #FFFFFF; padding: 0.3rem 0.8rem; border-radius: 16px; font-weight: bold; font-size: 0.9rem;">
                            {row['match_score']}% Match
                        </span>
                    </div>
                    <p style="color: #4A5568; font-size: 0.9rem; margin-top: 0.5rem;">{row['description']}</p>
                    <p style="font-size: 0.85rem; color: #718096;">
                        <b>Cuisine:</b> {row['cuisine']} | <b>Meal:</b> {row['meal_type']} | <b>Diet:</b> {row['diet']} | <b>Difficulty:</b> {row['difficulty']} | <b>Cooking Time:</b> {int(row['cooking_time'])} mins
                    </p>
                """, unsafe_allow_html=True)

                col_avail, col_miss = st.columns(2)
                
                with col_avail:
                    st.markdown("**Available Ingredients:**")
                    if row['matched_ingredients']:
                        tags_html = "".join([f'<span class="tag-have">{ing}</span>' for ing in row['matched_ingredients']])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    else:
                        st.caption("None selected")

                with col_miss:
                    st.markdown("**Missing Ingredients:**")
                    if row['missing_ingredients']:
                        tags_html = "".join([f'<span class="tag-miss">{ing}</span>' for ing in row['missing_ingredients']])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    else:
                        st.caption("All ingredients available!")

                st.markdown("<br>", unsafe_allow_html=True)

                with st.expander(f"View Recipe & Instructions for {row['name']}"):
                    col_ing, col_inst = st.columns([1, 2])
                    
                    with col_ing:
                        st.markdown("**Complete Ingredients:**")
                        full_ing_list = [i.strip() for i in str(row['ingredients']).split(';') if i.strip()]
                        for item in full_ing_list:
                            st.write(f"• {item.capitalize()}")

                    with col_inst:
                        st.markdown("**Cooking Instructions:**")
                        instructions_steps = str(row['instructions']).split('|')
                        for step_num, step_text in enumerate(instructions_steps, 1):
                            st.write(f"**Step {step_num}:** {step_text.strip()}")

                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
