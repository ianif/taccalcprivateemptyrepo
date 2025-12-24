"""
Unit tests for validation functions

This module contains unit tests for input validation functions used in the
Greek Tax Calculator. Tests cover data type validation, range checks, and
error handling.

To run only these tests:
    pytest tests/test_validators.py -v

To run with coverage:
    pytest tests/test_validators.py --cov=. --cov-report=term
"""

import pytest
from decimal import Decimal


# ============================================================================
# SMOKE TESTS - Basic validation functionality
# ============================================================================

@pytest.mark.unit
class TestValidatorsSmokeTests:
    """Smoke tests to verify basic validation functionality."""
    
    def test_decimal_conversion_from_float(self):
        """Verify that floats can be converted to Decimal."""
        value = 10000.50
        result = Decimal(str(value))
        assert isinstance(result, Decimal)
        assert result == Decimal('10000.50')
    
    def test_decimal_conversion_from_int(self):
        """Verify that integers can be converted to Decimal."""
        value = 10000
        result = Decimal(str(value))
        assert isinstance(result, Decimal)
        assert result == Decimal('10000.00')
    
    def test_decimal_conversion_from_string(self):
        """Verify that strings can be converted to Decimal."""
        value = "15000.75"
        result = Decimal(value)
        assert isinstance(result, Decimal)
        assert result == Decimal('15000.75')
    
    def test_negative_value_handling(self):
        """Verify that negative values can be represented as Decimal."""
        value = -5000
        result = Decimal(str(value))
        assert isinstance(result, Decimal)
        assert result == Decimal('-5000.00')
    
    def test_zero_value_handling(self):
        """Verify that zero is properly handled as Decimal."""
        value = 0
        result = Decimal(str(value))
        assert isinstance(result, Decimal)
        assert result == Decimal('0.00')
    
    def test_very_large_number_handling(self):
        """Verify that large numbers can be represented as Decimal."""
        value = 1000000
        result = Decimal(str(value))
        assert isinstance(result, Decimal)
        assert result == Decimal('1000000.00')
    
    def test_precision_maintenance(self):
        """Verify that Decimal maintains precision for financial calculations."""
        # This is a known floating-point precision issue
        float_result = 0.1 + 0.2
        decimal_result = Decimal('0.1') + Decimal('0.2')
        
        # Float will have precision issues
        assert float_result != 0.3
        
        # Decimal maintains precision
        assert decimal_result == Decimal('0.3')


# ============================================================================
# VALIDATION FUNCTION TESTS
# ============================================================================

from main import (
    validate_positive_number,
    validate_non_negative_number,
    validate_expenses_against_income,
    validate_realistic_amount,
    format_currency,
    save_results_to_file,
    MAX_ANNUAL_INCOME
)


@pytest.mark.unit
class TestValidatePositiveNumber:
    """Unit tests for validate_positive_number() function."""
    
    @pytest.mark.parametrize("value_str,expected", [
        ("100", 100.0),
        ("1000.50", 1000.50),
        ("0.01", 0.01),
        ("999999", 999999.0),
        ("  500  ", 500.0),  # Test whitespace stripping
    ])
    def test_valid_positive_numbers(self, value_str, expected):
        """Test that valid positive numbers are accepted and returned as floats."""
        result = validate_positive_number(value_str, "Test Field")
        assert result == expected
        assert isinstance(result, float)
    
    def test_reject_zero(self):
        """Test that zero is rejected with appropriate error message."""
        with pytest.raises(ValueError) as exc_info:
            validate_positive_number("0", "Test Field")
        assert "must be greater than zero" in str(exc_info.value)
        assert "you entered 0" in str(exc_info.value)
    
    @pytest.mark.parametrize("value_str", ["-100", "-0.01", "-999999"])
    def test_reject_negatives(self, value_str):
        """Test that negative numbers are rejected with appropriate error message."""
        with pytest.raises(ValueError) as exc_info:
            validate_positive_number(value_str, "Test Field")
        assert "cannot be negative" in str(exc_info.value)
        assert "you entered" in str(exc_info.value)
    
    @pytest.mark.parametrize("value_str", [
        "abc",
        "12.34.56",
        "€100",
        "",
        "not_a_number",
        "12,345"  # Comma separator not valid for float()
    ])
    def test_reject_non_numeric(self, value_str):
        """Test that non-numeric strings are rejected with appropriate error message."""
        with pytest.raises(ValueError) as exc_info:
            validate_positive_number(value_str, "Test Field")
        assert "must be a valid number" in str(exc_info.value)
        assert value_str in str(exc_info.value)
    
    def test_very_large_number(self):
        """Test that very large numbers are accepted (within float range)."""
        result = validate_positive_number("999999999999", "Test Field")
        assert result == 999999999999.0
    
    def test_field_name_in_error_message(self):
        """Test that the field name appears in error messages."""
        with pytest.raises(ValueError) as exc_info:
            validate_positive_number("0", "Income Amount")
        assert "Income Amount" in str(exc_info.value)


