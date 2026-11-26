
import streamlit as st
import json
import os
import re
from PIL import Image
from google import genai
from google.genai import types


# ==========================================
# 1. PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="What's Cooking?",
    page_icon="🍓",
    layout="wide"
)

SAVED_FILE = "saved_recipes.json"
MEAL_FILE = "meal_plan.json"


# ==========================================
# 2. CSS DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #fff8fb;
    color: #593b4b;
}

[data-testid="stSidebar"] {
    background-color: #fceaf1;
}

h1, h2, h3 {
    color: #a84f75 !important;
}

p, label, span {
    color: #68495a;
}

.stButton > button {
    background-color: #d8799d;
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 9px 20px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #bd5e84;
    color: white !important;
}

.stMultiSelect [data-baseweb="tag"] {
    background-color: #d8799d;
}

.hero-box {
    background: linear-gradient(
        115deg,
        #f7c4d7,
        #e9a9c4,
        #d98eae
    );
    padding: 35px;
    border-radius: 22px;
    color: white;
    margin-bottom: 20px;
}

.hero-box h1 {
    color: white !important;
    font-size: 38px;
}

.hero-box p {
    color: white !important;
    font-size: 16px;
}

.sidebar-title {
    color: #9f4269;
    font-size: 23px;
    font-weight: 800;
    margin-bottom: 4px;
}

.sidebar-subtitle {
    color: #a84f75;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 15px;
}

