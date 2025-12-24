#!/usr/bin/env python3
"""
Greek Tax Calculator - Configuration Module

This module centralizes all tax-related configuration, rates, brackets, and limits
used by the Greek Freelancer Tax Calculator. All values are based on 2024 Greek
tax legislation and should be updated annually or when tax laws change.

CONFIGURATION PHILOSOPHY:
=========================
This configuration module uses immutable dataclasses (frozen=True) to prevent
accidental modification of tax rates during runtime. All monetary values use
Python's Decimal type for precise financial calculations.

HOW TO UPDATE FOR A NEW TAX YEAR:
==================================
1. Verify current tax rates with official Greek sources (see SOURCES below)
2. Update TAX_YEAR constant to the new year
3. Update LAST_UPDATED with the verification date
4. Update any changed rates in the relevant sections:
   - INCOME_TAX_BRACKETS: Check for bracket threshold or rate changes
   - VAT_RATE: Verify standard VAT rate (rarely changes)
   - EFKA rates: Check for social security contribution changes
   - MAX_ANNUAL_INCOME: Review validation limit if needed
5. Run configuration validation to ensure integrity
6. Update RATE_SOURCES with new reference URLs if changed
7. Run all tests to ensure backward compatibility

OFFICIAL SOURCES FOR TAX RATES:
================================
These are the authoritative sources for Greek tax rates. Always verify rates
from these sources before updating:

1. INCOME TAX:
   - Authority: AADE (Independent Authority for Public Revenue)
   - Website: https://www.aade.gr
   - Law: 4172/2013 (Greek Income Tax Code), Articles 9 and 15
   - English info: https://www.aade.gr/english

2. SOCIAL SECURITY (EFKA):
   - Authority: EFKA (e-EFKA - Unified Social Security Fund)
   - Website: https://www.efka.gov.gr
   - Law: 4387/2016 (Unified Social Security System)
   - For self-employed: Check "Ελεύθεροι Επαγγελματίες" section

3. VAT:
   - Authority: AADE (same as income tax)
   - Law: Greek VAT Law 2859/2000, Article 21
   - EU Directive: 2006/112/EC
   - Website: https://www.aade.gr

4. General Tax Information (English):
   - OECD Tax Database: https://www.oecd.org/tax/
   - PWC Greece: https://taxsummaries.pwc.com/greece
   - Deloitte Greece: International Tax guides

IMPORTANT: Greek tax law changes frequently. This calculator may not reflect
the most current rates. Always verify with official sources and consult a
certified tax professional (λογιστής) for authoritative advice.

VALIDATION AND INTEGRITY:
==========================
The validate_configuration() function runs automatically on module import to
ensure configuration integrity. It checks:
- Tax rates are in valid range (0-1 for decimal representation)
- Tax brackets are in ascending order with no gaps
- EFKA rates sum correctly to the total
- All required fields are present and valid types

If validation fails, an exception is raised with details about the issue.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Tuple, Final
from datetime import datetime

__version__ = "1.0.0"

# ============================================================================
# METADATA - Tax Year and Update Information
# ============================================================================

# Tax year these rates apply to
# UPDATE THIS when updating rates for a new year
TAX_YEAR: Final[int] = 2024

# Date when tax rates were last verified against official sources
# UPDATE THIS whenever you verify/update rates (format: YYYY-MM-DD)
LAST_UPDATED: Final[str] = "2024-01-15"

# Human-readable timestamp of last configuration update
LAST_UPDATED_TIMESTAMP: Final[datetime] = datetime.fromisoformat(f"{LAST_UPDATED}T00:00:00")

# Sources where rates were verified (for audit trail)
RATE_SOURCES: Final[dict] = {
    'income_tax': 'AADE - Law 4172/2013, Articles 9 and 15 - https://www.aade.gr',
    'vat': 'AADE - Greek VAT Law 2859/2000, Article 21 - https://www.aade.gr',
    'efka': 'EFKA - Law 4387/2016 - https://www.efka.gov.gr',
    'verified_date': LAST_UPDATED
}


# ============================================================================
# TAX BRACKET DATA STRUCTURE
# ============================================================================

@dataclass(frozen=True)
class TaxBracket:
    """
    Immutable data structure representing a progressive income tax bracket.
    
    Attributes:
        upper_limit (Decimal): Upper income threshold for this bracket (EUR)
                              Use Decimal('inf') for the highest bracket
        rate (Decimal): Tax rate as decimal (e.g., 0.09 for 9%)
        description (str): Human-readable description of the bracket
    
    Examples:
        # First bracket: €0 - €10,000 at 9%
        TaxBracket(
            upper_limit=Decimal('10000.00'),
            rate=Decimal('0.09'),
            description='€0 - €10,000: 9%'
        )
        
        # Top bracket: Over €40,000 at 44%
        TaxBracket(
            upper_limit=Decimal('inf'),
            rate=Decimal('0.44'),
            description='Over €40,000: 44%'
        )
    """
    upper_limit: Decimal
    rate: Decimal
    description: str
    
    def __post_init__(self):
        """Validate bracket data on creation."""
        # Convert inf string to actual infinity if needed
        if isinstance(self.upper_limit, str) and self.upper_limit == 'inf':
            object.__setattr__(self, 'upper_limit', Decimal('inf'))
        
        # Validate rate is between 0 and 1
        if not (Decimal('0') <= self.rate <= Decimal('1')):
            raise ValueError(
                f"Tax rate must be between 0 and 1 (got {self.rate}). "
                f"Use decimal format: 0.09 for 9%, not 9."
            )
        
        # Validate upper_limit is positive or infinity
        if self.upper_limit != Decimal('inf') and self.upper_limit <= 0:
            raise ValueError(
                f"Upper limit must be positive or infinity (got {self.upper_limit})"
            )


# ============================================================================
# INCOME TAX CONFIGURATION
# ============================================================================

# Progressive Income Tax Brackets for 2024
# Source: Law 4172/2013, Articles 9 and 15 (Greek Income Tax Code)
# Last verified: 2024-01-15 via AADE (https://www.aade.gr)
#
# How progressive taxation works:
# - Income is taxed in segments at increasing rates
# - Each bracket only applies to the portion of income within that range
# - Example: €25,000 income is taxed as:
#   * €10,000 at 9% = €900
#   * €10,000 at 22% = €2,200
#   * €5,000 at 28% = €1,400
#   * Total tax = €4,500 (effective rate: 18%)
#
# Bracket transitions:
# - €0 to €10,000: First bracket
# - €10,000.01 to €20,000: Second bracket
# - €20,000.01 to €30,000: Third bracket
# - €30,000.01 to €40,000: Fourth bracket
# - Over €40,000: Top bracket
INCOME_TAX_BRACKETS: Final[Tuple[TaxBracket, ...]] = (
    TaxBracket(
        upper_limit=Decimal('10000.00'),
        rate=Decimal('0.09'),
        description='€0 - €10,000: 9%'
    ),
    TaxBracket(
        upper_limit=Decimal('20000.00'),
        rate=Decimal('0.22'),
        description='€10,001 - €20,000: 22%'
    ),
    TaxBracket(
        upper_limit=Decimal('30000.00'),
        rate=Decimal('0.28'),
        description='€20,001 - €30,000: 28%'
    ),
    TaxBracket(
        upper_limit=Decimal('40000.00'),
        rate=Decimal('0.36'),
        description='€30,001 - €40,000: 36%'
    ),
    TaxBracket(
        upper_limit=Decimal('inf'),
        rate=Decimal('0.44'),
        description='Over €40,000: 44%'
    ),
)


# ============================================================================
# VAT (VALUE ADDED TAX) CONFIGURATION
# ============================================================================

# Standard VAT Rate for Greece (24%)
# Source: Greek VAT Law 2859/2000, Article 21
# EU Directive: 2006/112/EC
# Last verified: 2024-01-15 via AADE
#
# This is the standard rate applicable to most professional services
# provided by freelancers in Greece.
#
# Notes:
# - Reduced rates (13%, 6%) exist for specific goods/services
# - Most freelance professional services use the standard 24% rate
# - VAT is collected from clients and remitted to tax authorities
# - VAT is NOT part of the freelancer's taxable income
VAT_RATE: Final[Decimal] = Decimal('0.24')  # 24%


# ============================================================================
# EFKA SOCIAL SECURITY CONFIGURATION
# ============================================================================

# EFKA Social Security Contribution Rates
# Source: Law 4387/2016 (Unified Social Security System)
# Administering body: EFKA (e-EFKA - Unified Social Security Fund)
# Last verified: 2024-01-15 via https://www.efka.gov.gr
#
# EFKA provides comprehensive social insurance including:
# - Healthcare coverage
# - Pension contributions
# - Unemployment insurance
# - Disability insurance
#
# Rate breakdown for self-employed professionals:
# - Main insurance: 13.33% (primary social security and pension)
# - Additional contributions: 6.67% (healthcare, auxiliary pension, etc.)
# - Total: 20.00% of gross income
#
# IMPORTANT LIMITATIONS (not implemented in this calculator):
# 1. Minimum monthly contribution: ~€230-250/month (2024)
# 2. Maximum insurable income: ~€81,000/year (2024)
# 3. Reduced rates for new professionals (first 5 years)
# 4. Different schemes for specific professions (engineers, doctors, etc.)

# Main insurance contribution rate (13.33%)
EFKA_MAIN_RATE: Final[Decimal] = Decimal('0.1333')

# Additional contributions rate (6.67%)
# Includes healthcare, auxiliary pension, and other benefits
EFKA_ADDITIONAL_RATE: Final[Decimal] = Decimal('0.0667')

# Total EFKA rate (20.00%)
# This is automatically calculated to ensure consistency
EFKA_TOTAL_RATE: Final[Decimal] = EFKA_MAIN_RATE + EFKA_ADDITIONAL_RATE


# ============================================================================
# VALIDATION LIMITS
# ============================================================================

# Maximum realistic annual income for validation (€10 million)
# This limit helps catch data entry errors (typos with extra zeros).
# While technically possible for ultra-high earners, income above this
# threshold is extremely rare for freelancers and likely indicates a
# mistake (e.g., entering 35000000 instead of 35000).
#
# Used by input validation in the CLI application.
MAX_ANNUAL_INCOME: Final[Decimal] = Decimal('10000000')


# ============================================================================
# PAYMENT SCHEDULE CONFIGURATION
# ============================================================================

# Valid payment frequency options for tax payment schedules
# These are the standard payment frequencies used in Greece:
# - 'monthly': 12 payments per year (most common for high earners)
# - 'quarterly': 4 payments per year (common for moderate earners)
# - 'annual': 1 payment per year (less common, for low earners)
VALID_FREQUENCIES: Final[Tuple[str, ...]] = ('monthly', 'quarterly', 'annual')


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_configuration() -> None:
    """
    Validate configuration integrity and consistency.
    
    This function checks:
    1. Tax brackets are in ascending order
    2. Tax brackets have no gaps (each starts where previous ended)
    3. Tax rates are in valid range (0-1)
    4. EFKA rates sum correctly
    5. All required constants are defined
    
    Raises:
        ValueError: If any validation check fails
        TypeError: If configuration values have wrong types
    
    This function is called automatically on module import to catch
    configuration errors early.
    """
    # Validate tax brackets are in ascending order
    previous_limit = Decimal('0')
    for i, bracket in enumerate(INCOME_TAX_BRACKETS):
        # Check type
        if not isinstance(bracket, TaxBracket):
            raise TypeError(
                f"INCOME_TAX_BRACKETS[{i}] must be TaxBracket instance, "
                f"got {type(bracket).__name__}"
            )
        
        # Check ascending order (skip infinity check)
        if bracket.upper_limit != Decimal('inf'):
            if bracket.upper_limit <= previous_limit:
                raise ValueError(
                    f"Tax bracket {i} upper limit ({bracket.upper_limit}) must be "
                    f"greater than previous bracket ({previous_limit})"
                )
            previous_limit = bracket.upper_limit
        
        # Rate validation is already done in TaxBracket.__post_init__
    
    # Verify last bracket has infinity upper limit
    if INCOME_TAX_BRACKETS[-1].upper_limit != Decimal('inf'):
        raise ValueError(
            "Last tax bracket must have infinite upper limit "
            "(use Decimal('inf'))"
        )
    
    # Validate VAT rate
    if not (Decimal('0') <= VAT_RATE <= Decimal('1')):
        raise ValueError(
            f"VAT_RATE must be between 0 and 1 (got {VAT_RATE}). "
            f"Use decimal format: 0.24 for 24%, not 24."
        )
    
    # Validate EFKA rates
    if not (Decimal('0') <= EFKA_MAIN_RATE <= Decimal('1')):
        raise ValueError(
            f"EFKA_MAIN_RATE must be between 0 and 1 (got {EFKA_MAIN_RATE})"
        )
    
    if not (Decimal('0') <= EFKA_ADDITIONAL_RATE <= Decimal('1')):
        raise ValueError(
            f"EFKA_ADDITIONAL_RATE must be between 0 and 1 "
            f"(got {EFKA_ADDITIONAL_RATE})"
        )
    
    # Verify EFKA total is sum of components (with small tolerance for decimal precision)
    expected_total = EFKA_MAIN_RATE + EFKA_ADDITIONAL_RATE
    if abs(EFKA_TOTAL_RATE - expected_total) > Decimal('0.0001'):
        raise ValueError(
            f"EFKA_TOTAL_RATE ({EFKA_TOTAL_RATE}) must equal "
            f"EFKA_MAIN_RATE + EFKA_ADDITIONAL_RATE ({expected_total})"
        )
    
    # Validate MAX_ANNUAL_INCOME
    if MAX_ANNUAL_INCOME <= 0:
        raise ValueError(
            f"MAX_ANNUAL_INCOME must be positive (got {MAX_ANNUAL_INCOME})"
        )
    
    # Validate VALID_FREQUENCIES
    if not VALID_FREQUENCIES:
        raise ValueError("VALID_FREQUENCIES cannot be empty")
    
    for freq in VALID_FREQUENCIES:
        if not isinstance(freq, str):
            raise TypeError(
                f"VALID_FREQUENCIES must contain strings, got {type(freq).__name__}"
            )
    
    # Validate TAX_YEAR
    current_year = datetime.now().year
    if not (2020 <= TAX_YEAR <= current_year + 5):
        raise ValueError(
            f"TAX_YEAR ({TAX_YEAR}) seems invalid. "
            f"Expected range: 2020-{current_year + 5}"
        )


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Validate configuration on module import
# This ensures any configuration errors are caught immediately
try:
    validate_configuration()
except (ValueError, TypeError) as e:
    raise RuntimeError(
        f"Configuration validation failed: {e}\n"
        f"Please check config.py for errors."
    ) from e


# ============================================================================
# SUMMARY FOR QUICK REFERENCE
# ============================================================================

def print_config_summary() -> str:
    """
    Generate a human-readable summary of current tax configuration.
    
    Returns:
        str: Formatted summary of all tax rates and brackets
    
    Example:
        >>> print(print_config_summary())
        Greek Tax Configuration Summary (2024)
        ======================================
        ...
    """
    lines = [
        f"Greek Tax Configuration Summary ({TAX_YEAR})",
        "=" * 60,
        f"Last Updated: {LAST_UPDATED}",
        "",
        "Income Tax Brackets:",
        "-" * 60
    ]
    
    for bracket in INCOME_TAX_BRACKETS:
        lines.append(f"  {bracket.description}")
    
    lines.extend([
        "",
        "Other Rates:",
        "-" * 60,
        f"  VAT Rate: {VAT_RATE * 100:.2f}%",
        f"  EFKA Main Rate: {EFKA_MAIN_RATE * 100:.2f}%",
        f"  EFKA Additional Rate: {EFKA_ADDITIONAL_RATE * 100:.2f}%",
        f"  EFKA Total Rate: {EFKA_TOTAL_RATE * 100:.2f}%",
        "",
        "Validation Limits:",
        "-" * 60,
        f"  Maximum Annual Income: €{MAX_ANNUAL_INCOME:,.0f}",
        "",
        "Payment Frequencies:",
        "-" * 60,
        f"  {', '.join(VALID_FREQUENCIES)}",
        "=" * 60
    ])
    
    return "\n".join(lines)


# If module is run directly, print configuration summary
if __name__ == "__main__":
    print(print_config_summary())
