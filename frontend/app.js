const API_BASE_URL = "http://127.0.0.1:8000";

const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");

const loading = document.getElementById("loading");
const error = document.getElementById("error");
const errorMessage = document.getElementById("errorMessage");

const results = document.getElementById("results");
const productGrid = document.getElementById("productGrid");

const resultsTitle = document.getElementById("resultsTitle");
const resultCount = document.getElementById("resultCount");


function showLoading() {

    loading.classList.remove("hidden");

    error.classList.add("hidden");

    results.classList.add("hidden");
}


function hideLoading() {

    loading.classList.add("hidden");
}


function showError(message) {

    hideLoading();

    results.classList.add("hidden");

    errorMessage.textContent = message;

    error.classList.remove("hidden");
}


function getProductIcon(category) {

    const value = (category || "").toLowerCase();

    if (value.includes("laptop")) {
        return "💻";
    }

    if (
        value.includes("headphone") ||
        value.includes("audio")
    ) {
        return "🎧";
    }

    if (
        value.includes("shoe") ||
        value.includes("running")
    ) {
        return "👟";
    }

    if (
        value.includes("phone") ||
        value.includes("smartphone")
    ) {
        return "📱";
    }

    if (value.includes("backpack")) {
        return "🎒";
    }

    if (value.includes("coffee")) {
        return "☕";
    }

    return "🛍️";
}


function formatPrice(price) {

    if (price === null || price === undefined) {
        return "Price unavailable";
    }

    return `$${Number(price).toFixed(2)}`;
}


function splitValues(value) {

    if (!value) {
        return [];
    }

    if (Array.isArray(value)) {
        return value;
    }

    return String(value)
        .split(",")
        .map(item => item.trim())
        .filter(Boolean);
}


function createProductCard(product) {

    const card = document.createElement("article");

    card.className = "product-card";


    const icon = document.createElement("div");

    icon.className = "product-icon";

    icon.textContent =
        getProductIcon(product.category);


    const brand = document.createElement("div");

    brand.className = "product-brand";

    brand.textContent =
        product.brand || "Product";


    const name = document.createElement("div");

    name.className = "product-name";

    name.textContent =
        product.name || "Unnamed Product";


    const description =
        document.createElement("p");

    description.className =
        "product-description";

    description.textContent =
        product.description ||
        "Recommended based on your shopping request.";


    const meta =
        document.createElement("div");

    meta.className =
        "product-meta";


    const price =
        document.createElement("div");

    price.className =
        "price";

    price.textContent =
        formatPrice(product.price);


    const rating =
        document.createElement("div");

    rating.className =
        "rating";

    if (
        product.rating !== null &&
        product.rating !== undefined
    ) {

        rating.textContent =
            `⭐ ${product.rating}`;

    } else {

        rating.textContent =
            "Rating unavailable";

    }


    meta.appendChild(price);

    meta.appendChild(rating);


    const tags =
        document.createElement("div");

    tags.className =
        "product-tags";


    const values = [
        ...splitValues(product.category),
        ...splitValues(product.use_cases),
        ...splitValues(product.tags)
    ];


    const uniqueValues = [
        ...new Set(values)
    ].slice(0, 4);


    uniqueValues.forEach(value => {

        const tag =
            document.createElement("span");

        tag.className =
            "tag";

        tag.textContent =
            value;

        tags.appendChild(tag);

    });


    card.appendChild(icon);

    card.appendChild(brand);

    card.appendChild(name);

    card.appendChild(description);

    card.appendChild(meta);

    card.appendChild(tags);


    return card;
}


function renderProducts(products, query) {

    productGrid.innerHTML = "";


    if (
        !products ||
        products.length === 0
    ) {

        showError(
            "No products were found for this request."
        );

        return;

    }


    products.forEach(product => {

        const card =
            createProductCard(product);

        productGrid.appendChild(card);

    });


    resultsTitle.textContent =
        `Products matching "${query}"`;

    resultCount.textContent =
        `${products.length} results`;


    results.classList.remove("hidden");
}


async function searchProducts(query) {

    const trimmedQuery =
        query.trim();


    if (trimmedQuery.length < 2) {

        showError(
            "Please enter at least 2 characters."
        );

        return;

    }


    showLoading();


    try {

        const url =
            `${API_BASE_URL}/assistant/recommend` +
            `?q=${encodeURIComponent(trimmedQuery)}` +
            `&top_k=5`;


        const response =
            await fetch(url);


        if (!response.ok) {

            throw new Error(
                `API request failed (${response.status})`
            );

        }


        const data =
            await response.json();


        hideLoading();


        /*
         * RecommendationResponse is expected to contain
         * the recommended products.
         *
         * The frontend checks several common field names
         * so it can remain compatible with the current
         * response structure.
         */

        const products =
            data.recommendations ||
            data.products ||
            data.results ||
            [];


        renderProducts(
            products,
            trimmedQuery
        );


    } catch (err) {

        console.error(err);

        showError(
            "Could not connect to the shopping assistant API. " +
            "Make sure FastAPI is running on port 8000."
        );

    }

}


searchButton.addEventListener(
    "click",
    () => {

        searchProducts(
            searchInput.value
        );

    }
);


searchInput.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            searchProducts(
                searchInput.value
            );

        }

    }
);


document
    .querySelectorAll(".suggestion")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const query =
                    button.dataset.query;

                searchInput.value =
                    query;

                searchProducts(query);

            }
        );

    });