.footer {
    text-align: center;
    color: #b33e70;
    padding: 30px 0 12px 0;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

div[data-testid="stExpander"] {
    background-color: #fff0f5;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. RECIPES DATABASE
# ==========================================

RECIPES = [
    {
        "name": "Fresh Salad",
        "category": "Healthy",
        "time": 10,
        "emoji": "🥗",
        "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=900",
        "ingredients": ["lettuce", "tomato", "cucumber", "lemon"],
        "steps": [
            "Wash all vegetables.",
            "Cut the vegetables into small pieces.",
            "Add lemon juice and mix well.",
            "Serve fresh."
        ]
    },
    {
        "name": "Fruit Yogurt Bowl",
        "category": "Breakfast",
        "time": 5,
        "emoji": "🍓",
        "image": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=900",
        "ingredients": ["yogurt", "banana", "apple", "honey"],
        "steps": [
            "Put yogurt in a bowl.",
            "Cut the fruits.",
            "Add fruits over the yogurt.",
            "Add honey and serve."
        ]
    },
    {
        "name": "Banana Pancakes",
        "category": "Breakfast",
        "time": 15,
        "emoji": "🥞",
        "image": "https://images.unsplash.com/photo-1528207776546-365bb710ee93?w=900",
        "ingredients": ["banana", "egg", "flour", "milk"],
        "steps": [
            "Mash the banana.",
            "Mix with egg, flour and milk.",
            "Pour small portions into a pan.",
            "Cook both sides until golden."
        ]
    },
    {
        "name": "Classic Pancakes",
        "category": "Breakfast",
        "time": 20,
        "emoji": "🥞",
        "image": "https://images.unsplash.com/photo-1528207776546-365bb710ee93?w=900",
        "ingredients": ["flour", "milk", "egg", "sugar"],
        "steps": [
            "Mix flour, milk, egg and sugar.",
            "Heat a non-stick pan.",
            "Pour the batter into the pan.",
            "Flip when bubbles appear."
        ]
    },
    {
        "name": "Cheese Omelette",
        "category": "Breakfast",
        "time": 10,
        "emoji": "🍳",
        "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=900",
        "ingredients": ["egg", "cheese", "pepper", "butter"],
        "steps": [
            "Beat the eggs.",
            "Add pepper and cheese.",
            "Melt butter in a pan.",
            "Pour the mixture and cook."
        ]
    },
    {
        "name": "Tomato Pasta",
        "category": "Lunch",
        "time": 25,
        "emoji": "🍝",
        "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=900",
        "ingredients": ["pasta", "tomato", "garlic", "olive oil"],
        "steps": [
            "Cook pasta in boiling water.",
            "Heat olive oil and add garlic.",
            "Add chopped tomatoes.",
            "Mix the sauce with pasta."
        ]
    },
    {
        "name": "Creamy Pasta",
        "category": "Lunch",
        "time": 25,
        "emoji": "🍝",
        "image": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=900",
        "ingredients": ["pasta", "milk", "cheese", "butter"],
        "steps": [
            "Cook the pasta.",
            "Melt butter in a pan.",
            "Add milk and cheese.",
            "Mix with pasta and serve."
        ]
    },
    {
        "name": "Homemade Pizza",
        "category": "Lunch",
        "time": 40,
        "emoji": "🍕",
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=900",
        "ingredients": ["flour", "yeast", "tomato", "cheese"],
        "steps": [
            "Prepare the dough using flour and yeast.",
            "Let the dough rest.",
            "Add tomato sauce and cheese.",
            "Bake until golden."
        ]
    },
    {
        "name": "Chicken Sandwich",
        "category": "Lunch",
        "time": 15,
        "emoji": "🥪",
        "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=900",
        "ingredients": ["bread", "chicken", "lettuce", "tomato"],
        "steps": [
            "Cook the chicken.",
            "Prepare the bread.",
            "Add lettuce and tomato.",
            "Add chicken and serve."
        ]
    },
    {
        "name": "Potato Wedges",
        "category": "Snacks",
        "time": 30,
        "emoji": "🍟",
        "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=900",
        "ingredients": ["potato", "olive oil", "pepper", "garlic"],
        "steps": [
            "Wash and cut potatoes into wedges.",
            "Mix with olive oil and seasoning.",
            "Bake until crispy.",
            "Serve warm."
        ]
    },
    {
        "name": "Mango Smoothie",
        "category": "Drinks",
        "time": 5,
        "emoji": "🥭",
        "image": "https://images.unsplash.com/photo-1546173159-315724a31696?w=900",
        "ingredients": ["mango", "milk", "yogurt", "honey"],
        "steps": [
            "Peel and cut the mango.",
            "Add mango, milk and yogurt to a blender.",
            "Blend until smooth.",
            "Add honey if desired."
        ]
    },
    {
        "name": "Cheese Toast",
        "category": "Breakfast",
        "time": 8,
        "emoji": "🧀",
        "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=900",
        "ingredients": ["bread", "cheese", "butter"],
        "steps": [
            "Spread butter on bread.",
            "Add cheese.",
            "Toast until golden.",
            "Serve warm."
        ]
    },
    {
        "name": "Chicken Rice Bowl",
        "category": "Lunch",
        "time": 30,
        "emoji": "🍚",
        "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=900",
        "ingredients": ["chicken", "rice", "onion", "pepper"],
        "steps": [
            "Cook the rice.",
            "Cook chicken with onion.",
            "Add pepper and seasoning.",
            "Serve chicken over rice."
        ]
    },
    {
        "name": "Mashed Potatoes",
        "category": "Sides",
        "time": 20,
        "emoji": "🥔",
        "image": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=900",
        "ingredients": ["potato", "milk", "butter", "salt"],
        "steps": [
            "Boil potatoes until soft.",
            "Mash the potatoes.",
            "Add milk and butter.",
            "Mix until creamy."
        ]
    },
    {
        "name": "Avocado Toast",
        "category": "Breakfast",
        "time": 10,
        "emoji": "🥑",
        "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=900",
        "ingredients": ["bread", "avocado", "lemon", "pepper"],
        "steps": [
            "Toast the bread.",
            "Mash avocado with lemon.",
            "Spread avocado over toast.",
            "Add pepper and serve."
        ]
    }
]


# ==========================================
# 4. INGREDIENTS AND QUANTITIES
# ==========================================

INGREDIENTS = [
    "apple", "avocado", "banana", "bread", "butter",
    "cheese", "chicken", "cucumber", "egg", "flour",
    "garlic", "honey", "lettuce", "lemon", "milk",
    "mango", "olive oil", "onion", "pasta", "pepper",
    "potato", "rice", "sugar", "tomato", "yeast",
    "yogurt", "orange", "broccoli", "carrot", "salt"
]

QUANTITIES = {
    "Fresh Salad": [
        (1, "cup", "lettuce"),
        (2, "medium", "tomato"),
        (1, "medium", "cucumber"),
        (1, "tbsp", "lemon juice")
    ],
    "Fruit Yogurt Bowl": [
        (2, "cups", "yogurt"),
        (1, "medium", "banana"),
        (1, "medium", "apple"),
        (2, "tsp", "honey")
    ],
    "Banana Pancakes": [
        (1, "medium", "banana"),
        (1, "large", "egg"),
        (0.5, "cup", "flour"),
        (0.25, "cup", "milk")
    ],
    "Classic Pancakes": [
        (1, "cup", "flour"),
        (0.75, "cup", "milk"),
        (1, "large", "egg"),
        (1, "tbsp", "sugar")
    ],
    "Cheese Omelette": [
        (2, "large", "egg"),
        (0.25, "cup", "cheese"),
        (0.25, "tsp", "pepper"),
        (1, "tsp", "butter")
    ],
    "Tomato Pasta": [
        (150, "g", "pasta"),
        (2, "medium", "tomato"),
        (1, "clove", "garlic"),
        (1, "tbsp", "olive oil")
    ],
    "Creamy Pasta": [
        (150, "g", "pasta"),
        (0.5, "cup", "milk"),
        (0.5, "cup", "cheese"),
        (1, "tbsp", "butter")
    ],
    "Homemade Pizza": [
        (1.5, "cups", "flour"),
        (1, "tsp", "yeast"),
        (0.5, "cup", "tomato sauce"),
        (1, "cup", "cheese")
    ],
    "Chicken Sandwich": [
        (2, "slices", "bread"),
        (150, "g", "chicken"),
        (2, "leaves", "lettuce"),
        (1, "medium", "tomato")
    ],
    "Potato Wedges": [
        (2, "medium", "potato"),
        (1, "tbsp", "olive oil"),
        (0.5, "tsp", "pepper"),
        (1, "clove", "garlic")
    ],
    "Mango Smoothie": [
        (1, "medium", "mango"),
        (1, "cup", "milk"),
        (0.5, "cup", "yogurt"),
        (1, "tsp", "honey")
    ],
    "Cheese Toast": [
        (2, "slices", "bread"),
        (2, "slices", "cheese"),
        (1, "tsp", "butter")
    ],
    "Chicken Rice Bowl": [
        (150, "g", "chicken"),
        (1, "cup", "rice"),
        (0.5, "medium", "onion"),
        (0.5, "medium", "pepper")
    ],
    "Mashed Potatoes": [
        (2, "medium", "potato"),
        (0.25, "cup", "milk"),
        (1, "tbsp", "butter"),
        (0.25, "tsp", "salt")
    ],
    "Avocado Toast": [
        (2, "slices", "bread"),
        (1, "medium", "avocado"),
        (1, "tsp", "lemon juice"),
        (0.25, "tsp", "pepper")
    ]
}


# ==========================================
# 5. JSON FUNCTIONS
# ==========================================

def load_json(filename, default):
    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, type(default)):
                return data

            return default

    except (json.JSONDecodeError, OSError):
        return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_saved():
    data = load_json(SAVED_FILE, [])

    return [
        recipe for recipe in data
        if isinstance(recipe, dict) and recipe.get("name")
    ]


# ==========================================
# 6. RECIPE MATCHING FUNCTIONS
# ==========================================

def normalize(value):
    aliases = {
        "tomatoes": "tomato",
        "potatoes": "potato",
        "apples": "apple",
        "bananas": "banana",
        "eggs": "egg",
        "carrots": "carrot",
        "oranges": "orange"
    }

    value = value.lower().strip()

    return aliases.get(value, value)


def find_matches(selected):
    selected = set(normalize(x) for x in selected)
    results = []

    for recipe in RECIPES:
        ingredients = set(recipe["ingredients"])

        matched = ingredients.intersection(selected)
        missing = ingredients - selected

        if matched:
            percentage = round(
                len(matched) / len(ingredients) * 100
            )

            results.append({
                "recipe": recipe,
                "matched": sorted(matched),
                "missing": sorted(missing),
                "percentage": percentage
            })

    return sorted(
        results,
        key=lambda item: item["percentage"],
        reverse=True
    )


def recipe_is_saved(name):
    return any(
        recipe.get("name") == name
        for recipe in get_saved()
    )


# ==========================================
# 7. RECIPE DISPLAY FUNCTION
# ==========================================

def show_recipe(recipe, show_save=True):
    st.markdown("---")

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.image(
            recipe["image"],
            use_container_width=True
        )

    with col2:
        st.subheader(
            recipe["emoji"] + " " + recipe["name"]
        )

        st.write("⏱️", recipe["time"], "minutes")
        st.write("Category:", recipe["category"])
        st.write("**Ingredients:**")
        st.write(", ".join(recipe["ingredients"]))

        with st.expander("View Recipe Details"):
            st.write("**Preparation Steps:**")

            for i, step in enumerate(recipe["steps"], 1):
                st.write(f"{i}. {step}")

        if show_save:
            if recipe_is_saved(recipe["name"]):
                st.markdown(
                    "<span style='color:#d12f68;font-weight:700;'>❤️ Saved</span>",
                    unsafe_allow_html=True
                )
            else:
                if st.button(
                    "♡ Save Recipe",
                    key="save_" + recipe["name"]
                ):
                    saved = get_saved()

                    if not any(
                        item.get("name") == recipe["name"]
                        for item in saved
                    ):
                        saved.append(recipe)
                        save_json(SAVED_FILE, saved)

                    st.success("Recipe saved successfully!")
                    st.rerun()


# ==========================================
# 8. SESSION STATE
# ==========================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "search_done" not in st.session_state:
    st.session_state.search_done = False

if "scan_ingredients" not in st.session_state:
    st.session_state.scan_ingredients = []

if "view_recipe" not in st.session_state:
    st.session_state.view_recipe = None

if "carousel_index" not in st.session_state:
    st.session_state.carousel_index = 0

if "reviewed_scan" not in st.session_state:
    st.session_state.reviewed_scan = []


# ==========================================
# 9. SIDEBAR NAVIGATION
# ==========================================

PAGES = [
    "Home",
    "Find Recipes",
    "Recipe Ingredients",
    "Scan Ingredients",
    "Weekly Meal Planner",
    "Saved Recipes"
]

with st.sidebar:
    st.markdown(
        '<div class="sidebar-title">🍓 What\'s Cooking?</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">Your Kitchen, Your Inspiration ♡</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    for page in PAGES:
        if st.button(
            page,
            key="nav_" + page,
            use_container_width=True
        ):
            st.session_state.page = page
            st.rerun()


# ==========================================
# 10. HOME PAGE
# ==========================================

if st.session_state.page == "Home":

    left, right = st.columns(
        [1.2, 0.8],
        gap="large"
    )

    with left:
        st.markdown("""
        <div class="hero-box">
            <h1>What's Cooking?</h1>
            <p>
                Discover delicious ideas using the
                ingredients you already have.
            </p>
        </div>
        """, unsafe_allow_html=True)

        welcome_col, heart_col = st.columns([4, 1])

        with welcome_col:
            st.subheader("Welcome to your kitchen!")

        with heart_col:
            st.markdown("""
            <div style="
                font-size:55px;
                color:#e9a9c4;
                opacity:0.55;
                text-align:center;
                margin-top:-10px;">
                ♡
            </div>
            """, unsafe_allow_html=True)

        st.write(
            "Find recipes, organize your weekly meals, "
            "and save your favorite dishes."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Find Recipes",
                use_container_width=True
            ):
                st.session_state.page = "Find Recipes"
                st.rerun()

        with col2:
            if st.button(
                "Discover Ingredients",
                use_container_width=True
            ):
                st.session_state.page = "Recipe Ingredients"
                st.rerun()

    with right:
        if os.path.exists("home_cover.png"):
            st.image(
                "home_cover.png",
                use_container_width=True
            )
        else:
            st.info(
                "Add home_cover.png beside app.py "
                "to show your cover image."
            )

    st.markdown("---")
    st.subheader("A Little Recipe Inspiration 🍓")

    carousel_recipes = RECIPES[:3]
    current_index = st.session_state.carousel_index
    current_recipe = carousel_recipes[current_index]

    previous_col, image_col, next_col = st.columns([1, 6, 1])

    with previous_col:
        st.write("")
        st.write("")
        if st.button("❮", key="previous_recipe"):
            st.session_state.carousel_index = (
                current_index - 1
            ) % len(carousel_recipes)
            st.rerun()

    with image_col:
        st.image(
            current_recipe["image"],
            use_container_width=True
        )

        st.markdown(
            f"<h3 style='text-align:center;'>"
            f"{current_recipe['emoji']} {current_recipe['name']}"
            f"</h3>",
            unsafe_allow_html=True
        )

    with next_col:
        st.write("")
        st.write("")
        if st.button("❯", key="next_recipe"):
            st.session_state.carousel_index = (
                current_index + 1
            ) % len(carousel_recipes)
            st.rerun()


# ==========================================
# 11. FIND RECIPES PAGE
# ==========================================

elif st.session_state.page == "Find Recipes":

    st.title("Find Your Recipe 🍓")

    st.write(
        "Choose the ingredients you have "
        "and discover what you can make."
    )

    selected = st.multiselect(
        "Select your ingredients",
        INGREDIENTS,
        key="manual_ingredients"
    )

    if st.button(
        "Find Recipes",
        key="search_recipes"
    ):
        st.session_state.search_results = find_matches(selected)
        st.session_state.search_done = True
        st.session_state.view_recipe = None

    if st.session_state.search_done:
        if st.session_state.search_results:
            st.subheader("Recipe Suggestions")

            for item in st.session_state.search_results:
                recipe = item["recipe"]

                st.markdown(
                    f"### {recipe['emoji']} {recipe['name']}"
                )

                st.caption(
                    f"⏱️ {recipe['time']} minutes"
                )

                st.write(
                    "Matched ingredients:",
                    ", ".join(item["matched"])
                )

                st.progress(
                    item["percentage"] / 100
                )

                st.write(
                    f"**{item['percentage']}% Match**"
                )

                if item["missing"]:
                    st.write(
                        "Still needed:",
                        ", ".join(item["missing"])
                    )
                else:
                    st.success(
                        "You have all the ingredients!"
                    )

                if st.button(
                    "View Recipe Details",
                    key="view_" + recipe["name"]
                ):
                    st.session_state.view_recipe = recipe["name"]

                if st.session_state.view_recipe == recipe["name"]:
                    show_recipe(recipe)

        else:
            st.warning(
                "No matching recipes found. "
                "Try selecting more ingredients."
            )


# ==========================================
# 12. RECIPE INGREDIENTS PAGE
# ==========================================

elif st.session_state.page == "Recipe Ingredients":

    st.title("Discover Recipe Ingredients 🍓")

    st.write(
        "Choose a dish and discover everything "
        "you need to prepare it."
    )

    recipe_names = [
        recipe["name"] for recipe in RECIPES
    ]

    selected_recipe = st.selectbox(
        "Choose your recipe",
        recipe_names,
        key="ingredients_recipe"
    )

    servings = st.selectbox(
        "How many people?",
        list(range(1, 11)),
        index=1,
        key="recipe_servings"
    )

    recipe = next(
        item for item in RECIPES
        if item["name"] == selected_recipe
    )

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(
            recipe["image"],
            use_container_width=True
        )

    with col2:
        st.subheader(
            recipe["emoji"] + " " + recipe["name"]
        )

        st.write("⏱️", recipe["time"], "minutes")
        st.write("👥 Servings:", servings)

        st.markdown("### Ingredients You Need")

        base_ingredients = QUANTITIES.get(
            recipe["name"], []
        )

        for amount, unit, ingredient in base_ingredients:
            total = amount * servings / 2
            amount_text = f"{total:g}"

            st.write(
                f"✓ {amount_text} {unit} {ingredient}"
            )

        st.caption(
            "Quantities are suggested estimates "
            "and may be adjusted to taste."
        )

    st.markdown("---")

    with st.expander("View Preparation Steps"):
        for i, step in enumerate(recipe["steps"], 1):
            st.write(f"{i}. {step}")


# ==========================================
# 13. SCAN INGREDIENTS PAGE - GEMINI VISION
# ==========================================

elif st.session_state.page == "Scan Ingredients":

    st.title("Scan Your Ingredients 📸")

    st.write(
        "Upload a photo and let AI recognize "
        "the ingredients you have."
    )

    st.markdown("### 1. Upload & Detect")

    uploaded_image = st.file_uploader(
        "Choose an image of your ingredients",
        type=["jpg", "jpeg", "png"],
        key="ingredient_photo"
    )

    if uploaded_image is not None:

        image = Image.open(uploaded_image).convert("RGB")

        st.image(
            image,
            caption="Your uploaded ingredients",
            use_container_width=True
        )

        if st.button(
            "Detect Ingredients",
            use_container_width=True
        ):

            try:
                with st.spinner(
                    "AI is analyzing your ingredients..."
                ):

                    # Read the API key from Streamlit secrets
                    api_key = st.secrets["GEMINI_API_KEY"]

                    client = genai.Client(
                        api_key=api_key
                    )

                    prompt = f"""
                    Carefully analyze this food ingredients photo.

                    Identify ALL clearly visible food ingredients.
                    Look at the entire image.
                    Identify different ingredients even if they are
                    close together or touching.

                    Do not guess ingredients that are not visible.
                    Do not include plates, bags, containers or dishes.

                    Only return ingredients from this list:
                    {", ".join(INGREDIENTS)}

                    Return valid JSON only in this format:
                    {{"ingredients": ["tomato", "carrot", "broccoli"]}}

                    Use English ingredient names.
                    Return an empty list if no supported ingredients
                    are clearly visible.
                    """

                    image_bytes = uploaded_image.getvalue()

                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=[
                            prompt,
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type=uploaded_image.type
                            )
                        ],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )

                    response_text = response.text

                    if not response_text:
                        raise ValueError(
                            "Gemini returned an empty response."
                        )

                    response_text = response_text.strip()

                    # Remove markdown code fences if present
                    response_text = re.sub(
                        r"^```(?:json)?\s*|\s*```$",
                        "",
                        response_text
                    )

                    result = json.loads(response_text)

                    detected = result.get("ingredients", [])

                    aliases = {
                        "tomatoes": "tomato",
                        "potatoes": "potato",
                        "apples": "apple",
                        "bananas": "banana",
                        "eggs": "egg",
                        "carrots": "carrot",
                        "oranges": "orange",
                        "bell pepper": "pepper",
                        "capsicum": "pepper",
                        "red onion": "onion",
                        "green onion": "onion",
                        "chicken breast": "chicken"
                    }

                    detected_list = []

                    for item in detected:

                        if not isinstance(item, str):
                            continue

                        item = item.lower().strip()
                        item = aliases.get(item, item)

                        if item in INGREDIENTS:
                            if item not in detected_list:
                                detected_list.append(item)

                    detected_list.sort()

                    st.session_state.scan_ingredients = detected_list
                    st.session_state.reviewed_scan = detected_list

                if detected_list:
                    st.success(
                        f"Successfully detected "
                        f"{len(detected_list)} ingredient(s)!"
                    )

                    st.write("Detected ingredients:")
                    st.write(", ".join(detected_list))

                else:
                    st.warning(
                        "No supported ingredients were recognized. "
                        "You can add them manually below."
                    )

            except Exception as error:

                st.error("Could not analyze the image.")

                error_text = str(error)

                if "503" in error_text or "UNAVAILABLE" in error_text:
                    st.warning(
                        "Gemini is temporarily busy. "
                        "Please try again later."
                    )

                elif "GEMINI_API_KEY" in error_text:
                    st.warning(
                        "Gemini API key was not found in secrets.toml."
                    )

                else:
                    st.caption(error_text)

    st.markdown("---")
    st.markdown("### 2. Edit Your Ingredients")

    st.write(
        "Review the detected ingredients. "
        "Remove incorrect items or add missing ones."
    )

    chosen_scan = st.multiselect(
        "Your final ingredient list",
        INGREDIENTS,
        key="reviewed_scan"
    )

    st.caption(
        "You can add ingredients manually if they were not detected."
    )

    if st.button(
        "Find Recipes With These Ingredients",
        use_container_width=True
    ):

        if not chosen_scan:
            st.warning(
                "Please add at least one ingredient."
            )

        else:
            st.session_state.search_results = find_matches(
                chosen_scan
            )

            st.session_state.search_done = True
            st.session_state.view_recipe = None
            st.session_state.page = "Find Recipes"

            st.rerun()