@pytest.mark.unit
class TestValidateNonNegativeNumber:
    """Unit tests for validate_non_negative_number() function."""
    
    @pytest.mark.parametrize("value_str,expected", [
        ("0", 0.0),  # Zero should be accepted
        ("100", 100.0),
        ("1000.50", 1000.50),
        ("0.01", 0.01),
        ("  250  ", 250.0),  # Test whitespace stripping
    ])
    def test_accept_zero_and_positives(self, value_str, expected):
        """Test that zero and positive numbers are accepted."""
        result = validate_non_negative_number(value_str, "Test Field")
        assert result == expected
        assert isinstance(result, float)
    
    @pytest.mark.parametrize("value_str", ["-100", "-0.01", "-999999"])
    def test_reject_negatives(self, value_str):
        """Test that negative numbers are rejected with appropriate error message."""
        with pytest.raises(ValueError) as exc_info:
            validate_non_negative_number(value_str, "Test Field")
        assert "cannot be negative" in str(exc_info.value)
        assert "you entered" in str(exc_info.value)
    
    @pytest.mark.parametrize("value_str", [
        "abc",
        "12.34.56",
        "€100",
        "",
        "not_a_number"
    ])
    def test_reject_non_numeric(self, value_str):
        """Test that non-numeric strings are rejected with appropriate error message."""
        with pytest.raises(ValueError) as exc_info:
            validate_non_negative_number(value_str, "Test Field")
        assert "must be a valid number" in str(exc_info.value)
        assert value_str in str(exc_info.value)


@pytest.mark.unit
class TestValidateExpensesAgainstIncome:
    """Unit tests for validate_expenses_against_income() function."""
    
    def test_valid_expenses_less_than_income(self):
        """Test that expenses less than income are accepted."""
        # Should not raise any exception
        validate_expenses_against_income(5000, 10000)
        validate_expenses_against_income(1, 100)
        validate_expenses_against_income(0, 1000)
    
    def test_valid_expenses_equal_to_income(self):
        """Test that expenses equal to income are accepted (edge case)."""
        # Should not raise any exception
        validate_expenses_against_income(10000, 10000)
        validate_expenses_against_income(0, 0)
    
    def test_invalid_expenses_exceed_income(self):
        """Test that expenses exceeding income are rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_expenses_against_income(15000, 10000)
        assert "cannot exceed" in str(exc_info.value)
        assert "€15,000.00" in str(exc_info.value)
        assert "€10,000.00" in str(exc_info.value)
    
    def test_error_message_formatting(self):
        """Test that error message includes properly formatted amounts."""
        with pytest.raises(ValueError) as exc_info:
            validate_expenses_against_income(6000, 5000)
        error_msg = str(exc_info.value)
        assert "Deductible expenses" in error_msg
        assert "gross income" in error_msg
        # Verify comma formatting in error message
        assert "€6,000.00" in error_msg
        assert "€5,000.00" in error_msg


@pytest.mark.unit
class TestValidateRealisticAmount:
    """Unit tests for validate_realistic_amount() function."""
    
    def test_valid_amounts_within_default_limit(self):
        """Test that amounts within MAX_ANNUAL_INCOME are accepted."""
        # Should not raise any exception
        validate_realistic_amount(100, "Test Field")
        validate_realistic_amount(50000, "Test Field")
        validate_realistic_amount(1000000, "Test Field")
        validate_realistic_amount(MAX_ANNUAL_INCOME, "Test Field")  # Exactly at limit
    
    def test_reject_amounts_exceeding_default_limit(self):
        """Test that amounts exceeding MAX_ANNUAL_INCOME are rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_realistic_amount(MAX_ANNUAL_INCOME + 1, "Test Field")
        assert "seems unrealistic" in str(exc_info.value)
    
    def test_custom_max_amount(self):
        """Test that custom max_amount parameter works correctly."""
        # Should accept values under custom limit
        validate_realistic_amount(5000, "Test Field", max_amount=10000)
        
        # Should reject values over custom limit
        with pytest.raises(ValueError) as exc_info:
            validate_realistic_amount(15000, "Test Field", max_amount=10000)
        assert "seems unrealistic" in str(exc_info.value)
        assert "€10,000" in str(exc_info.value)
    
    def test_verify_constant_is_used(self):
        """Test that MAX_ANNUAL_INCOME constant is properly used."""
        # Verify the constant value is what we expect
        assert MAX_ANNUAL_INCOME == 10000000
        
        # Test that amounts just over the limit are rejected
        with pytest.raises(ValueError) as exc_info:
            validate_realistic_amount(20000000, "Test Field")
        assert "€10,000,000" in str(exc_info.value)
    
    def test_error_message_includes_field_name(self):
        """Test that field name appears in error message."""
        with pytest.raises(ValueError) as exc_info:
            validate_realistic_amount(99999999999, "Gross Income")
        assert "Gross Income" in str(exc_info.value)


