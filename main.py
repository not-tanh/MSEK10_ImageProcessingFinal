from PIL import Image
import streamlit as st

from search_engine import SearchEngine

st.set_page_config(page_title='Product Searching Demo', page_icon='frame_with_picture', layout='wide')


@st.cache(hash_funcs={SearchEngine: lambda _: None})
def load_search_engine():
    return SearchEngine()


def make_clickable(link, text):
    text = text.replace('"', '\'')
    subtext = text[:min(20, len(text))] + '...'
    return f'<a target="_blank" href="{link}" title="{text}">{subtext}</a>'


st.title('Product Searching Demo')
search_engine = load_search_engine()

with st.form('search_form'):
    k = st.slider('Number of products to display', min_value=5, max_value=50)
    uploaded_image = st.file_uploader('Upload an img of the product you want to search')

    submitted = st.form_submit_button('Search')

    if uploaded_image is not None:
        image = Image.open(uploaded_image).convert('RGB')
        w, h = image.size
        if w > 300:
            displayed_image = image.resize((300, int(h / (w / 300))))
        else:
            displayed_image = image
        st.image(displayed_image, caption='Your input img')

        if submitted:
            with st.spinner('Wait for it...'):
                search_results = search_engine(image, k=k)
            st.success('Done')
            columns = st.columns(5)
            for i, result in enumerate(search_results):
                columns[i % 5].image(Image.open(result['image_path']))

                columns[i % 5].write(make_clickable(result['url'], result['name']), unsafe_allow_html=True)
                if not result['price']:
                    result['price'] = 'N/A'
                columns[i % 5].write(result['price'])