# ==========================================
# 14. WEEKLY MEAL PLANNER
# ==========================================

elif st.session_state.page == "Weekly Meal Planner":

    st.title("Weekly Meal Planner 🗓️")

    days = [
        "Saturday",
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ]

    meals = [
        "Breakfast",
        "Lunch",
        "Dinner"
    ]

    meal_plan = load_json(
        MEAL_FILE,
        {}
    )

    st.write(
        "Plan your meals for the whole week."
    )

    for day in days:
        with st.expander(day):

            if day not in meal_plan:
                meal_plan[day] = {}

            for meal in meals:
                options = ["Not selected"] + [
                    recipe["name"] for recipe in RECIPES
                ]

                current = meal_plan[day].get(
                    meal,
                    "Not selected"
                )

                if current not in options:
                    current = "Not selected"

                choice = st.selectbox(
                    meal,
                    options,
                    index=options.index(current),
                    key=f"{day}_{meal}"
                )

                if choice == "Not selected":
                    meal_plan[day].pop(meal, None)
                else:
                    meal_plan[day][meal] = choice

    if st.button("Save Weekly Plan"):
        save_json(
            MEAL_FILE,
            meal_plan
        )

        st.success(
            "Your weekly meal plan has been saved!"
        )

    st.markdown("---")
    st.subheader("Your Saved Weekly Plan")

    meal_plan = load_json(
        MEAL_FILE,
        {}
    )

    for day in days:
        if meal_plan.get(day):
            st.markdown(f"**{day}**")

            for meal, recipe_name in meal_plan[day].items():
                st.write(
                    f"- {meal}: {recipe_name}"
                )


