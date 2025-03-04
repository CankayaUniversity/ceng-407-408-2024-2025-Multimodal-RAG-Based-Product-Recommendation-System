import pandas as pd
import re

def is_english(text):
    turkish_chars = set("çğıöşüÇĞİÖŞÜ")
    return not any(char in turkish_chars for char in text)

def extract_english_ingredients(text):
    if pd.isna(text):
        return []
    
    pattern = r"([\w\s\-\(\)/]+(?:mg|g|µg|mcg|ml)[\w\s\-\(\)/]*)"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    
    english_matches = [match.strip() for match in matches if is_english(match)]
    return english_matches

df = pd.read_excel('urunliste.xlsx')

columns_to_drop = [
    'Stok Kodu', 'Barkod', 'Grup Kodu', 'Varyant', 'KDV Oran', 'Liste Fiyatı Not',
    'Maliyet', 'Maliyet Not', 'Ortalama Maliyet', 'Ek İskonto', 'Desi', 'Miat Tarihi',
    'Adet', 'Son Sayım Tarihi', 'Raf No', 'GTİP', 'Miatlı'
]


df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

df["English Ingredients"] = df["Ürün Açıklaması"].apply(extract_english_ingredients)

df = df[df["English Ingredients"].apply(len) > 0]

df["English Ingredients"] = df["English Ingredients"].apply(lambda ing_list: ", ".join(ing_list))

output_file = "prodlist.xlsx"
df.to_excel(output_file, index=False)


