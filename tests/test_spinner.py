"""Tests for the spinner module."""

import unittest
import threading
import io
from unittest.mock import patch, MagicMock

from etracer.utils import Spinner, Colors

_THREAD_TIME_OUT = 0.5  # seconds for spinner thread to stop gracefully


class TestSpinner(unittest.TestCase):
    """Test the Spinner class."""

    def setUp(self):
        """Set up the test."""
        self._stop_event = threading.Event()
        self._output = io.StringIO()
        self._spinner = Spinner(self._stop_event, output=self._output, message="Testing")

    def tearDown(self):
        """Clean up after the test."""
        # Ensure spinner is stopped
        if not self._stop_event.is_set():
            self._stop_event.set()
            if (
                hasattr(self._spinner, "_spinner_thread")
                and self._spinner._spinner_thread
                and self._spinner._spinner_thread.is_alive()
            ):
                self._spinner._spinner_thread.join(_THREAD_TIME_OUT)

    def test_init(self):
        """Test the __init__ method."""
        # Test with explicit parameters
        spinner = Spinner(self._stop_event, output=self._output, message="Custom message")
        self.assertEqual(spinner._stop_event, self._stop_event)
        self.assertEqual(spinner._output, self._output)
        self.assertEqual(spinner._message, "Custom message")
        self.assertEqual(spinner._sleep, 0.1)
        self.assertIsNone(spinner._spinner_thread)

        # Test with default stop_event
        spinner = Spinner(None, output=self._output)
        self.assertIsNotNone(spinner._stop_event)
        self.assertIsInstance(spinner._stop_event, threading.Event)
        self.assertFalse(spinner._stop_event.is_set())
        self.assertEqual(spinner._message, "Processing")  # Default message

    @patch("time.sleep")  # Mock sleep to avoid waiting in tests
    def test_spin_worker(self, mock_sleep):
        """Test the _spin_worker method."""
        # We'll manually call _spin_worker for a short time
        mock_stop_event = MagicMock()

        # Configure the mock to return False first time, then True (to stop after one iteration)
        mock_stop_event.is_set.side_effect = [False, True]

        self._spinner._stop_event = mock_stop_event
        self._spinner._spin_worker()

        # Verify output was written and flushed
        output_content = self._output.getvalue()
        self.assertIn(f"{Colors.CYAN}Testing", output_content)
        self.assertIn(f"{Colors.ENDC}", output_content)  # Check that color is reset

        # Verify sleep was called with correct time
        mock_sleep.assert_called_once_with(0.1)

    def test_clear_line(self):
        """Test the _clear_line method."""
        self._spinner._clear_line()

        # Verify output contains the clear sequence and was flushed
        output_content = self._output.getvalue()
        self.assertIn("\r" + " " * 80 + "\r", output_content)

    @patch("threading.Thread")
    def test_start(self, mock_thread):
        """Test the start method."""
        # Create a mock thread
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Call start
        self._spinner.start()

        # Verify thread was created with correct parameters
        mock_thread.assert_called_once_with(target=self._spinner._spin_worker)

        # Verify thread was started and set to daemon
        mock_thread_instance.daemon = True
        mock_thread_instance.start.assert_called_once()

        # Verify thread was stored
        self.assertEqual(self._spinner._spinner_thread, mock_thread_instance)

    @patch("threading.Thread")
    def test_stop(self, mock_thread):
        """Test the stop method."""
        # Create a mock thread that reports as alive
        mock_thread_instance = MagicMock()
        mock_thread_instance.is_alive.return_value = True
        mock_thread.return_value = mock_thread_instance

        # Start the spinner (which creates the thread)
        self._spinner.start()

        # Call stop
        with patch.object(self._spinner, "_clear_line") as mock_clear_line:
            self._spinner.stop()

            # Verify stop event was set
            self.assertTrue(self._stop_event.is_set())

            # Verify thread was joined with timeout
            mock_thread_instance.join.assert_called_once_with(_THREAD_TIME_OUT)

            # Verify line was cleared
            mock_clear_line.assert_called_once()

    def test_stop_no_thread(self):
        """Test the stop method when no thread is running."""
        # Don't start the spinner, so _spinner_thread is None
        self.assertIsNone(self._spinner._spinner_thread)

        # Call stop
        with patch.object(self._spinner, "_clear_line") as mock_clear_line:
            self._spinner.stop()

            # Verify line was still cleared
            mock_clear_line.assert_called_once()

    def test_stop_thread_not_alive(self):
        """Test the stop method when thread is not alive."""
        # Create a mock thread that reports as not alive
        mock_thread = MagicMock()
        mock_thread.is_alive.return_value = False
        self._spinner._spinner_thread = mock_thread

        # Call stop
        with patch.object(self._spinner, "_clear_line") as mock_clear_line:
            self._spinner.stop()

            # Verify thread was not joined
            mock_thread.join.assert_not_called()

            # Verify line was still cleared
            mock_clear_line.assert_called_once()


if __name__ == "__main__":
    unittest.main()
