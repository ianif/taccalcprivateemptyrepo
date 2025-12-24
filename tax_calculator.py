#!/usr/bin/env python3
"""
Greek Tax Calculator Module for Freelancers

This module provides comprehensive tax calculation functions for Greek freelancers,
implementing the 2024 Greek tax law requirements including:
- Progressive income tax brackets
- VAT (Value Added Tax)
- EFKA social security contributions

All monetary values use Decimal type for exact financial calculations with
precision to 2 decimal places, eliminating floating-point rounding errors.

TAX RATE SOURCES AND VERIFICATION
==================================

This calculator implements tax rates based on official Greek tax legislation:

INCOME TAX BRACKETS:
    Source: Law 4172/2013 (Greek Income Tax Code), as amended
    Reference: Articles 9 and 15
    Official source: AADE (Independent Authority for Public Revenue)
    URL: https://www.aade.gr
    
    The progressive tax brackets apply to all individual income in Greece,
    including income from self-employment and freelance activities.

EFKA SOCIAL SECURITY CONTRIBUTIONS:
    Source: Law 4387/2016 (Unified Social Security System)
    Administering body: EFKA (e-EFKA - Unified Social Security Fund)
    URL: https://www.efka.gov.gr
    
    Rates apply to self-employed professionals and freelancers.
    Note: EFKA has minimum monthly contributions (approx. €230-250/month as of 2024)
    and maximum insurable income caps that are not implemented in this calculator.

VAT (VALUE ADDED TAX):
    Source: Greek VAT Law 2859/2000, as amended
    Reference: Article 21 (Standard rate)
    EU Directive: 2006/112/EC
    URL: https://www.aade.gr
    
    Standard rate applies to most professional services. Reduced rates
    (13%, 6%) exist but are not applicable to most freelance services.

LAST VERIFICATION DATE: 2024-01-15

IMPORTANT ASSUMPTIONS AND LIMITATIONS:
=======================================

This calculator makes the following assumptions:

1. STANDARD TAXATION REGIME
   - Assumes the standard progressive tax system applies
   - Does not account for simplified/presumptive tax regimes
   - Does not include special professional category rates

2. NO SPECIAL DEDUCTIONS OR CREDITS
   - Does not calculate personal tax-free threshold adjustments
   - Does not include dependent allowances
   - Does not account for special professional expense percentages
   - Does not include tax credits for insurance premiums paid

3. EFKA SIMPLIFICATIONS
   - Uses flat 20% rate on all gross income
   - Does NOT enforce minimum monthly contributions (~€230-250/month)
   - Does NOT apply maximum insurable income caps (~€81,000/year)
   - Does NOT account for reduced rates for new professionals
   - Does NOT include OAEE contributions for certain professions

4. SOLIDARITY CONTRIBUTION NOT INCLUDED
   - The "Special Solidarity Contribution" (2.2%-10% on income >€12,000)
   - was suspended for 2024 but may be reinstated - NOT CALCULATED

5. OTHER EXCLUSIONS
   - Real estate tax (ENFIA)
   - Advanced prepayments (προκαταβολή φόρου)
   - Municipal taxes and fees
   - Professional chamber fees
   - Withholding tax considerations

6. VAT ASSUMPTIONS
   - Assumes all income is VAT-eligible at standard rate
   - Does not account for VAT exemptions
   - Does not calculate input VAT deductions
   - Simplified calculation for estimation only

DISCLAIMER:
===========
This calculator is provided for INFORMATIONAL and PLANNING purposes only.
Greek tax law is complex and changes frequently. Individual circumstances,
professional categories, and special regimes may significantly affect actual
tax obligations. 

**Always consult with a certified Greek tax professional (λογιστής) and
verify current rates with official sources before making financial decisions.**

For official information, consult:
- AADE (Tax Authority): https://www.aade.gr
- EFKA (Social Security): https://www.efka.gov.gr  
- Taxisnet (Tax Portal): https://www.gsis.gr
"""

