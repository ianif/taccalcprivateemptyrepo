#!/usr/bin/env python3
"""
Greek Freelancer Tax Calculator - Command Line Interface

CLI application for calculating taxes for Greek freelancers with support for
interactive, non-interactive, and hybrid modes. Provides robust input validation
and comprehensive tax calculations including income tax, VAT, and social security.

USAGE MODES:

1. INTERACTIVE MODE (default):
    python main.py
    
    Follow the interactive prompts to:
    1. Enter gross annual income (e.g., 35000 for €35,000)
    2. Enter deductible business expenses (e.g., 5000 for €5,000)
    3. Choose payment frequency (monthly, quarterly, or annual)
    4. Review and confirm inputs
    5. View comprehensive tax breakdown and payment schedule
    6. Results are automatically saved to a timestamped file

2. NON-INTERACTIVE MODE (via command-line arguments):
    python main.py --income 35000 --expenses 5000 --frequency quarterly
    
    All parameters provided via CLI, no prompts. Perfect for automation.

3. HYBRID MODE (partial CLI arguments):
    python main.py --income 35000
    
    Provided arguments are used, prompts shown for missing values.

EXAMPLE SESSION (Interactive):
    Gross annual income (€): 35000
    Deductible expenses (€): 5000
    Payment frequency: 2 (Quarterly)
    
    → Calculates: 
      - Taxable income: €30,000
      - Income tax: €5,900
      - EFKA: €7,000
      - Total taxes: €12,900
      - Net income: €22,100
      - Quarterly payment: €3,225

EXAMPLE COMMAND (Non-Interactive):
    python main.py --income 35000 --expenses 5000 --frequency quarterly --quiet
    
    Same calculation as above, minimal output, perfect for scripts.

For full CLI documentation, run: python main.py --help
"""

