# 👶 My Baby Name Generator

An interactive web app to discover baby names similar to the ones you like, with detailed information on their origin, meaning, and popularity.

---

## 🚀 Features

- Smart name suggestions based on embeddings and cosine similarity
- Filter by gender (M/F)
- Multi-select reference names
- Clean and elegant mosaic layout with styled cards
- Add and manage favorite names in session
- Popularity displayed with progress bars
- Easy sharing via WhatsApp, Messenger, X (formerly Twitter), and Facebook

---

## 🛠️ Installation

1. Clone this repository  
```bash
git clone https://github.com/your-username/my-baby-name-generator.git
cd my-baby-name-generator

2. Install dependencies (preferably in a virtual environment)

```bash
pip install -r requirements.txt
```
3. Prepare the CSV file prenoms_embed_dedup.csv containing names, embeddings, gender, popularity, origin, meaning, etc.

## ⚙️ Usage
Run the Streamlit app:

```bash
streamlit run app.py
```

### How to use the UI:
Select one or multiple reference names

Choose gender (M or F)

Click "Generate Suggestions" to see similar baby names

Add names to your favorites to easily find them later

Share your favorite results with integrated social buttons

## 📁 Expected Data Structure
The CSV file `prenoms_embed_dedup.csv` should contain at least the following columns:

| Column           | Description                             |
|------------------|---------------------------------------|
| `name`           | Baby name (string)                     |
| `embedding`      | Embedding vector stored as a list/array |
| `gender`         | Gender (M or F)                       |
| `total_popularity`| Total number of births                |
| `origin`         | Name origin                          |
| `meaning`        | Name meaning                        |


## 🎨 Styling
Card styles are defined via CSS injected using st.markdown. Modify the <style> section in the app code to customize colors, shadows, borders, etc.

## 🧠 How it works
Uses name embeddings and cosine similarity for smart matching

Averages embeddings of selected names as a reference vector

Returns the most similar and popular names sorted accordingly

## 🔗 Social Sharing
Share your name lists on WhatsApp, Facebook Messenger, X (formerly Twitter), and Facebook using dynamically generated URLs and sleek icons.

