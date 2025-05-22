import os
import sys
import pickle
import streamlit as st
import numpy as np
from books_recommender.logger.log import logging
from books_recommender.config.configuration import AppConfiguration
from books_recommender.pipeline.training_pipeline import TrainingPipeline
from books_recommender.exception.exception_handler import AppException
from urllib.error import URLError
from PIL import Image
import requests
from io import BytesIO

class Recommendation:
    def __init__(self,app_config = AppConfiguration()):
        try:
            self.recommendation_config= app_config.get_recommendation_config()
        except Exception as e:
            raise AppException(e, sys) from e

    def fetch_poster(self,suggestion):
        try:
            book_name = []
            ids_index = []
            poster_url = []
            book_pivot =  pickle.load(open(self.recommendation_config.book_pivot_serialized_objects,'rb'))
            final_rating =  pickle.load(open(self.recommendation_config.final_rating_serialized_objects,'rb'))

            for book_id in suggestion:
                book_name.append(book_pivot.index[book_id])

            for name in book_name[0]: 
                ids = np.where(final_rating['title'] == name)[0][0]
                ids_index.append(ids)

            for idx in ids_index:
                url = final_rating.iloc[idx]['image_url']
                poster_url.append(url)

            return poster_url
        
        except Exception as e:
            raise AppException(e, sys) from e

    def recommend_book(self,book_name):
        try:
            books_list = []
            model = pickle.load(open(self.recommendation_config.trained_model_path,'rb'))
            book_pivot =  pickle.load(open(self.recommendation_config.book_pivot_serialized_objects,'rb'))
            book_id = np.where(book_pivot.index == book_name)[0][0]
            distance, suggestion = model.kneighbors(book_pivot.iloc[book_id,:].values.reshape(1,-1), n_neighbors=6 )

            poster_url = self.fetch_poster(suggestion)
            
            for i in range(len(suggestion)):
                    books = book_pivot.index[suggestion[i]]
                    for j in books:
                        books_list.append(j)
            return books_list , poster_url   
        
        except Exception as e:
            raise AppException(e, sys) from e

    def train_engine(self):
        try:
            with st.spinner('Training in progress... Please wait...'):
                obj = TrainingPipeline()
                obj.start_training_pipeline()
            st.success("Training Completed!")
            st.balloons()
            logging.info(f"Training completed successfully!")
        except URLError as e:
            st.error(f"⚠️ Training failed: Could not download data. Please check your internet connection.")
            st.info("ℹ️ Using pre-trained model and existing data instead.")
            logging.error(f"Network error during training: {e}")
        except Exception as e:
            st.error(f"⚠️ Training failed: {str(e)}")
            st.info("ℹ️ Using pre-trained model and existing data instead.")
            logging.error(f"Training failed: {str(e)}")

    def recommendations_engine(self,selected_books):
        try:
            recommended_books,poster_url = self.recommend_book(selected_books)
            
            st.subheader(f"Recommended books similar to '{selected_books}':")
            
            # Display the selected book first
            st.markdown("---")
            st.subheader("Your selected book:")
            col0 = st.columns(1)
            with col0[0]:
                st.text(selected_books)
                book_pivot = pickle.load(open(self.recommendation_config.book_pivot_serialized_objects,'rb'))
                selected_book_id = np.where(book_pivot.index == selected_books)[0][0]
                selected_poster = self.fetch_poster([[selected_book_id]])[0]
                st.image(selected_poster, width=150)
            
            st.markdown("---")
            st.subheader("You might also like:")
            
            # Display recommendations in a responsive grid
            cols = st.columns(5)
            for i in range(1, 6):
                with cols[i-1]:
                    st.text(recommended_books[i])
                    st.image(poster_url[i], use_column_width=True)
                    
        except Exception as e:
            st.error(f"Error showing recommendations: {str(e)}")
            raise AppException(e, sys) from e

def load_image_from_url(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        st.warning(f"Could not load image from URL: {url}")
        return None

if __name__ == "__main__":
    # Set page config
    st.set_page_config(
        page_title="Book Recommender System",
        page_icon="📚",
        layout="wide"
    )
    
    # Load images from GitHub URLs
    author_image_url = "https://github.com/Rishikesh1411/Book-Recommender-System/blob/main/pic/rishikesh1.jpg?raw=true"
    org_image_url = "https://github.com/Rishikesh1411/Book-Recommender-System/blob/main/pic/organisation.jpeg?raw=true"
    
    author_image = load_image_from_url(author_image_url)
    org_image = load_image_from_url(org_image_url)
    
    # Sidebar with author info
    with st.sidebar:
        if org_image:
            st.image(org_image, width=150, caption="IIT Patna")
        else:
            st.markdown("**Organization:** IIT Patna")
            
        st.markdown("## About")
        st.markdown("""
        **Book Recommender System**  
        A collaborative filtering based recommendation engine  
        """)
        st.markdown("---")
        if author_image:
            st.image(author_image, width=150, caption="Rishikesh Raj")
        else:
            st.markdown("**Author:** Rishikesh Raj")  
        st.markdown("---")
        st.markdown("### Instructions")
        st.markdown("""
        1. Select a book from the dropdown
        2. Click 'Show Recommendation'
        3. Discover similar books!
        """)
    
    # Main content
    st.title('📚 Book Recommender System')
    st.markdown("Discover your next favorite book based on collaborative filtering!")
    
    obj = Recommendation()

    # Training section (optional - can be removed if not needed)
    st.markdown("---")
    st.subheader("System Training")
    st.warning("Note: Training requires internet connection to download data")
    if st.button('🚀 Train Recommender System'):
        obj.train_engine()
    
    # Recommendation section
    st.markdown("---")
    st.subheader("Get Recommendations")
    
    book_names = pickle.load(open(os.path.join('templates','book_names.pkl'),'rb'))
    selected_books = st.selectbox(
        "Type or select a book from the dropdown",
        book_names,
        index=0,
        help="Select a book to get recommendations"
    )
    
    if st.button('🔍 Show Recommendation', type="primary"):
        with st.spinner('Finding similar books...'):
            obj.recommendations_engine(selected_books)
