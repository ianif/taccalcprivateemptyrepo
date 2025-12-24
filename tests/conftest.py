"""
Shared pytest fixtures and configuration for Greek Tax Calculator tests.

This module provides reusable fixtures for testing tax calculation functions,
including sample income values, expense values, and expected results for
regression testing.
"""

import pytest
from decimal import Decimal


# ============================================================================
# SAMPLE INCOME VALUE FIXTURES
# ============================================================================

@pytest.fixture
def income_low():
    """Low income test value: €5,000"""
    return Decimal('5000.00')


@pytest.fixture
def income_medium():
    """Medium income test value: €25,000"""
    return Decimal('25000.00')


@pytest.fixture
def income_high():
    """High income test value: €60,000"""
    return Decimal('60000.00')


@pytest.fixture
def income_boundary_10k():
    """Boundary value at first tax bracket limit: €10,000"""
    return Decimal('10000.00')


@pytest.fixture
def income_boundary_20k():
    """Boundary value at second tax bracket limit: €20,000"""
    return Decimal('20000.00')


@pytest.fixture
def income_boundary_30k():
    """Boundary value at third tax bracket limit: €30,000"""
    return Decimal('30000.00')


@pytest.fixture
def income_boundary_40k():
    """Boundary value at fourth tax bracket limit: €40,000"""
    return Decimal('40000.00')


# ============================================================================
# SAMPLE EXPENSE VALUE FIXTURES
# ============================================================================

@pytest.fixture
def expenses_zero():
    """No expenses"""
    return Decimal('0.00')


@pytest.fixture
def expenses_low():
    """Low expenses: €1,000"""
    return Decimal('1000.00')


@pytest.fixture
def expenses_medium():
    """Medium expenses: €5,000"""
    return Decimal('5000.00')


@pytest.fixture
def expenses_high():
    """High expenses: €10,000"""
    return Decimal('10000.00')


@pytest.fixture
def expenses_percentage_10(request):
    """
    Fixture that returns 10% of income as expenses.
    
    Usage: Use with indirect parametrization passing income value.
    Example: @pytest.mark.parametrize('expenses_percentage_10', [25000], indirect=True)
    """
    income = request.param
    return Decimal(str(income)) * Decimal('0.10')


@pytest.fixture
def expenses_percentage_20(request):
    """
    Fixture that returns 20% of income as expenses.
    
    Usage: Use with indirect parametrization passing income value.
    """
    income = request.param
    return Decimal(str(income)) * Decimal('0.20')


@pytest.fixture
def expenses_percentage_50(request):
    """
    Fixture that returns 50% of income as expenses.
    
    Usage: Use with indirect parametrization passing income value.
    """
    income = request.param
    return Decimal(str(income)) * Decimal('0.50')


# ============================================================================
# EXPECTED RESULTS FIXTURES (Regression Testing)
# ============================================================================

@pytest.fixture
def expected_results_low_income_no_expenses():
    """
    Expected tax calculation results for €5,000 income with no expenses.
    
    Calculations:
    - Taxable income: €5,000
    - Income tax (9% on €5,000): €450
    - EFKA (20% on €5,000): €1,000
    - VAT (24% on €5,000): €1,200
    - Total taxes: €1,450
    - Net income: €3,550
    """
    return {
        'gross_income': Decimal('5000.00'),
        'deductible_expenses': Decimal('0.00'),
        'taxable_income': Decimal('5000.00'),
        'income_tax_total': Decimal('450.00'),
        'efka_total': Decimal('1000.00'),
        'vat_amount': Decimal('1200.00'),
        'total_taxes': Decimal('1450.00'),
        'net_income': Decimal('3550.00')
    }


@pytest.fixture
def expected_results_medium_income_no_expenses():
    """
    Expected tax calculation results for €25,000 income with no expenses.
    
    Calculations:
    - Taxable income: €25,000
    - Income tax: €10,000 @ 9% + €10,000 @ 22% + €5,000 @ 28% = €900 + €2,200 + €1,400 = €4,500
    - EFKA (20% on €25,000): €5,000
    - VAT (24% on €25,000): €6,000
    - Total taxes: €9,500
    - Net income: €15,500
    """
    return {
        'gross_income': Decimal('25000.00'),
        'deductible_expenses': Decimal('0.00'),
        'taxable_income': Decimal('25000.00'),
        'income_tax_total': Decimal('4500.00'),
        'efka_total': Decimal('5000.00'),
        'vat_amount': Decimal('6000.00'),
        'total_taxes': Decimal('9500.00'),
        'net_income': Decimal('15500.00')
    }


@pytest.fixture
def expected_results_high_income_with_expenses():
    """
    Expected tax calculation results for €60,000 income with €10,000 expenses.
    
    Calculations:
    - Taxable income: €60,000 - €10,000 = €50,000
    - Income tax: €10k @ 9% + €10k @ 22% + €10k @ 28% + €10k @ 36% + €10k @ 44%
    -           = €900 + €2,200 + €2,800 + €3,600 + €4,400 = €13,900
    - EFKA (20% on €60,000 GROSS): €12,000
    - VAT (24% on €60,000 GROSS): €14,400
    - Total taxes: €25,900
    - Net income: €34,100
    """
    return {
        'gross_income': Decimal('60000.00'),
        'deductible_expenses': Decimal('10000.00'),
        'taxable_income': Decimal('50000.00'),
        'income_tax_total': Decimal('13900.00'),
        'efka_total': Decimal('12000.00'),
        'vat_amount': Decimal('14400.00'),
        'total_taxes': Decimal('25900.00'),
        'net_income': Decimal('34100.00')
    }


