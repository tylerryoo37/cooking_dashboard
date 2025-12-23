import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Gourmet Recipe Dashboard",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")


# Data Loading & Preparation
@st.cache_data
def load_data():
    df = pd.read_csv('recipes.csv')
    df['dish_name'] = df['dish_name'].ffill()
    return df

df = load_data()

# Initialize session state
if 'selected_dish' not in st.session_state:
    st.session_state.selected_dish = None

def display_recipe_card(dish, df):
    dish_data = df[df['dish_name'] == dish]
    
    # Recipe Card Container
    with st.container():
        st.markdown(f'<div class="recipe-card">', unsafe_allow_html=True)
        
        # Header with Badge
        # st.markdown(f'<span class="badge">Recipe</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-header"><h2 style="margin:0;">{dish}</h2><span class="badge">Recipe</span></div>', unsafe_allow_html=True)

        
        col1, col2 = st.columns([1, 1.5], gap="large")
        
        with col1:
            st.markdown('### 🛒 Ingredients', unsafe_allow_html=True)
            for _, row in dish_data.iterrows():
                st.markdown(f"""
                <div class="ingredient-item">
                    <span class="ingredient-name">{row['ingredient']}</span>
                    <span class="ingredient-amount">{row['amount']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('### 📝 Instructions', unsafe_allow_html=True)
            if not dish_data.empty:
                instructions = dish_data.iloc[0]['instructions']
                if pd.notna(instructions) and instructions.strip():
                    # Splitting instructions by numbered list if possible
                    steps = str(instructions).split('\n')
                    for step in steps:
                        if step.strip():
                            st.markdown(f'<div class="instruction-step">{step.strip()}</div>', unsafe_allow_html=True)
                else:
                    st.info("No detailed instructions provided for this recipe.")
            
            # Link Button
            if not dish_data.empty and 'link' in dish_data.columns:
                link = dish_data.iloc[0]['link']
                if pd.notna(link) and str(link).startswith('http'):
                    st.link_button("View Full Recipe Source", link, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


# Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3565/3565418.png", width=100)
    st.title("Kitchen Assistant")
    st.divider()
    
    search_type = st.radio('Search Strategy', ['By Dish Name', 'By Ingredient'])
    
    # Reset selected dish if search strategy changes
    if 'last_search_type' not in st.session_state:
        st.session_state.last_search_type = search_type
    
    if search_type != st.session_state.last_search_type:
        st.session_state.selected_dish = None
        st.session_state.last_search_type = search_type

    if search_type == 'By Dish Name':
        search_query = st.text_input('Search for a dish...', placeholder="e.g. 야끼니꾸")
    else:
        search_query = st.text_input('Search for an ingredient...', placeholder="e.g. 간장")




# Main Content
st.markdown("""
<div class="hero-section">
    <h1 style="color: white; margin:0;">Gourmet Recipe Dashboard</h1>
    <p style="opacity: 0.8; font-weight: 300;">Discover your next meal in 20 minutes.</p>
</div>
""", unsafe_allow_html=True)

# Search Logic
if search_type == 'By Dish Name':
    if search_query:
        filtered_df = df[df['dish_name'].str.contains(search_query, case=False, na=False)]
        dishes = filtered_df['dish_name'].unique()
    else:
        dishes = df['dish_name'].unique()

    if len(dishes) == 0:
        st.warning("No dishes found matching your search.")
    
    for dish in dishes:
        display_recipe_card(dish, df)


else:  # Search by Ingredient
    if search_query:
        # If a dish is already selected, show its recipe
        if st.session_state.selected_dish:
            if st.button("← Back to search results", type="secondary"):
                st.session_state.selected_dish = None
                st.rerun()
            
            display_recipe_card(st.session_state.selected_dish, df)
        
        else:
            filtered = df[df['ingredient'].str.contains(search_query, case=False, na=False)]
            found_dishes = filtered['dish_name'].unique()
            
            st.markdown(f"### Dishes featuring '{search_query}'")
            
            if len(found_dishes) > 0:
                cols = st.columns(3)
                for idx, dish in enumerate(found_dishes):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="recipe-card" style="text-align: center;">
                            <span class="badge" style="background-color: var(--primary-color);">Match Found</span>
                            <h4>{dish}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"View {dish} Recipe", key=f"btn_{idx}", use_container_width=True):
                            st.session_state.selected_dish = dish
                            st.rerun()
            else:
                st.warning(f"No dishes found containing '{search_query}'.")
    else:
        st.info("Start typing an ingredient in the sidebar to filter recipes.")


# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.8rem; padding: 2rem;">
    Premium Recipe Dashboard &copy; 2025 | Created for busy cooks
</div>
""", unsafe_allow_html=True)