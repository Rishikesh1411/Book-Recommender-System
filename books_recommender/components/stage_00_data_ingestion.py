import os
import sys
import urllib.request
import urllib.error
import zipfile
from typing import Optional

from books_recommender.logger.log import logger
from books_recommender.exception.exception_handler import AppException
from books_recommender.config.configuration import AppConfiguration


class DataIngestion:
    """Handles data downloading and extraction from remote sources."""
    
    def __init__(self, app_config: AppConfiguration = AppConfiguration()):
        """
        Initialize DataIngestion with configuration.
        
        Args:
            app_config: Application configuration object
        """
        try:
            logger.info(f"{'='*20} Data Ingestion log started {'='*20}")
            self.data_ingestion_config = app_config.get_data_ingestion_config()
        except Exception as e:
            logger.error("Failed to initialize DataIngestion")
            raise AppException(e, sys) from e

    def download_data(self) -> str:
        """
        Download data from configured URL.
        
        Returns:
            str: Path to downloaded zip file
            
        Raises:
            AppException: If download fails
        """
        try:
            dataset_url = self.data_ingestion_config.dataset_download_url
            zip_download_dir = self.data_ingestion_config.raw_data_dir
            
            os.makedirs(zip_download_dir, exist_ok=True)
            file_name = os.path.basename(dataset_url)
            zip_file_path = os.path.join(zip_download_dir, file_name)
            
            logger.info(f"Downloading data from {dataset_url} to {zip_file_path}")
            
            # Download with timeout
            urllib.request.urlretrieve(
                dataset_url,
                zip_file_path,
                reporthook=self._download_progress_hook
            )
            
            logger.info("Download completed successfully")
            return zip_file_path
            
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            raise AppException(e, sys) from e

    def _download_progress_hook(self, count: int, block_size: int, total_size: int) -> None:
        """Display download progress."""
        percent = min(int(count * block_size * 100 / total_size), 100)
        if percent % 10 == 0:  # Log every 10%
            logger.info(f"Download progress: {percent}%")

    def extract_zip_file(self, zip_file_path: str) -> None:
        """
        Extract downloaded zip file.
        
        Args:
            zip_file_path: Path to zip file
            
        Raises:
            AppException: If extraction fails
        """
        try:
            ingested_dir = self.data_ingestion_config.ingested_dir
            os.makedirs(ingested_dir, exist_ok=True)
            
            logger.info(f"Extracting {zip_file_path} to {ingested_dir}")
            
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(ingested_dir)
                
            logger.info("Extraction completed successfully")
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise AppException(e, sys) from e

    def initiate_data_ingestion(self) -> None:
        """Orchestrate the complete data ingestion process."""
        try:
            zip_file_path = self.download_data()
            self.extract_zip_file(zip_file_path)
            logger.info(f"{'='*20} Data Ingestion completed {'='*20}\n")
        except Exception as e:
            logger.error("Data ingestion process failed")
            raise AppException(e, sys) from e