@pytest.mark.unit
class TestFormatCurrency:
    """Unit tests for format_currency() function."""
    
    @pytest.mark.parametrize("amount,expected", [
        (0, "€0.00"),
        (100, "€100.00"),
        (1000, "€1,000.00"),
        (1234.56, "€1,234.56"),
        (10000, "€10,000.00"),
        (999999.99, "€999,999.99"),
        (1000000, "€1,000,000.00"),
        (0.01, "€0.01"),
        (0.1, "€0.10"),
    ])
    def test_various_amounts(self, amount, expected):
        """Test formatting of various amounts."""
        result = format_currency(amount)
        assert result == expected
    
    def test_euro_symbol_present(self):
        """Test that € symbol is present in formatted output."""
        result = format_currency(100)
        assert result.startswith("€")
    
    def test_comma_thousand_separator(self):
        """Test that comma is used as thousand separator."""
        result = format_currency(1234567.89)
        assert result == "€1,234,567.89"
        assert "," in result
    
    def test_two_decimal_places(self):
        """Test that exactly two decimal places are shown."""
        result = format_currency(100)
        assert result == "€100.00"
        
        result = format_currency(100.5)
        assert result == "€100.50"
        
        result = format_currency(100.123)  # Should round
        assert ".12" in result or ".13" in result  # Allow for rounding
    
    def test_negative_amounts(self):
        """Test formatting of negative amounts (if applicable)."""
        result = format_currency(-100)
        assert "€-100.00" in result or "-€100.00" in result


@pytest.mark.unit  
class TestSaveResultsToFile:
    """Unit tests for save_results_to_file() function with mocked file operations."""
    
    def test_successful_save(self, mocker, sample_calculation_result):
        """Test successful file save returns filename."""
        # Mock the open function
        mock_open = mocker.patch('builtins.open', mocker.mock_open())
        
        # Mock datetime to get predictable filename
        mock_datetime = mocker.patch('main.datetime')
        mock_datetime.now.return_value.strftime.return_value = '2024-01-15_120000'
        
        result = save_results_to_file(sample_calculation_result, 'monthly')
        
        assert result == 'tax_calculation_2024-01-15_120000.txt'
        mock_open.assert_called_once()
    
    def test_ioerror_handling(self, mocker, sample_calculation_result, capsys):
        """Test that IOError is handled gracefully."""
        # Mock open to raise IOError
        mocker.patch('builtins.open', side_effect=IOError("Permission denied"))
        
        result = save_results_to_file(sample_calculation_result, 'monthly')
        
        assert result is None
        captured = capsys.readouterr()
        assert "Could not save results to file" in captured.out
    
    def test_permission_error_handling(self, mocker, sample_calculation_result, capsys):
        """Test that PermissionError is handled gracefully."""
        # Mock open to raise PermissionError
        mocker.patch('builtins.open', side_effect=PermissionError("Access denied"))
        
        result = save_results_to_file(sample_calculation_result, 'monthly')
        
        assert result is None
        captured = capsys.readouterr()
        assert "unexpected error occurred" in captured.out
    
    def test_generic_exception_handling(self, mocker, sample_calculation_result, capsys):
        """Test that unexpected exceptions are handled gracefully."""
        # Mock open to raise generic exception
        mocker.patch('builtins.open', side_effect=Exception("Unexpected error"))
        
        result = save_results_to_file(sample_calculation_result, 'monthly')
        
        assert result is None
        captured = capsys.readouterr()
        assert "unexpected error occurred" in captured.out


# ============================================================================
# PLACEHOLDER FOR ADDITIONAL VALIDATION TESTS
# ============================================================================

@pytest.mark.unit
class TestInputValidation:
    """Unit tests for input validation functions."""
    
    def test_placeholder(self):
        """Placeholder test - additional validation tests can be added here."""
        assert True


@pytest.mark.unit
class TestRangeValidation:
    """Unit tests for range validation functions."""
    
    def test_placeholder(self):
        """Placeholder test - additional range validation tests can be added here."""
        assert True


@pytest.mark.unit
class TestTypeValidation:
    """Unit tests for type validation functions."""
    
    def test_placeholder(self):
        """Placeholder test - additional type validation tests can be added here."""
        assert True


@pytest.mark.unit
class TestErrorHandling:
    """Unit tests for error handling in validation."""
    
    def test_placeholder(self):
        """Placeholder test - additional error handling tests can be added here."""
        assert True
