"""Tests for exceptions module."""

import pytest

from nocodb_simple_client.exceptions import NocoDBException, RecordNotFoundException


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_nocodb_exception_creation(self):
        """Test NocoDBException creation and attributes."""
        error = "TEST_ERROR"
        message = "This is a test error"

        exception = NocoDBException(error, message)

        assert exception.error == error
        assert exception.message == message
        assert str(exception) == f"{error}: {message}"

    def test_nocodb_exception_inheritance(self):
        """Test that NocoDBException inherits from Exception."""
        exception = NocoDBException("ERROR", "message")

        assert isinstance(exception, Exception)
        assert isinstance(exception, NocoDBException)

    def test_record_not_found_exception(self):
        """Test RecordNotFoundException creation and inheritance."""
        message = "Record with ID 123 not found"
        record_id = "123"

        exception = RecordNotFoundException(message, record_id)

        assert exception.error == "RECORD_NOT_FOUND"
        assert exception.message == message
        assert exception.record_id == record_id
        assert str(exception) == f"RECORD_NOT_FOUND: {message} (HTTP 404)"

        # Test inheritance
        assert isinstance(exception, NocoDBException)
        assert isinstance(exception, RecordNotFoundException)
        assert isinstance(exception, Exception)

    def test_exception_str_representation(self):
        """Test string representation of exceptions."""
        nocodb_exc = NocoDBException("VALIDATION_ERROR", "Invalid field value")
        record_exc = RecordNotFoundException("Record does not exist")

        assert str(nocodb_exc) == "VALIDATION_ERROR: Invalid field value"
        assert str(record_exc) == "RECORD_NOT_FOUND: Record does not exist (HTTP 404)"

    def test_exception_message_attribute(self):
        """Test that exception message is available as both message and args."""
        message = "This is the error message"
        exception = NocoDBException("ERROR", message)

        # Should be available as .message attribute
        assert exception.message == message

        # Should also be available in args (inherited from Exception)
        assert str(exception) == f"ERROR: {message}"

    def test_exception_with_empty_strings(self):
        """Test exceptions with empty or None values."""
        exception1 = NocoDBException("", "message")
        exception2 = NocoDBException("ERROR", "")

        assert exception1.error == ""
        assert exception1.message == "message"
        assert str(exception1) == ": message"

        assert exception2.error == "ERROR"
        assert exception2.message == ""
        assert str(exception2) == "ERROR: "

    def test_exception_raising_and_catching(self):
        """Test raising and catching the custom exceptions."""
        # Test raising and catching NocoDBException
        with pytest.raises(NocoDBException) as exc_info:
            raise NocoDBException("API_ERROR", "Something went wrong")

        assert exc_info.value.error == "API_ERROR"
        assert exc_info.value.message == "Something went wrong"

        # Test raising and catching RecordNotFoundException
        with pytest.raises(RecordNotFoundException) as exc_info:
            raise RecordNotFoundException("Record not found")

        assert exc_info.value.error == "RECORD_NOT_FOUND"
        assert exc_info.value.message == "Record not found"

    def test_catching_as_base_exception(self):
        """Test catching RecordNotFoundException as NocoDBException."""
        try:
            raise RecordNotFoundException("Not found")
        except NocoDBException as e:
            # Should be caught as base exception
            assert e.error == "RECORD_NOT_FOUND"
            assert e.message == "Not found"
            assert isinstance(e, RecordNotFoundException)

    def test_exception_in_exception_hierarchy(self):
        """Test the complete exception hierarchy."""
        record_exc = RecordNotFoundException("Not found")

        # Test with isinstance
        assert isinstance(record_exc, Exception)
        assert isinstance(record_exc, NocoDBException)
        assert isinstance(record_exc, RecordNotFoundException)

        # Test exception handling hierarchy
        caught_as_exception = False
        caught_as_nocodb = False
        caught_as_record_not_found = False

        try:
            raise record_exc
        except RecordNotFoundException:
            caught_as_record_not_found = True
        except NocoDBException:
            caught_as_nocodb = True
        except Exception:
            caught_as_exception = True

        # Should be caught by the most specific exception first
        assert caught_as_record_not_found
        assert not caught_as_nocodb
        assert not caught_as_exception
