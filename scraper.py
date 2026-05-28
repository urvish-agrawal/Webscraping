import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time

# =========================================================
# SNAPDEAL MEN'S SPORTS SHOES WEB SCRAPER
# =========================================================

# URL
BASE_URL = "https://www.snapdeal.com/products/mens-footwear-sports-shoes"

# Headers

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Store all products
products = []

# Number of pages to scrape
NUM_PAGES = 5

# =========================================================
# SCRAPING
# =========================================================

for page in range(1, NUM_PAGES + 1):

    print(f"Scraping Page {page}...")

    params = {
        "sort": "plrty",
        "page": page
    }

    try:
        response = requests.get(
            BASE_URL,
            headers=headers,
            params=params,
            timeout=10
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page}: {e}")
        continue

    soup = BeautifulSoup(response.text, "lxml")

    # Find all product containers
    items = soup.find_all("div", class_="product-tuple-listing")

    print(f"Found {len(items)} products on page {page}")

    # -----------------------------------------------------
    # LOOP THROUGH PRODUCTS
    # -----------------------------------------------------

    for item in items:

        # =================================================
        # PRODUCT NAME
        # =================================================

        name_tag = item.find("p", class_="product-title")

        product_name = (
            name_tag.text.strip()
            if name_tag
            else "N/A"
        )

        # =================================================
        # BRAND
        # =================================================

        if product_name != "N/A":
            brand = product_name.split()[0]
        else:
            brand = "Unknown"

        # =================================================
        # DISCOUNTED PRICE
        # =================================================

        price_tag = item.find(
            "span",
            class_="lfloat product-price"
        )

        discounted_price = (
            price_tag.get("data-price")
            if price_tag and price_tag.get("data-price")
            else "0"
        )

        # =================================================
        # ORIGINAL PRICE
        # =================================================

        original_price_tag = item.find(
            "span",
            class_="lfloat product-desc-price strike"
        )

        if original_price_tag:

            original_price = (
                original_price_tag.text
                .replace("Rs.", "")
                .replace(",", "")
                .strip()
            )

        else:
            original_price = discounted_price

        # =================================================
        # DISCOUNT
        # =================================================

        discount_tag = item.find(
            "div",
            class_="product-discount"
        )

        discount = (
            discount_tag.text.strip()
            if discount_tag
            else "0% Off"
        )

       # =================================================
        # RATING
        # =================================================

        rating = "N/A"

        rating_tag = item.find("div", class_="filled-stars")

        if rating_tag:

            style = rating_tag.get("style", "")

            try:
                # Extract percentage value
                width = style.replace("width:", "").replace("%", "").strip()

                width = float(width)

                # Convert percentage to rating out of 5
                rating = round((width / 100) * 5, 1)

            except Exception as e:
                rating = "N/A"

        # =================================================
        # REVIEWS
        # =================================================

        review_tag = item.find(
            "p",
            class_="product-rating-count"
        )

        if review_tag:

            reviews = (
                review_tag.text
                .replace("(", "")
                .replace(")", "")
                .strip()
            )

        else:
            reviews = "0"

        # =================================================
        # CONVERT PRICES TO INTEGER
        # =================================================

        try:
            discounted_price = int(float(discounted_price))
        except:
            discounted_price = 0

        try:
            original_price = int(float(original_price))
        except:
            original_price = 0

        # =================================================
        # STORE DATA
        # =================================================

        products.append({
            "Product Name": product_name,
            "Brand": brand,
            "Original Price": original_price,
            "Discounted Price": discounted_price,
            "Discount": discount,
            "Rating": rating,
            "Reviews": reviews
        })

    # Delay to avoid blocking
    time.sleep(2)

# =========================================================
# CREATE DATAFRAME
# =========================================================

df = pd.DataFrame(products)

# =========================================================
# SAVE CSV
# =========================================================

csv_file = "snapdeal_mens_sports_shoes.csv"

df.to_csv(csv_file, index=False)

print("\n===================================")
print(f"Data saved to {csv_file}")
print("===================================")

# =========================================================
# DISPLAY FIRST 5 ROWS
# =========================================================

print("\nFirst 5 Products:\n")

print(df.head())

# =========================================================
# DATA ANALYSIS
# =========================================================

print("\n===================================")
print("DATA ANALYSIS")
print("===================================")

# ---------------------------------------------------------
# TOP BRANDS
# ---------------------------------------------------------

top_brands = df["Brand"].value_counts().head(10)

print("\nTop Brands:\n")
print(top_brands)

# ---------------------------------------------------------
# CONVERT RATING TO NUMERIC
# ---------------------------------------------------------

df["Rating"] = pd.to_numeric(
    df["Rating"],
    errors="coerce"
)

# =========================================================
# VISUALIZATION SETTINGS
# =========================================================

sns.set_style("whitegrid")

# =========================================================
# TOP BRANDS CHART
# =========================================================

if not top_brands.empty:

    plt.figure(figsize=(10, 6))

    top_brands.plot(kind="bar")

    plt.title("Top 10 Brands")

    plt.xlabel("Brand")

    plt.ylabel("Number of Products")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig("images/top_brands.png")

    plt.show()

else:
    print("No brand data available for plotting.")

# =========================================================
# PRICE DISTRIBUTION
# =========================================================

plt.figure(figsize=(10, 6))

sns.histplot(
    df["Discounted Price"],
    bins=20
)

plt.title("Price Distribution")

plt.xlabel("Discounted Price")

plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig("images/price_distribution.png")

plt.show()

# =========================================================
# TOP RATED BRANDS
# =========================================================

avg_rating = (
    df.groupby("Brand")["Rating"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

if not avg_rating.empty:

    plt.figure(figsize=(10, 6))

    avg_rating.plot(kind="bar")

    plt.title("Top Rated Brands")

    plt.xlabel("Brand")

    plt.ylabel("Average Rating")

    plt.xticks(rotation=45)

    plt.tight_layout()
    
    plt.savefig("images/top_rated_brands.png")

    plt.show()

else:
    print("No rating data available.")

# =========================================================
# MOST EXPENSIVE PRODUCTS
# =========================================================

print("\nTop 5 Most Expensive Products:\n")

top_expensive = df.sort_values(
    by="Discounted Price",
    ascending=False
).head(5)

print(
    top_expensive[
        [
            "Product Name",
            "Brand",
            "Discounted Price"
        ]
    ]
)

# =========================================================
# DISCOUNT ANALYSIS
# =========================================================

print("\nAverage Discounted Price:")

print(round(df["Discounted Price"].mean(), 2))

print("\nMaximum Discounted Price:")

print(df["Discounted Price"].max())

print("\nMinimum Discounted Price:")

print(df["Discounted Price"].min())

# =========================================================
# FINISHED
# =========================================================

print("\n===================================")
print("PROJECT COMPLETED SUCCESSFULLY!")
print("===================================")