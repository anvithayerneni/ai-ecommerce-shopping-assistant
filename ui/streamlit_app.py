import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://localhost:8000"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI E-Commerce Shopping Assistant",
    page_icon="🛍️",
    layout="wide",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .subtitle {
            font-size: 18px;
            color: #666;
            margin-bottom: 30px;
        }

        .product-card {
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #ddd;
            margin-bottom: 15px;
            background-color: #fafafa;
        }

        .product-name {
            font-size: 22px;
            font-weight: 700;
        }

        .product-price {
            font-size: 20px;
            font-weight: 600;
        }

        .score {
            font-size: 14px;
            color: #666;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🛍️ AI E-Commerce Shopping Assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Search, discover, compare, and get personalized product recommendations
        using hybrid AI-powered retrieval and recommendation models.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    top_k = st.slider(
        "Number of recommendations",
        min_value=1,
        max_value=10,
        value=5,
    )

    st.divider()

    st.markdown("### 🤖 AI Pipeline")

    st.write("🔎 Product Search")
    st.write("🧠 Semantic Embeddings")
    st.write("🏷️ Category Similarity")
    st.write("🎯 Use-Case Similarity")
    st.write("📊 Hybrid Ranking")
    st.write("💬 Recommendation Explanation")


# ============================================================
# SEARCH INPUT
# ============================================================

st.subheader("What are you looking for?")

query = st.text_input(
    "Shopping query",
    placeholder="Example: laptop for programming under $1000",
    label_visibility="collapsed",
)


# ============================================================
# SEARCH BUTTON
# ============================================================

search_clicked = st.button(
    "🔍 Find Products",
    type="primary",
    use_container_width=True,
)


# ============================================================
# API CALL
# ============================================================

if search_clicked:

    if not query.strip():

        st.warning(
            "Please enter a shopping query."
        )

    else:

        with st.spinner(
            "Finding the best products..."
        ):

            try:

                response = requests.get(
                    f"{API_URL}/assistant/recommend",
                    params={
                        "q": query,
                        "top_k": top_k,
                    },
                    timeout=60,
                )

                response.raise_for_status()

                data = response.json()

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the FastAPI backend. "
                    "Make sure the API is running on port 8000."
                )

                st.stop()

            except requests.exceptions.RequestException as exc:

                st.error(
                    f"API request failed: {exc}"
                )

                st.stop()

            except ValueError:

                st.error(
                    "The API returned an invalid response."
                )

                st.stop()


        # ====================================================
        # ASSISTANT RESPONSE
        # ====================================================

        assistant_response = data.get(
            "assistant_response"
        )

        if assistant_response:

            st.subheader("🤖 Shopping Assistant")

            st.info(
                assistant_response
            )


        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        recommendations = data.get(
            "recommendations",
            [],
        )

        st.subheader(
            f"🛒 Recommended Products ({len(recommendations)})"
        )


        if not recommendations:

            st.warning(
                "No matching products were found."
            )

        else:

            for index, item in enumerate(
                recommendations,
                start=1,
            ):

                product = item.get(
                    "product",
                    {},
                )

                name = product.get(
                    "name",
                    "Unknown Product",
                )

                brand = product.get(
                    "brand"
                )

                category = product.get(
                    "category"
                )

                price = product.get(
                    "price"
                )

                rating = product.get(
                    "rating"
                )

                score = item.get(
                    "score"
                )

                match_reasons = item.get(
                    "match_reasons",
                    [],
                )


                # --------------------------------------------
                # PRODUCT CARD
                # --------------------------------------------

                st.markdown(
                    '<div class="product-card">',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<div class="product-name">'
                    f'{index}. {name}'
                    f'</div>',
                    unsafe_allow_html=True,
                )


                # Brand / category

                details = []

                if brand:
                    details.append(
                        f"**Brand:** {brand}"
                    )

                if category:
                    details.append(
                        f"**Category:** {category}"
                    )

                if details:

                    st.markdown(
                        " • ".join(details)
                    )


                # Price / rating

                col1, col2, col3 = st.columns(3)


                with col1:

                    if price is not None:

                        st.metric(
                            "Price",
                            f"${price:,.2f}",
                        )


                with col2:

                    if rating is not None:

                        st.metric(
                            "Rating",
                            f"⭐ {rating}",
                        )


                with col3:

                    if score is not None:

                        st.metric(
                            "Match Score",
                            f"{score:.3f}",
                        )


                # --------------------------------------------
                # MATCH REASONS
                # --------------------------------------------

                if match_reasons:

                    st.markdown(
                        "**Why this product?**"
                    )

                    for reason in match_reasons:

                        st.write(
                            f"✓ {reason}"
                        )


                # --------------------------------------------
                # EXTRA PRODUCT INFORMATION
                # --------------------------------------------

                features = product.get(
                    "features"
                )

                use_cases = product.get(
                    "use_cases"
                )

                target_audience = product.get(
                    "target_audience"
                )


                with st.expander(
                    "View product details"
                ):

                    if features:

                        st.markdown(
                            f"**Features:** {features}"
                        )

                    if use_cases:

                        st.markdown(
                            f"**Use cases:** {use_cases}"
                        )

                    if target_audience:

                        st.markdown(
                            f"**Target audience:** "
                            f"{target_audience}"
                        )


                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )


# ============================================================
# DEMO SECTION
# ============================================================

if not search_clicked:

    st.divider()

    st.subheader("💡 Try these examples")

    examples = [
        "laptop for programming",
        "running shoes for training",
        "noise cancelling headphones",
        "smartphone for photography",
        "laptop under $1000",
    ]

    cols = st.columns(len(examples))

    for col, example in zip(
        cols,
        examples,
    ):

        with col:

            st.caption(
                example
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI E-Commerce Shopping Assistant • "
    "FastAPI + Streamlit + Semantic Search + Hybrid Recommendations"
)