import logging
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict, List, Tuple, Union

# Import configuration from centralized config module
from config import (
    INCOME_TAX_BRACKETS,
    VAT_RATE,
    EFKA_MAIN_RATE,
    EFKA_ADDITIONAL_RATE,
    EFKA_TOTAL_RATE,
    VALID_FREQUENCIES,
    TAX_YEAR,
    LAST_UPDATED
)

# Import data models
from models import (
    BracketBreakdown,
    IncomeTaxBreakdown,
    VATCalculation,
    SocialSecurityCalculation,
    TaxCalculationResult,
    PaymentInstallment,
    PaymentSchedule
)

__author__ = "Tax Calculator"
__version__ = "1.0.0"

# Create logger for this module
logger = logging.getLogger(__name__)

# Set decimal context for consistent financial rounding
getcontext().rounding = ROUND_HALF_UP

# ============================================================================
# CONFIGURATION NOTE
# ============================================================================
# All tax rates, brackets, and constants have been moved to config.py
# for centralized configuration management. This improves maintainability
# and makes it easier to update rates when tax laws change.
#
# See config.py for:
# - INCOME_TAX_BRACKETS: Progressive tax bracket thresholds and rates
# - VAT_RATE: Value Added Tax rate (24%)
# - EFKA rates: Social security contribution rates
# - VALID_FREQUENCIES: Payment schedule options
# - TAX_YEAR and LAST_UPDATED: Version metadata


# ============================================================================
# CORE TAX CALCULATION FUNCTIONS
# ============================================================================

def calculate_taxable_income(gross_income: Union[Decimal, float, int, str], 
                            deductible_expenses: Union[Decimal, float, int, str]) -> Decimal:
    """
    Calculate taxable income after deducting eligible expenses.
    
    Args:
        gross_income: Total gross income in EUR
        deductible_expenses: Total deductible business expenses in EUR
    
    Returns:
        Decimal: Taxable income (minimum 0.00, rounded to 2 decimal places)
    """
    logger.debug("Calculating taxable income")
    gross_income = Decimal(str(gross_income))
    deductible_expenses = Decimal(str(deductible_expenses))
    
    taxable = max(Decimal('0'), gross_income - deductible_expenses)
    result = taxable.quantize(Decimal('0.01'), ROUND_HALF_UP)
    logger.debug(f"Taxable income calculated: {result}")
    return result


