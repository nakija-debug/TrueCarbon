"""Earth Engine singleton manager with thread-safe lazy initialization."""

import json
import logging
import threading
import time
from typing import Optional

import ee

from app.core.config import settings
from app.services.exceptions import (
    EarthEngineError,
    EarthEngineQuotaError,
    EarthEngineAuthError,
)

logger = logging.getLogger(__name__)


class EarthEngineManager:
    """
    Thread-safe singleton manager for Google Earth Engine initialization.

    Implements lazy initialization to prevent repeated API calls and ensure
    the event loop is not blocked. Includes exponential backoff retry logic
    for handling quota errors.
    """

    _instance: Optional["EarthEngineManager"] = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls) -> "EarthEngineManager":
        """Implement singleton pattern with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "EarthEngineManager":
        """Get or create singleton instance."""
        return cls()

    def initialize(self) -> None:
        """
        Perform lazy initialization of Earth Engine with error handling.

        Checks if EE is already initialized. If not, attempts authentication
        using service account credentials or default credentials. Implements
        exponential backoff for transient failures.

        Raises:
            EarthEngineAuthError: If authentication fails after retries
            EarthEngineQuotaError: If quota error is persistent
        """
        if self._initialized:
            logger.debug("Earth Engine already initialized")
            return

        with self._lock:
            # Double-check pattern
            if self._initialized:
                return

            self._perform_initialization()
            self._initialized = True

    def _perform_initialization(self) -> None:
        """Perform actual EE initialization with retry logic."""
        max_retries = settings.GEE_MAX_RETRIES
        retry_delay = settings.GEE_RETRY_DELAY

        for attempt in range(max_retries):
            try:
                # Check if already initialized
                if self._is_ee_initialized():
                    logger.info("Earth Engine is already initialized")
                    return

                # Try service account authentication first
                if settings.GEE_SERVICE_ACCOUNT:
                    self._initialize_with_service_account()
                else:
                    self._initialize_with_default_auth()

                logger.info(
                    f"Successfully initialized Earth Engine with project: {settings.GEE_PROJECT}"
                )
                return

            except ee.EEException as e:
                error_msg = str(e).lower()

                # Check for quota error
                if "quota" in error_msg or "limit" in error_msg or "rate" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(
                            f"GEE quota/rate limit hit. Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"GEE quota exceeded after {max_retries} retries")
                        raise EarthEngineQuotaError(
                            f"Google Earth Engine quota exceeded after {max_retries} retries"
                        ) from e

                # Other EE exceptions
                logger.error(f"Earth Engine initialization failed: {e}")
                raise EarthEngineAuthError(
                    f"Failed to initialize Earth Engine: {str(e)}"
                ) from e

            except Exception as e:
                logger.error(f"Unexpected error during EE initialization: {e}")
                raise EarthEngineError(f"Unexpected error: {str(e)}") from e

        raise EarthEngineAuthError("Failed to initialize Earth Engine after all retries")

    def _initialize_with_service_account(self) -> None:
        """Initialize using service account credentials."""
        try:
            service_account_info = json.loads(settings.GEE_SERVICE_ACCOUNT)
            credentials = ee.ServiceAccountCredentials(
                email=service_account_info.get("client_email"),
                key_data=settings.GEE_SERVICE_ACCOUNT,
            )
            ee.Initialize(credentials, project=settings.GEE_PROJECT)
            logger.info("Initialized Earth Engine with service account")
        except json.JSONDecodeError as e:
            raise EarthEngineAuthError(
                "Invalid JSON in GEE_SERVICE_ACCOUNT environment variable"
            ) from e

    def _initialize_with_default_auth(self) -> None:
        """Initialize using default authentication."""
        try:
            ee.Initialize(project=settings.GEE_PROJECT)
            logger.info("Initialized Earth Engine with default authentication")
        except ee.EEException:
            # Fallback to authenticate
            logger.info("Default auth failed, attempting ee.Authenticate()")
            ee.Authenticate()
            ee.Initialize(project=settings.GEE_PROJECT)
            logger.info("Initialized Earth Engine after authentication")

    @staticmethod
    def _is_ee_initialized() -> bool:
        """Check if Earth Engine is already initialized."""
        try:
            ee.Number(1).getInfo()
            return True
        except Exception:
            return False

    def is_initialized(self) -> bool:
        """Check if EE manager has been initialized."""
        return self._initialized