# ==========================================
# 15. SAVED RECIPES PAGE
# ==========================================

elif st.session_state.page == "Saved Recipes":

    st.title("♡ My Saved Recipes")

    saved = get_saved()

    if not saved:
        st.info(
            "You haven't saved any recipes yet."
        )

    else:
        st.write(
            f"You have saved {len(saved)} recipe(s)."
        )

        for recipe in saved:
            col1, col2 = st.columns([1, 2])

            with col1:
                if recipe.get("image"):
                    st.image(
                        recipe["image"],
                        use_container_width=True
                    )
                else:
                    st.caption("No image available")

            with col2:
                st.subheader(recipe["name"])

                st.write(
                    "⏱️",
                    recipe.get("time", ""),
                    "minutes"
                )

                with st.expander("View Recipe"):
                    st.write("**Ingredients:**")

                    st.write(
                        ", ".join(
                            recipe.get("ingredients", [])
                        )
                    )

                    st.write("**Steps:**")

                    for i, step in enumerate(
                        recipe.get("steps", []), 1
                    ):
                        st.write(f"{i}. {step}")

                if st.button(
                    "Remove Recipe",
                    key="remove_" + recipe["name"]
                ):
                    saved = [
                        item for item in get_saved()
                        if item.get("name") != recipe["name"]
                    ]

                    save_json(
                        SAVED_FILE,
                        saved
                    )

                    st.success("Recipe removed.")
                    st.rerun()

            st.markdown("---")


# ==========================================
# 16. FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    ♡ A Little Taste of Happiness ♡
</div>
""", unsafe_allow_html=True)