def calculate_income_tax(taxable_income: Union[Decimal, float, int, str]) -> IncomeTaxBreakdown:
    """
    Calculate progressive income tax based on Greek tax brackets for 2024.
    
    Applies progressive taxation where each bracket is taxed at its own rate.
    
    Args:
        taxable_income: Taxable income in EUR (after deductions)
    
    Returns:
        IncomeTaxBreakdown: Income tax calculation with bracket-by-bracket details
    """
    logger.debug("Calculating income tax using progressive brackets")
    taxable_income = Decimal(str(taxable_income))
    
    if taxable_income <= 0:
        logger.debug("Taxable income is zero or negative - returning zero tax")
        return IncomeTaxBreakdown(
            total_tax=Decimal('0.00'),
            effective_rate=Decimal('0.00'),
            bracket_breakdown=[]
        )
    
    logger.debug(f"Processing {len(INCOME_TAX_BRACKETS)} tax brackets")
    total_tax = Decimal('0')
    bracket_breakdown = []
    remaining_income = taxable_income
    previous_bracket_limit = Decimal('0')
    
    for i, bracket in enumerate(INCOME_TAX_BRACKETS):
        if remaining_income <= 0:
            break
        
        bracket_limit = bracket.upper_limit
        rate = bracket.rate
        
        if bracket_limit == Decimal('inf'):
            taxable_in_bracket = remaining_income
        else:
            bracket_size = bracket_limit - previous_bracket_limit
            taxable_in_bracket = min(remaining_income, bracket_size)
        
        tax_in_bracket = taxable_in_bracket * rate
        total_tax += tax_in_bracket
        
        logger.debug(f"Bracket {i+1}: amount={taxable_in_bracket.quantize(Decimal('0.01'), ROUND_HALF_UP)}, "
                    f"rate={rate*100:.2f}%, tax={tax_in_bracket.quantize(Decimal('0.01'), ROUND_HALF_UP)}")
        
        bracket_breakdown.append(BracketBreakdown(
            bracket_min=previous_bracket_limit.quantize(Decimal('0.01'), ROUND_HALF_UP),
            bracket_max='unlimited' if bracket_limit == Decimal('inf') else bracket_limit.quantize(Decimal('0.01'), ROUND_HALF_UP),
            rate=(rate * 100).quantize(Decimal('0.01'), ROUND_HALF_UP),
            taxable_amount=taxable_in_bracket.quantize(Decimal('0.01'), ROUND_HALF_UP),
            tax_amount=tax_in_bracket.quantize(Decimal('0.01'), ROUND_HALF_UP)
        ))
        
        remaining_income -= taxable_in_bracket
        if bracket_limit != Decimal('inf'):
            previous_bracket_limit = bracket_limit
    
    effective_rate = (total_tax / taxable_income * 100) if taxable_income > 0 else Decimal('0')
    total_tax_rounded = total_tax.quantize(Decimal('0.01'), ROUND_HALF_UP)
    logger.debug(f"Income tax calculation complete: total_tax={total_tax_rounded}, effective_rate={effective_rate.quantize(Decimal('0.01'), ROUND_HALF_UP)}%")
    
    return IncomeTaxBreakdown(
        total_tax=total_tax_rounded,
        effective_rate=effective_rate.quantize(Decimal('0.01'), ROUND_HALF_UP),
        bracket_breakdown=bracket_breakdown
    )