import sys
import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Union, List
from decimal import Decimal
import argparse
from tax_calculator import (
    calculate_all_taxes,
    calculate_payment_schedule
)
from config import (
    VALID_FREQUENCIES,
    MAX_ANNUAL_INCOME
)
from models import TaxCalculationResult, PaymentSchedule
from formatters import (
    format_currency,
    format_input_parameters,
    format_income_breakdown,
    format_income_tax_breakdown,
    format_vat_and_social_security,
    format_payment_schedule,
    format_summary,
    ConsoleWriter,
    FileWriter
)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging(verbose: bool = False, quiet: bool = False, 
                 log_file: Optional[str] = None, no_log_file: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        verbose: Enable DEBUG level logging to console
        quiet: Show only WARNING and above to console
        log_file: Custom log file path (default: tax_calculator_debug.log)
        no_log_file: Disable file logging entirely
    """
    # Determine console log level
    if verbose:
        console_level = logging.DEBUG
    elif quiet:
        console_level = logging.WARNING
    else:
        console_level = logging.INFO
    
    # Set up handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler (unless disabled)
    if not no_log_file:
        log_file_path = log_file if log_file else 'tax_calculator_debug.log'
        try:
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)
        except (PermissionError, OSError) as e:
            # If we can't create log file, continue without it
            print(f"⚠️  Warning: Could not create log file '{log_file_path}': {e}")
            print("   Continuing without file logging.")
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Override any existing configuration
    )

# Create logger for this module (will be configured by setup_logging)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Note: Tax-related constants (MAX_ANNUAL_INCOME, VAT_RATE, EFKA rates, etc.)
# are imported from config.py for centralized configuration management.

# Output directory for saved tax calculation files
# All calculation results will be saved to this directory to prevent
# path traversal attacks and maintain organized file storage
OUTPUT_DIR = 'output'

# Maximum file size for output files (10 MB)
# Prevents potential disk space exhaustion attacks or accidental creation
# of extremely large files due to calculation errors
MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================================
# INPUT VALIDATION FUNCTIONS
# ============================================================================

def validate_positive_number(value_str: str, field_name: str) -> Decimal:
    """
    Validate that input is a positive number (> 0).
    
    Args:
        value_str: String input from user
        field_name: Name of field for error messages
    
    Returns:
        Decimal: Validated positive number
    
    Raises:
        ValueError: If input is not a valid positive number
    """
    logger.debug(f"Validating positive number for {field_name}: '{value_str}'")
    try:
        value = Decimal(value_str.strip())
        if value == 0:
            logger.warning(f"Validation failed: {field_name} is zero")
            raise ValueError(f"{field_name} must be greater than zero (you entered 0).")
        elif value < 0:
            logger.warning(f"Validation failed: {field_name} is negative")
            raise ValueError(f"{field_name} cannot be negative (you entered {value:,.2f}).")
        logger.debug(f"Validation successful: {field_name} is valid positive number")
        return value
    except ValueError as e:
        if "could not convert" in str(e):
            logger.warning(f"Validation failed: {field_name} is not a valid number: '{value_str}'")
            raise ValueError(f"{field_name} must be a valid number (not '{value_str}').")
        raise


def validate_non_negative_number(value_str: str, field_name: str) -> Decimal:
    """
    Validate that input is a non-negative number (>= 0).
    
    Args:
        value_str: String input from user
        field_name: Name of field for error messages
    
    Returns:
        Decimal: Validated non-negative number
    
    Raises:
        ValueError: If input is not a valid non-negative number
    """
    logger.debug(f"Validating non-negative number for {field_name}: '{value_str}'")
    try:
        value = Decimal(value_str.strip())
        if value < 0:
            logger.warning(f"Validation failed: {field_name} is negative")
            raise ValueError(f"{field_name} cannot be negative (you entered {value:,.2f}).")
        logger.debug(f"Validation successful: {field_name} is valid non-negative number")
        return value
    except ValueError as e:
        if "could not convert" in str(e) or "Invalid literal" in str(e):
            logger.warning(f"Validation failed: {field_name} is not a valid number: '{value_str}'")
            raise ValueError(f"{field_name} must be a valid number (not '{value_str}').")
        raise


def validate_expenses_against_income(expenses: Decimal, gross_income: Decimal) -> None:
    """
    Validate that expenses do not exceed gross income.
    
    Args:
        expenses (float): Deductible expenses amount
        gross_income (float): Gross income amount
    
    Raises:
        ValueError: If expenses exceed gross income
    """
    logger.debug("Validating expenses against gross income")
    if expenses > gross_income:
        logger.warning("Validation failed: Expenses exceed gross income")
        raise ValueError(
            f"Deductible expenses (€{expenses:,.2f}) cannot exceed "
            f"gross income (€{gross_income:,.2f})."
        )
    logger.debug("Validation successful: Expenses do not exceed gross income")


def validate_realistic_amount(value: Decimal, field_name: str, max_amount: Optional[float] = None) -> None:
    """
    Validate that amount is realistic (not absurdly high).
    
    Args:
        value: Amount to validate
        field_name: Name of field for error messages
        max_amount: Maximum realistic amount (default: uses MAX_ANNUAL_INCOME constant)
    
    Raises:
        ValueError: If amount exceeds realistic maximum
    """
    if max_amount is None:
        max_amount = MAX_ANNUAL_INCOME
    
    logger.debug(f"Validating realistic amount for {field_name} (max: €{max_amount:,.0f})")
    if value > max_amount:
        logger.warning(f"Validation failed: {field_name} exceeds realistic maximum")
        raise ValueError(
            f"{field_name} of €{value:,.2f} seems unrealistic. "
            f"Please enter a value less than €{max_amount:,.0f}."
        )
    logger.debug(f"Validation successful: {field_name} is within realistic range")


# ============================================================================
# FILE SECURITY FUNCTIONS
# ============================================================================

def sanitize_filename(filename: str) -> str:
    """
    Sanitize and validate filename to prevent path traversal attacks.
    
    Args:
        filename: Proposed filename to sanitize
    
    Returns:
        str: Sanitized filename safe for use
    
    Raises:
        ValueError: If filename contains unsafe characters or patterns
    """
    logger.debug(f"Sanitizing filename: '{filename}'")
    
    # Check for empty filename
    if not filename or not filename.strip():
        logger.warning("Filename sanitization failed: empty filename")
        raise ValueError("Filename cannot be empty")
    
    filename = filename.strip()
    
    # Check for absolute paths (Unix-style)
    if filename.startswith('/'):
        logger.warning(f"Filename sanitization failed: absolute Unix path detected")
        raise ValueError(f"Absolute paths are not allowed: {filename}")
    
    # Check for absolute paths (Windows-style)
    if len(filename) > 1 and filename[1] == ':':
        logger.warning(f"Filename sanitization failed: absolute Windows path detected")
        raise ValueError(f"Absolute paths are not allowed: {filename}")
    
    # Check for path traversal patterns
    if '..' in filename:
        logger.warning(f"Filename sanitization failed: path traversal pattern detected")
        raise ValueError(f"Path traversal patterns (..) are not allowed: {filename}")
    
    # Check for directory separators
    if '/' in filename or '\\' in filename:
        logger.warning(f"Filename sanitization failed: directory separator detected")
        raise ValueError(f"Directory separators are not allowed in filename: {filename}")
    
    # Validate characters: allow alphanumeric, underscore, hyphen, dot
    # Pattern: only letters, digits, underscore, hyphen, and dot
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
        logger.warning(f"Filename sanitization failed: invalid characters detected")
        raise ValueError(
            f"Filename contains invalid characters. "
            f"Only alphanumeric, underscore, hyphen, and dot are allowed: {filename}"
        )
    
    logger.debug(f"Filename sanitization successful: '{filename}'")
    return filename


def ensure_output_directory() -> None:
    """
    Ensure output directory exists and is writable.
    
    Raises:
        PermissionError: If directory cannot be created or is not writable
        OSError: If directory creation fails for system-level reasons
    """
    logger.debug(f"Ensuring output directory exists: '{OUTPUT_DIR}'")
    try:
        # Create directory if it doesn't exist (parents=True for nested paths)
        Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory verified: '{OUTPUT_DIR}'")
        
        # Verify the directory is writable by checking permissions
        if not os.access(OUTPUT_DIR, os.W_OK):
            logger.error(f"Output directory '{OUTPUT_DIR}' is not writable")
            raise PermissionError(
                f"Output directory '{OUTPUT_DIR}' exists but is not writable. "
                f"Please check directory permissions."
            )
            
    except PermissionError:
        # Re-raise permission errors with context
        raise
    except OSError as e:
        # Handle other OS-level errors (disk full, etc.)
        logger.error(f"Failed to create output directory: {str(e)}")
        raise OSError(
            f"Failed to create or access output directory '{OUTPUT_DIR}': {str(e)}"
        )


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_header() -> None:
    """Display application header."""
    print("\n" + "=" * 70)
    print("  GREEK FREELANCER TAX CALCULATOR")
    print("=" * 70)


def display_main_menu() -> None:
    """Display main menu options."""
    print("\n" + "-" * 70)
    print("MAIN MENU")
    print("-" * 70)
    print("1. New Calculation")
    print("2. Exit")
    print("-" * 70)


def display_frequency_menu() -> str:
    """
    Display payment frequency menu and get user selection.
    
    Returns:
        str: Selected frequency ('monthly', 'quarterly', or 'annual')
    """
    logger.debug("Displaying payment frequency menu")
    print("\n" + "-" * 70)
    print("SELECT PAYMENT FREQUENCY")
    print("-" * 70)
    print("1. Monthly (12 payments per year)")
    print("2. Quarterly (4 payments per year)")
    print("3. Annual (1 payment per year)")
    print("-" * 70)
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                logger.info("User selected monthly payment frequency")
                return 'monthly'
            elif choice == '2':
                logger.info("User selected quarterly payment frequency")
                return 'quarterly'
            elif choice == '3':
                logger.info("User selected annual payment frequency")
                return 'annual'
            else:
                logger.debug(f"Invalid frequency choice entered: '{choice}'")
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except (EOFError, KeyboardInterrupt):
            logger.info("User cancelled frequency selection")
            print("\n\n❌ Input cancelled.")
            sys.exit(0)


def display_results(tax_result: 'TaxCalculationResult', payment_frequency: str) -> None:
    """
    Display comprehensive tax calculation results in terminal.
    
    Args:
        tax_result: Results from calculate_all_taxes()
        payment_frequency: Payment frequency ('monthly', 'quarterly', 'annual')
    """
    payment_schedule = calculate_payment_schedule(tax_result.total_taxes, payment_frequency)
    writer = ConsoleWriter()
    
    print("\n" + "=" * 70)
    print("TAX CALCULATION RESULTS")
    print("=" * 70)
    print(f"Calculation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    print()
    writer.write_lines(format_input_parameters(tax_result, payment_frequency))
    print()
    writer.write_lines(format_income_breakdown(tax_result))
    print()
    writer.write_lines(format_income_tax_breakdown(tax_result.income_tax))
    print()
    writer.write_lines(format_vat_and_social_security(tax_result.vat, tax_result.social_security))
    print()
    writer.write_lines(format_payment_schedule(payment_schedule, payment_frequency))
    print()
    writer.write_lines(format_summary(tax_result))


def _generate_output_filepath() -> str:
    """
    Generate unique, sanitized file path for output file.
    
    Handles timestamp generation, filename sanitization, and ensures uniqueness
    by appending a counter if file already exists.
    
    Returns:
        str: Full file path for output file
    """
    logger.debug("Generating output file path")
    ensure_output_directory()
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filename = sanitize_filename(f"tax_calculation_{timestamp}.txt")
    file_path = os.path.join(OUTPUT_DIR, filename)
    logger.debug(f"Generated file path: {os.path.basename(file_path)}")
    
    if os.path.exists(file_path):
        logger.warning(f"File already exists: {os.path.basename(file_path)} (unusual - rapid calculations?)")
        print(f"\n⚠️  Warning: File '{file_path}' already exists.")
        print(f"   This is unusual and may indicate rapid successive calculations.")
        counter = 1
        while os.path.exists(file_path):
            filename = sanitize_filename(f"tax_calculation_{timestamp}_{counter}.txt")
            file_path = os.path.join(OUTPUT_DIR, filename)
            counter += 1
        logger.info(f"Using alternative filename: {os.path.basename(file_path)}")
        print(f"   Saving to '{file_path}' instead.")
    
    return file_path


def _build_file_content_lines(tax_result: 'TaxCalculationResult', payment_frequency: str) -> List[str]:
    """
    Build content lines for tax calculation file.
    
    Args:
        tax_result: Tax calculation results
        payment_frequency: Payment frequency ('monthly', 'quarterly', 'annual')
    
    Returns:
        List[str]: Content lines for file
    """
    logger.debug("Building file content lines")
    payment_schedule = calculate_payment_schedule(tax_result.total_taxes, payment_frequency)
    
    content_lines = []
    content_lines.append("=" * 70)
    content_lines.append("GREEK FREELANCER TAX CALCULATION RESULTS")
    content_lines.append("=" * 70)
    content_lines.append(f"Calculation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content_lines.append("=" * 70)
    content_lines.append("")
    content_lines.extend(format_input_parameters(tax_result, payment_frequency))
    content_lines.append("")
    content_lines.extend(format_income_breakdown(tax_result))
    content_lines.append("")
    content_lines.extend(format_income_tax_breakdown(tax_result.income_tax))
    content_lines.append("")
    content_lines.extend(format_vat_and_social_security(tax_result.vat, tax_result.social_security))
    content_lines.append("")
    content_lines.extend(format_payment_schedule(payment_schedule, payment_frequency))
    content_lines.append("")
    content_lines.extend(format_summary(tax_result))
    
    logger.debug(f"Built {len(content_lines)} content lines")
    return content_lines


def save_results_to_file(tax_result: 'TaxCalculationResult', payment_frequency: str) -> Optional[str]:
    """
    Save tax calculation results to timestamped file.
    
    Args:
        tax_result: Results from calculate_all_taxes()
        payment_frequency: Payment frequency ('monthly', 'quarterly', 'annual')
    
    Returns:
        str: Full file path if successful, None if error occurred
    """
    logger.debug("Starting save_results_to_file")
    try:
        file_path = _generate_output_filepath()
        content_lines = _build_file_content_lines(tax_result, payment_frequency)
        file_content = FileWriter.lines_to_content(content_lines)
        
        content_size = len(file_content.encode('utf-8'))
        logger.debug(f"File content size: {content_size:,} bytes")
        
        if content_size > MAX_FILE_SIZE:
            logger.error(f"File size ({content_size:,} bytes) exceeds maximum ({MAX_FILE_SIZE:,} bytes)")
            print(f"\n⚠️  Warning: Cannot save results to file.")
            print(f"   Error: Generated file size ({content_size:,} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE:,} bytes).")
            print(f"   This may indicate a calculation error. Please contact support.")
            return None
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        logger.debug(f"File written successfully: {os.path.basename(file_path)}")
        return file_path
        
    except PermissionError as e:
        logger.error(f"Permission denied while saving file: {str(e)}", exc_info=True)
        print(f"\n⚠️  Warning: Permission denied when saving results to file.")
        print(f"   Error: {str(e)}")
        print(f"   Please check that you have write permissions for the '{OUTPUT_DIR}' directory.")
        return None
    except OSError as e:
        logger.error(f"OS error while saving file: {str(e)}", exc_info=True)
        print(f"\n⚠️  Warning: System error occurred while saving results to file.")
        print(f"   Error: {str(e)}")
        print(f"   This may be due to insufficient disk space or system restrictions.")
        return None
    except IOError as e:
        logger.error(f"I/O error while saving file: {str(e)}", exc_info=True)
        print(f"\n⚠️  Warning: Could not save results to file due to I/O error.")
        print(f"   Error: {str(e)}")
        print(f"   Please ensure the '{OUTPUT_DIR}' directory is accessible.")
        return None
    except ValueError as e:
        logger.error(f"Filename sanitization error: {str(e)}", exc_info=True)
        print(f"\n⚠️  Warning: Invalid filename detected.")
        print(f"   Error: {str(e)}")
        print(f"   This is an internal error. Please contact support.")
        return None
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        logger.error(f"Unicode encoding error while saving file: {str(e)}", exc_info=True)
        print(f"\n⚠️  Warning: Character encoding error while saving file.")
        print(f"   Error: {str(e)}")
        print(f"   Please ensure your calculation doesn't contain unsupported characters.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while saving file: {str(e)}", exc_info=True)
        print(f"\n⚠️  Warning: An unexpected error occurred while saving file.")
        print(f"   Error: {str(e)}")
        print(f"   Please try again or contact support if the problem persists.")
        return None


# ============================================================================
# USER INPUT COLLECTION FUNCTIONS
# ============================================================================

def get_gross_income() -> Decimal:
    """
    Prompt user for gross annual income with validation.
    
    Returns:
        Decimal: Validated gross annual income (>= 0)
    """
    logger.debug("Collecting gross income from user")
    print("\n" + "-" * 70)
    print("GROSS ANNUAL INCOME")
    print("-" * 70)
    print("Enter your total gross annual income (excluding VAT).")
    print("Example: 50000 for €50,000")
    print("Enter 0 if you have no income to calculate.")
    print("-" * 70)
    
    while True:
        try:
            value_str = input("Gross annual income (€): ").strip()
            
            if not value_str:
                logger.debug("User entered empty value for gross income")
                print("❌ Please enter a value.")
                continue
            
            gross_income = validate_non_negative_number(value_str, "Gross income")
            
            if gross_income > 0:
                validate_realistic_amount(gross_income, "Gross income")
            
            logger.info("Gross income collected successfully")
            logger.debug(f"Gross income value accepted: {gross_income}")
            return gross_income
            
        except ValueError as e:
            print(f"❌ {str(e)}")
        except (EOFError, KeyboardInterrupt):
            logger.info("User cancelled gross income input")
            print("\n\n❌ Input cancelled.")
            sys.exit(0)


def get_deductible_expenses(gross_income: Decimal) -> Decimal:
    """
    Prompt user for deductible business expenses with validation.
    
    Args:
        gross_income: Gross income for validation
    
    Returns:
        Decimal: Validated deductible expenses
    """
    logger.debug("Collecting deductible expenses from user")
    print("\n" + "-" * 70)
    print("DEDUCTIBLE BUSINESS EXPENSES")
    print("-" * 70)
    print("Enter your total deductible business expenses for the year.")
    print("This includes office rent, equipment, software, etc.")
    print(f"Maximum allowed: {format_currency(gross_income)}")
    print("Enter 0 if you have no deductible expenses.")
    print("-" * 70)
    
    while True:
        try:
            value_str = input("Deductible expenses (€): ").strip()
            
            if not value_str:
                logger.debug("User entered empty value for expenses")
                print("❌ Please enter a value (or 0 for no expenses).")
                continue
            
            expenses = validate_non_negative_number(value_str, "Expenses")
            validate_expenses_against_income(expenses, gross_income)
            validate_realistic_amount(expenses, "Expenses")
            
            logger.info("Deductible expenses collected successfully")
            logger.debug(f"Expenses value accepted: {expenses}")
            return expenses
            
        except ValueError as e:
            print(f"❌ {str(e)}")
        except (EOFError, KeyboardInterrupt):
            logger.info("User cancelled expenses input")
            print("\n\n❌ Input cancelled.")
            sys.exit(0)


def confirm_inputs(gross_income: Decimal, expenses: Decimal, frequency: str) -> bool:
    """
    Display input summary and ask for confirmation.
    
    Args:
        gross_income: Gross annual income
        expenses: Deductible expenses
        frequency: Payment frequency
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    logger.debug("Requesting user confirmation of inputs")
    print("\n" + "=" * 70)
    print("CONFIRM YOUR INPUTS")
    print("=" * 70)
    print(f"Gross Annual Income:       {format_currency(gross_income)}")
    print(f"Deductible Expenses:       {format_currency(expenses)}")
    print(f"Payment Frequency:         {frequency.capitalize()}")
    print("=" * 70)
    
    while True:
        try:
            response = input("\nProceed with calculation? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y']:
                logger.info("User confirmed inputs - proceeding with calculation")
                return True
            elif response in ['no', 'n']:
                logger.info("User declined to proceed with calculation")
                return False
            else:
                logger.debug(f"Invalid confirmation response: '{response}'")
                print("❌ Please enter 'yes' or 'no'.")
        except (EOFError, KeyboardInterrupt):
            logger.info("User cancelled input confirmation")
            print("\n\n❌ Input cancelled.")
            return False


# ============================================================================
# CALCULATION EXECUTION
# ============================================================================

def perform_calculation(gross_income: Decimal, expenses: Decimal, frequency: str) -> Optional[Dict[str, Union[Decimal, Dict]]]:
    """
    Execute tax calculation, display results, and save to file.
    
    Args:
        gross_income: Gross annual income
        expenses: Deductible expenses
        frequency: Payment frequency
    
    Returns:
        Optional[Dict]: Tax calculation results, or None if error occurred
    """
    try:
        logger.info("Starting tax calculation")
        logger.debug(f"Calculation parameters: frequency={frequency}")
        
        print("\n" + "=" * 70)
        print("CALCULATING...")
        print("=" * 70)
        
        if gross_income == 0:
            logger.info("Zero income calculation requested")
            print("\n" + "ℹ️  " + "=" * 68)
            print("ℹ️  ZERO INCOME CALCULATION")
            print("ℹ️  " + "=" * 68)
            print("ℹ️  You have entered zero gross income.")
            print("ℹ️  All tax calculations will be zero.")
            print("ℹ️  This is useful for planning purposes or understanding tax structure.")
            print("ℹ️  " + "=" * 68 + "\n")
        
        results = calculate_all_taxes(gross_income, expenses)
        display_results(results, frequency)
        
        logger.info("Saving calculation results to file")
        filename = save_results_to_file(results, frequency)
        
        if filename:
            # Sanitize file path for logging (show only filename, not full path)
            sanitized_path = os.path.basename(filename)
            logger.info(f"Results saved successfully to {sanitized_path}")
            print(f"\n✅ Results saved to: {filename}")
        else:
            logger.warning("Failed to save results to file")
        
        return results
        
    except (TypeError, AttributeError) as e:
        logger.error(f"Data type error during calculation: {str(e)}", exc_info=True)
        print(f"\n❌ A data error occurred during calculation: {str(e)}")
        print("This may indicate corrupted data. Please try again.")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Data structure error during calculation: {str(e)}", exc_info=True)
        print(f"\n❌ A data structure error occurred: {str(e)}")
        print("This is an internal error. Please contact support.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during calculation: {str(e)}", exc_info=True)
        print(f"\n❌ An unexpected error occurred during calculation: {str(e)}")
        print("Please try again or contact support if the problem persists.")
        return None


# ============================================================================
# MAIN APPLICATION LOOP
# ============================================================================

def run_calculator() -> None:
    """
    Main application loop for the tax calculator.
    
    Handles menu navigation and calculation workflow including input collection,
    validation, calculation, display, and file saving.
    """
    logger.info("Starting calculator main loop")
    display_header()
    
    while True:
        try:
            display_main_menu()
            choice = input("Enter your choice (1-2): ").strip()
            
            if choice == '1':
                logger.info("User selected: New Calculation")
                print("\n" + "=" * 70)
                print("NEW TAX CALCULATION")
                print("=" * 70)
                
                gross_income = get_gross_income()
                expenses = get_deductible_expenses(gross_income)
                frequency = display_frequency_menu()
                
                if confirm_inputs(gross_income, expenses, frequency):
                    perform_calculation(gross_income, expenses, frequency)
                else:
                    logger.info("Calculation cancelled by user")
                    print("\n❌ Calculation cancelled. Returning to main menu.")
                    continue
                
            elif choice == '2':
                logger.info("User selected: Exit")
                print("\n" + "=" * 70)
                print("Thank you for using the Greek Freelancer Tax Calculator!")
                print("=" * 70 + "\n")
                sys.exit(0)
                
            else:
                logger.debug(f"Invalid menu choice entered: '{choice}'")
                print("❌ Invalid choice. Please enter 1 or 2.")
                
        except (EOFError, KeyboardInterrupt):
            logger.info("User interrupted application")
            print("\n\n" + "=" * 70)
            print("Application interrupted. Exiting gracefully...")
            print("=" * 70 + "\n")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}", exc_info=True)
            print(f"\n❌ An unexpected error occurred: {str(e)}")
            print("Returning to main menu...")


# ============================================================================
# COMMAND LINE ARGUMENT PARSING
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for both calculation and logging configuration.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Greek Freelancer Tax Calculator - Calculate taxes, VAT, and social security contributions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  python main.py
  
  # Non-interactive mode
  python main.py --income 50000 --expenses 10000 --frequency monthly
  
  # Hybrid mode (prompts only for missing values)
  python main.py --income 50000
  
  # Custom output file
  python main.py --income 50000 --expenses 10000 --frequency quarterly --output my_taxes.txt
  
  # Quiet mode (only show results, no status messages)
  python main.py --income 50000 --expenses 10000 --frequency annual --quiet
  
  # Strict non-interactive (fail if required args missing)
  python main.py --income 50000 --expenses 10000 --frequency monthly --no-interactive
  
  # Show version
  python main.py --version
        """
    )
    
    # Version flag
    parser.add_argument(
        '--version',
        action='version',
        version='Greek Freelancer Tax Calculator v1.0.0'
    )
    
    # Calculation arguments group
    calc_group = parser.add_argument_group('Calculation Options')
    calc_group.add_argument(
        '--income',
        type=str,
        metavar='AMOUNT',
        help='Gross annual income in euros (e.g., 50000 for €50,000)'
    )
    calc_group.add_argument(
        '--expenses',
        type=str,
        metavar='AMOUNT',
        help='Deductible business expenses in euros (e.g., 10000 for €10,000)'
    )
    calc_group.add_argument(
        '--frequency',
        type=str,
        choices=['monthly', 'quarterly', 'annual'],
        metavar='FREQUENCY',
        help='Payment frequency: monthly, quarterly, or annual'
    )
    calc_group.add_argument(
        '--output',
        type=str,
        metavar='PATH',
        help='Custom output file path (if not specified, auto-generates timestamped file)'
    )
    calc_group.add_argument(
        '--no-interactive',
        action='store_true',
        help='Non-interactive mode - fail if required arguments are missing (requires --income, --expenses, --frequency)'
    )
    
    # Logging arguments group
    log_group = parser.add_argument_group('Logging Options')
    log_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level to console)'
    )
    log_group.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode - show only warnings and errors to console'
    )
    log_group.add_argument(
        '--log-file',
        type=str,
        metavar='PATH',
        help='Custom log file path (default: tax_calculator_debug.log)'
    )
    log_group.add_argument(
        '--no-log-file',
        action='store_true',
        help='Disable file logging (useful for privacy-conscious users)'
    )
    
    args = parser.parse_args()
    
    # Validate mutually exclusive options
    if args.verbose and args.quiet:
        parser.error("--verbose and --quiet are mutually exclusive")
    
    # Validate --no-interactive mode requirements
    if args.no_interactive:
        missing_args = []
        if args.income is None:
            missing_args.append('--income')
        if args.expenses is None:
            missing_args.append('--expenses')
        if args.frequency is None:
            missing_args.append('--frequency')
        
        if missing_args:
            parser.error(
                f"--no-interactive mode requires all of: --income, --expenses, --frequency\n"
                f"Missing: {', '.join(missing_args)}"
            )
    
    return args


def validate_cli_arguments(args: argparse.Namespace) -> Optional[Tuple[Decimal, Decimal, str]]:
    """
    Validate CLI arguments and return validated values.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Optional[tuple]: (income, expenses, frequency) if all provided and valid, None otherwise
        
    Raises:
        SystemExit: If validation fails with exit code 1
    """
    logger.debug("Validating CLI arguments")
    
    # If no calculation args provided, return None (interactive mode)
    if args.income is None and args.expenses is None and args.frequency is None:
        logger.debug("No calculation arguments provided - using interactive mode")
        return None
    
    validated_income = None
    validated_expenses = None
    validated_frequency = None
    
    # Validate income if provided
    if args.income is not None:
        try:
            validated_income = validate_non_negative_number(args.income, "Income")
            if validated_income > 0:
                validate_realistic_amount(validated_income, "Income")
            logger.debug(f"CLI income validated: {validated_income}")
        except ValueError as e:
            logger.error(f"Invalid --income argument: {e}")
            print(f"❌ Error: --income must be a positive number, got: {args.income}")
            print(f"   {str(e)}")
            sys.exit(1)
    
    # Validate expenses if provided
    if args.expenses is not None:
        try:
            validated_expenses = validate_non_negative_number(args.expenses, "Expenses")
            validate_realistic_amount(validated_expenses, "Expenses")
            logger.debug(f"CLI expenses validated: {validated_expenses}")
        except ValueError as e:
            logger.error(f"Invalid --expenses argument: {e}")
            print(f"❌ Error: --expenses must be a non-negative number, got: {args.expenses}")
            print(f"   {str(e)}")
            sys.exit(1)
    
    # Validate expenses against income if both provided
    if validated_income is not None and validated_expenses is not None:
        try:
            validate_expenses_against_income(validated_expenses, validated_income)
        except ValueError as e:
            logger.error(f"Expenses validation failed: {e}")
            print(f"❌ Error: {str(e)}")
            sys.exit(1)
    
    # Frequency is already validated by argparse choices
    if args.frequency is not None:
        validated_frequency = args.frequency
        logger.debug(f"CLI frequency validated: {validated_frequency}")
    
    # Return validated values if all are provided, None if partial
    if validated_income is not None and validated_expenses is not None and validated_frequency is not None:
        logger.info("All CLI calculation arguments validated successfully")
        return (validated_income, validated_expenses, validated_frequency)
    else:
        logger.debug("Partial CLI arguments provided - will use hybrid mode")
        return None


def run_calculator_with_args(args: argparse.Namespace) -> None:
    """
    Run calculator with command-line arguments (non-interactive or hybrid mode).
    
    Args:
        args: Parsed command line arguments
    """
    logger.info("Running calculator with CLI arguments")
    
    # Validate provided arguments
    validated = validate_cli_arguments(args)
    
    # Initialize values
    gross_income = None
    expenses = None
    frequency = None
    
    if validated:
        # Non-interactive mode - all args provided
        logger.info("Non-interactive mode: all required arguments provided")
        gross_income, expenses, frequency = validated
        
        # Display inputs (not a prompt, just showing what was provided)
        if not args.quiet:
            print("\n" + "=" * 70)
            print("CALCULATION PARAMETERS (from command line)")
            print("=" * 70)
            print(f"Gross Annual Income:       {format_currency(gross_income)}")
            print(f"Deductible Expenses:       {format_currency(expenses)}")
            print(f"Payment Frequency:         {frequency.capitalize()}")
            print("=" * 70)
    else:
        # Hybrid mode - prompt for missing values
        logger.info("Hybrid mode: prompting for missing arguments")
        
        if not args.quiet:
            print("\n" + "=" * 70)
            print("HYBRID MODE: Some arguments provided via command line")
            print("You will be prompted for any missing required values")
            print("=" * 70)
        
        # Get income (from CLI or prompt)
        if args.income is not None:
            try:
                gross_income = validate_non_negative_number(args.income, "Income")
                if gross_income > 0:
                    validate_realistic_amount(gross_income, "Income")
                logger.info(f"Using income from CLI: {gross_income}")
                if not args.quiet:
                    print(f"\n✓ Using income from command line: {format_currency(gross_income)}")
            except ValueError as e:
                logger.error(f"Invalid --income argument: {e}")
                print(f"❌ Error: Invalid --income value: {args.income}")
                print(f"   {str(e)}")
                sys.exit(1)
        else:
            gross_income = get_gross_income()
        
        # Get expenses (from CLI or prompt)
        if args.expenses is not None:
            try:
                expenses = validate_non_negative_number(args.expenses, "Expenses")
                validate_realistic_amount(expenses, "Expenses")
                validate_expenses_against_income(expenses, gross_income)
                logger.info(f"Using expenses from CLI: {expenses}")
                if not args.quiet:
                    print(f"✓ Using expenses from command line: {format_currency(expenses)}")
            except ValueError as e:
                logger.error(f"Invalid --expenses argument: {e}")
                print(f"❌ Error: Invalid --expenses value: {args.expenses}")
                print(f"   {str(e)}")
                sys.exit(1)
        else:
            expenses = get_deductible_expenses(gross_income)
        
        # Get frequency (from CLI or prompt)
        if args.frequency is not None:
            frequency = args.frequency
            logger.info(f"Using frequency from CLI: {frequency}")
            if not args.quiet:
                print(f"✓ Using payment frequency from command line: {frequency.capitalize()}")
        else:
            frequency = display_frequency_menu()
        
        # Confirm inputs in hybrid mode unless --no-interactive
        if not args.no_interactive:
            if not confirm_inputs(gross_income, expenses, frequency):
                logger.info("User cancelled calculation in hybrid mode")
                print("\n❌ Calculation cancelled.")
                sys.exit(0)
    
    # Perform calculation
    logger.info("Executing tax calculation")
    
    # Handle custom output file if specified
    custom_output = args.output if hasattr(args, 'output') else None
    
    try:
        results = calculate_all_taxes(gross_income, expenses)
        display_results(results, frequency)
        
        # Save to file
        if custom_output:
            logger.info(f"Saving results to custom output file: {custom_output}")
            try:
                # Sanitize custom filename (basename only)
                custom_filename = os.path.basename(custom_output)
                sanitized = sanitize_filename(custom_filename)
                ensure_output_directory()
                custom_path = os.path.join(OUTPUT_DIR, sanitized)
                
                content_lines = _build_file_content_lines(results, frequency)
                with open(custom_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(content_lines))
                
                logger.info(f"Results saved to custom file: {sanitized}")
                print(f"\n✅ Results saved to: {custom_path}")
            except Exception as e:
                logger.error(f"Failed to save to custom output file: {e}")
                print(f"\n⚠️  Warning: Could not save to custom output file: {str(e)}")
                print(f"   Saving to default location instead...")
                filename = save_results_to_file(results, frequency)
                if filename:
                    print(f"✅ Results saved to: {filename}")
        else:
            filename = save_results_to_file(results, frequency)
            if filename:
                logger.info(f"Results saved to file: {os.path.basename(filename)}")
                print(f"\n✅ Results saved to: {filename}")
        
        logger.info("Tax calculation completed successfully")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Calculation failed: {str(e)}", exc_info=True)
        print(f"\n❌ Calculation failed: {str(e)}")
        sys.exit(1)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging based on CLI arguments
    setup_logging(
        verbose=args.verbose,
        quiet=args.quiet,
        log_file=args.log_file,
        no_log_file=args.no_log_file
    )
    
    logger.info("Greek Freelancer Tax Calculator starting")
    logger.debug(f"Logging configuration: verbose={args.verbose}, quiet={args.quiet}, "
                f"log_file={args.log_file}, no_log_file={args.no_log_file}")
    
    # Detect mode: interactive vs non-interactive/hybrid
    has_calc_args = (args.income is not None or 
                     args.expenses is not None or 
                     args.frequency is not None or
                     args.no_interactive)
    
    try:
        if has_calc_args:
            # Non-interactive or hybrid mode
            logger.info("Running in CLI argument mode (non-interactive or hybrid)")
            run_calculator_with_args(args)
        else:
            # Pure interactive mode (original behavior)
            logger.info("Running in interactive mode (no CLI arguments provided)")
            run_calculator()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n\n" + "=" * 70)
        print("Application interrupted. Exiting gracefully...")
        print("=" * 70 + "\n")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error in application: {str(e)}", exc_info=True)
        print(f"\n❌ Fatal error: {str(e)}")
        print("Application will now exit.")
        sys.exit(1)
