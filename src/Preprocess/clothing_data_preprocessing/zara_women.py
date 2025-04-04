import pandas as pd
import glob
import os
import requests
import ast

target_categories = {
    "SPECIAL PRICES", "WAISTCOATS_GILETS", "BASICS", "BLAZERS",
    "DRESSES_JUMPSUITS", "JACKETS", "KNITWEAR", "SHIRTS", "SHOES"
}

download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "CLOTHES/WOMEN")
os.makedirs(download_dir, exist_ok=True)


csv_files = glob.glob(os.path.join(r"~\zara_data\Women", "*.csv"))

dataframes = []


def get_inr_to_try_exchange_rate():
    url = 'https://api.exchangerate-api.com/v4/latest/INR'
    response = requests.get(url)
    data = response.json()
    return data['rates']['TRY']

exchange_rate = get_inr_to_try_exchange_rate()
#print(exchange_rate)


# clean and convert price string to float
def clean_price(price_str):
    try:
        cleaned_price = price_str.replace('â‚¹', '').replace('₹', '').replace(',', '').strip()
        return float(cleaned_price)
    except ValueError:
        return None
    
# downloading images
def download_image(url, save_path):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Image downloaded: {save_path}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False
    
    
category_image_count = {}


# loop through each file, process, and append to list
for file in csv_files:
    df = pd.read_csv(file)
    #print(df.head())
    
    file_name = os.path.splitext(os.path.basename(file))[0]
    df['category'] = file_name
    
    if file_name not in target_categories:
        continue
    
    if 'Price' in df.columns:
        df['Price'] = df['Price'].astype(str).apply(clean_price).apply(lambda x: round(x * exchange_rate, 2))   # convert prices to try

    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
        
    # downloading imgs (max 30 per category)
    if 'Product_Image' in df.columns:
        for index, row in df.iterrows():
            category = row['category']
            
            if category_image_count.get(category, 0) >= 30:
                continue
            
            try:
                image_list = ast.literal_eval(row['Product_Image']) 
                for img_dict in image_list:
                    for url, description in img_dict.items():
                        if category_image_count.get(category, 0) >= 30:
                            break
                        
                        
                        image_name = f"{category}_{index}_{description.replace(' ', '_')}.jpg"
                        save_path = os.path.join(download_dir, image_name)
                        
                        if download_image(url, save_path):
                            category_image_count[category] = category_image_count.get(category, 0) + 1

            except Exception as e:
                print(f"Error processing images for row {index}: {e}")
    
    dataframes.append(df)


# add all dataframes vertically
combined_df = pd.concat(dataframes, ignore_index=True)

combined_df.to_csv("zara_women.csv", index=True, index_label="Index")