def calculate_vat(gross_income: Union[Decimal, float, int, str]) -> VATCalculation:
    """
    Calculate Value Added Tax (VAT) for Greek freelancers.
    
    Args:
        gross_income: Total gross income in EUR (excluding VAT)
    
    Returns:
        VATCalculation: VAT calculation with amount and rate
    """
    logger.debug(f"Calculating VAT at {VAT_RATE*100}% rate")
    gross_income = Decimal(str(gross_income))
    
    if gross_income <= 0:
        logger.debug("Gross income is zero or negative - returning zero VAT")
        return VATCalculation(
            vat_amount=Decimal('0.00'),
            rate=(VAT_RATE * 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
        )
    
    vat_amount = gross_income * VAT_RATE
    vat_rounded = vat_amount.quantize(Decimal('0.01'), ROUND_HALF_UP)
    logger.debug(f"VAT calculated: {vat_rounded}")
    
    return VATCalculation(
        vat_amount=vat_rounded,
        rate=(VAT_RATE * 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
    )


def calculate_social_security(gross_income: Union[Decimal, float, int, str]) -> SocialSecurityCalculation:
    """
    Calculate EFKA social security contributions for Greek freelancers.
    
    Note: EFKA is calculated on GROSS income, not taxable income.
    
    Args:
        gross_income: Total gross income in EUR
    
    Returns:
        SocialSecurityCalculation: EFKA contribution details
    """
    logger.debug(f"Calculating EFKA social security at {EFKA_TOTAL_RATE*100}% rate")
    gross_income = Decimal(str(gross_income))
    
    if gross_income <= 0:
        logger.debug("Gross income is zero or negative - returning zero EFKA")
        return SocialSecurityCalculation(
            total_contribution=Decimal('0.00'),
            main_insurance=Decimal('0.00'),
            additional_contributions=Decimal('0.00'),
            rate=(EFKA_TOTAL_RATE * 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
        )
    
    main_insurance = gross_income * EFKA_MAIN_RATE
    additional_contributions = gross_income * EFKA_ADDITIONAL_RATE
    total_contribution = gross_income * EFKA_TOTAL_RATE
    
    total_rounded = total_contribution.quantize(Decimal('0.01'), ROUND_HALF_UP)
    logger.debug(f"EFKA calculated: main={main_insurance.quantize(Decimal('0.01'), ROUND_HALF_UP)}, "
                f"additional={additional_contributions.quantize(Decimal('0.01'), ROUND_HALF_UP)}, "
                f"total={total_rounded}")
    
    return SocialSecurityCalculation(
        total_contribution=total_rounded,
        main_insurance=main_insurance.quantize(Decimal('0.01'), ROUND_HALF_UP),
        additional_contributions=additional_contributions.quantize(Decimal('0.01'), ROUND_HALF_UP),
        rate=(EFKA_TOTAL_RATE * 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
    )


def calculate_all_taxes(gross_income: Union[Decimal, float, int, str], 
                       deductible_expenses: Union[Decimal, float, int, str]) -> TaxCalculationResult:
    """
    Calculate all tax components for Greek freelancers.
    
    Calculates taxable income, progressive income tax, VAT, EFKA social security,
    and total tax burden. Note: Income tax is on taxable income, but EFKA and VAT
    are calculated on gross income.
    
    Args:
        gross_income: Total gross income in EUR (excluding VAT)
        deductible_expenses: Total deductible business expenses in EUR
    
    Returns:
        TaxCalculationResult: Comprehensive tax calculation with all components
    """
    logger.debug("Starting comprehensive tax calculation")
    logger.debug(f"Input parameters received (types will be converted to Decimal)")
    
    gross_income = Decimal(str(gross_income))
    deductible_expenses = Decimal(str(deductible_expenses))
    
    if gross_income <= 0:
        logger.warning(f"Zero or negative gross income provided")
        logger.info("Returning zero tax calculation result")
        return TaxCalculationResult(
            gross_income=gross_income.quantize(Decimal('0.01'), ROUND_HALF_UP),
            deductible_expenses=deductible_expenses.quantize(Decimal('0.01'), ROUND_HALF_UP),
            taxable_income=Decimal('0.00'),
            income_tax=calculate_income_tax(0),
            vat=calculate_vat(0),
            social_security=calculate_social_security(0),
            total_taxes=Decimal('0.00'),
            total_obligations=Decimal('0.00'),
            net_income=Decimal('0.00'),
            effective_total_rate=Decimal('0.00')
        )
    
    logger.debug("Calculating individual tax components")
    taxable_income = calculate_taxable_income(gross_income, deductible_expenses)
    income_tax = calculate_income_tax(taxable_income)
    vat = calculate_vat(gross_income)
    social_security = calculate_social_security(gross_income)
    
    logger.debug("Calculating totals and net income")
    total_taxes = income_tax.total_tax + social_security.total_contribution
    total_obligations = total_taxes + vat.vat_amount
    net_income = gross_income - total_taxes
    effective_total_rate = (total_taxes / gross_income * 100) if gross_income > 0 else Decimal('0')
    
    # Log summary at INFO level without sensitive amounts
    logger.info("Tax calculation completed successfully")
    # Log detailed amounts at DEBUG level only
    logger.debug(f"Calculation summary: total_taxes={total_taxes.quantize(Decimal('0.01'), ROUND_HALF_UP)}, "
                f"net_income={net_income.quantize(Decimal('0.01'), ROUND_HALF_UP)}, "
                f"effective_rate={effective_total_rate.quantize(Decimal('0.01'), ROUND_HALF_UP)}%")
    
    return TaxCalculationResult(
        gross_income=gross_income.quantize(Decimal('0.01'), ROUND_HALF_UP),
        deductible_expenses=deductible_expenses.quantize(Decimal('0.01'), ROUND_HALF_UP),
        taxable_income=taxable_income,
        income_tax=income_tax,
        vat=vat,
        social_security=social_security,
        total_taxes=total_taxes.quantize(Decimal('0.01'), ROUND_HALF_UP),
        total_obligations=total_obligations.quantize(Decimal('0.01'), ROUND_HALF_UP),
        net_income=net_income.quantize(Decimal('0.01'), ROUND_HALF_UP),
        effective_total_rate=effective_total_rate.quantize(Decimal('0.01'), ROUND_HALF_UP)
    )


def calculate_payment_schedule(annual_tax: Union[Decimal, float, int, str], 
                              frequency: str = 'monthly') -> PaymentSchedule:
    """
    Calculate payment schedule breakdown for tax payments.
    
    Args:
        annual_tax: Total annual tax amount in EUR
        frequency: Payment frequency ('monthly', 'quarterly', or 'annual')
    
    Returns:
        PaymentSchedule: Payment schedule with installment details
    
    Raises:
        ValueError: If frequency is not one of the valid options
    """
    logger.debug(f"Calculating payment schedule for frequency: {frequency}")
    annual_tax = Decimal(str(annual_tax))
    
    if annual_tax < 0:
        logger.warning("Negative annual tax provided, using 0.00")
        annual_tax = Decimal('0.00')
    
    if frequency.lower() not in VALID_FREQUENCIES:
        logger.error(f"Invalid payment frequency provided: '{frequency}'. Valid options: {VALID_FREQUENCIES}")
        raise ValueError(
            f"Invalid frequency '{frequency}'. Must be one of: {', '.join(VALID_FREQUENCIES)}"
        )
    
    frequency = frequency.lower()
    
    payments_per_year = {
        'monthly': 12,
        'quarterly': 4,
        'annual': 1
    }
    
    num_payments = payments_per_year[frequency]
    payment_amount = annual_tax / num_payments
    
    logger.debug(f"Payment schedule: {num_payments} installments of {payment_amount.quantize(Decimal('0.01'), ROUND_HALF_UP)} each")
    
    schedule = []
    for i in range(1, num_payments + 1):
        schedule.append(PaymentInstallment(
            period_number=i,
            payment_amount=payment_amount.quantize(Decimal('0.01'), ROUND_HALF_UP)
        ))
    
    return PaymentSchedule(
        annual_total=annual_tax.quantize(Decimal('0.01'), ROUND_HALF_UP),
        frequency=frequency,
        number_of_installments=num_payments,
        installment_amount=payment_amount.quantize(Decimal('0.01'), ROUND_HALF_UP),
        schedule=schedule
    )


# ============================================================================
# MODULE TESTING (only runs when module is executed directly)
# ============================================================================

if __name__ == "__main__":
    # This section only runs when the module is executed directly
    # It does not execute when the module is imported
    print("Greek Tax Calculator Module - Test Run")
    print("=" * 60)
    
    # Test case: Freelancer with €50,000 gross income and €10,000 expenses
    test_gross = 50000.0
    test_expenses = 10000.0
    
    print(f"\nTest Case: Gross Income = €{test_gross:,.2f}, Expenses = €{test_expenses:,.2f}")
    print("-" * 60)
    
    results = calculate_all_taxes(test_gross, test_expenses)
    
    print(f"Taxable Income: €{results.taxable_income:,.2f}")
    print(f"Income Tax: €{results.income_tax.total_tax:,.2f}")
    print(f"Social Security (EFKA): €{results.social_security.total_contribution:,.2f}")
    print(f"VAT (24%): €{results.vat.vat_amount:,.2f}")
    print(f"Total Tax Burden: €{results.total_taxes:,.2f}")
    print(f"Net Income: €{results.net_income:,.2f}")
    print(f"Effective Tax Rate: {results.effective_total_rate:.2f}%")
    
    print("\n" + "=" * 60)
    print("Module can be safely imported without executing test code.")