@pytest.fixture
def expected_results_boundary_10k():
    """
    Expected results for exact boundary at €10,000 (first bracket limit).
    
    Calculations:
    - Taxable income: €10,000
    - Income tax (9% on €10,000): €900
    - EFKA (20% on €10,000): €2,000
    - VAT (24% on €10,000): €2,400
    """
    return {
        'gross_income': Decimal('10000.00'),
        'deductible_expenses': Decimal('0.00'),
        'taxable_income': Decimal('10000.00'),
        'income_tax_total': Decimal('900.00'),
        'efka_total': Decimal('2000.00'),
        'vat_amount': Decimal('2400.00'),
        'total_taxes': Decimal('2900.00'),
        'net_income': Decimal('7100.00')
    }


@pytest.fixture
def expected_results_boundary_20k():
    """
    Expected results for exact boundary at €20,000 (second bracket limit).
    
    Calculations:
    - Taxable income: €20,000
    - Income tax: €10,000 @ 9% + €10,000 @ 22% = €900 + €2,200 = €3,100
    - EFKA (20% on €20,000): €4,000
    - VAT (24% on €20,000): €4,800
    """
    return {
        'gross_income': Decimal('20000.00'),
        'deductible_expenses': Decimal('0.00'),
        'taxable_income': Decimal('20000.00'),
        'income_tax_total': Decimal('3100.00'),
        'efka_total': Decimal('4000.00'),
        'vat_amount': Decimal('4800.00'),
        'total_taxes': Decimal('7100.00'),
        'net_income': Decimal('12900.00')
    }


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def zero_income():
    """Edge case: Zero income"""
    return Decimal('0.00')


@pytest.fixture
def negative_income():
    """Edge case: Negative income (should be handled gracefully)"""
    return Decimal('-1000.00')


@pytest.fixture
def very_large_income():
    """Edge case: Very large income to test highest tax bracket"""
    return Decimal('1000000.00')


@pytest.fixture
def expenses_exceed_income():
    """Edge case: Expenses greater than income"""
    return {
        'income': Decimal('5000.00'),
        'expenses': Decimal('10000.00')
    }


# ============================================================================
# MOCK FIXTURES FOR FILE OPERATIONS
# ============================================================================

@pytest.fixture
def sample_calculation_result():
    """
    Sample calculation result for testing file operations.
    
    Returns a complete tax calculation result dictionary that can be used
    to test save_results_to_file() and other output functions.
    """
    return {
        'gross_income': Decimal('50000.00'),
        'deductible_expenses': Decimal('5000.00'),
        'taxable_income': Decimal('45000.00'),
        'income_tax': {
            'total_tax': Decimal('12100.00'),
            'effective_rate': Decimal('26.89'),
            'bracket_breakdown': [
                {
                    'bracket_min': Decimal('0'),
                    'bracket_max': Decimal('10000'),
                    'rate': Decimal('9'),
                    'taxable_amount': Decimal('10000'),
                    'tax_amount': Decimal('900')
                },
                {
                    'bracket_min': Decimal('10000'),
                    'bracket_max': Decimal('20000'),
                    'rate': Decimal('22'),
                    'taxable_amount': Decimal('10000'),
                    'tax_amount': Decimal('2200')
                },
                {
                    'bracket_min': Decimal('20000'),
                    'bracket_max': Decimal('30000'),
                    'rate': Decimal('28'),
                    'taxable_amount': Decimal('10000'),
                    'tax_amount': Decimal('2800')
                },
                {
                    'bracket_min': Decimal('30000'),
                    'bracket_max': Decimal('40000'),
                    'rate': Decimal('36'),
                    'taxable_amount': Decimal('10000'),
                    'tax_amount': Decimal('3600')
                },
                {
                    'bracket_min': Decimal('40000'),
                    'bracket_max': 'unlimited',
                    'rate': Decimal('44'),
                    'taxable_amount': Decimal('5000'),
                    'tax_amount': Decimal('2200')
                }
            ]
        },
        'vat': {
            'vat_rate': Decimal('0.24'),
            'vat_amount': Decimal('12000.00')
        },
        'social_security': {
            'total_contribution': Decimal('10000.00'),
            'contribution_rate': Decimal('0.20'),
            'main_insurance': Decimal('6665.00'),
            'main_insurance_rate': Decimal('0.1333'),
            'additional_contributions': Decimal('3335.00'),
            'additional_contributions_rate': Decimal('0.0667')
        },
        'total_taxes': Decimal('22100.00'),
        'net_income': Decimal('27900.00'),
        'effective_total_rate': Decimal('44.20')
    }
