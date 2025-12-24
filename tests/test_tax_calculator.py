"""
Unit tests for tax_calculator.py

This module contains unit tests for the core tax calculation functions
in the Greek Tax Calculator. Tests are organized by function and include
edge cases, boundary values, and regression tests.

To run only these tests:
    pytest tests/test_tax_calculator.py -v

To run with coverage:
    pytest tests/test_tax_calculator.py --cov=tax_calculator --cov-report=term
"""

import pytest
from decimal import Decimal
from tax_calculator import (
    calculate_taxable_income,
    calculate_income_tax,
    calculate_vat,
    calculate_social_security,
    calculate_all_taxes,
    calculate_payment_schedule,
    INCOME_TAX_BRACKETS,
    VAT_RATE,
    EFKA_TOTAL_RATE,
    LAST_UPDATED,
    TAX_YEAR
)


# ============================================================================
# SMOKE TESTS - Basic functionality verification
# ============================================================================

@pytest.mark.unit
class TestSmokeTests:
    """Smoke tests to verify basic functionality of the tax calculator."""
    
    def test_module_imports(self):
        """Verify that all expected functions can be imported."""
        assert callable(calculate_taxable_income)
        assert callable(calculate_income_tax)
        assert callable(calculate_vat)
        assert callable(calculate_social_security)
        assert callable(calculate_all_taxes)
        assert callable(calculate_payment_schedule)
    
    def test_constants_exist(self):
        """Verify that required constants are defined."""
        assert INCOME_TAX_BRACKETS is not None
        assert len(INCOME_TAX_BRACKETS) == 5
        assert VAT_RATE == Decimal('0.24')
        assert EFKA_TOTAL_RATE == Decimal('0.20')
        assert LAST_UPDATED is not None
        assert TAX_YEAR == 2024
    
    def test_basic_calculation_returns_dict(self):
        """Verify that calculate_all_taxes returns a dictionary with expected keys."""
        result = calculate_all_taxes(10000, 0)
        assert isinstance(result, dict)
        assert 'gross_income' in result
        assert 'taxable_income' in result
        assert 'income_tax' in result
        assert 'vat' in result
        assert 'social_security' in result
        assert 'total_taxes' in result
        assert 'net_income' in result
    
    def test_basic_calculation_returns_decimals(self):
        """Verify that calculations return Decimal types for precision."""
        result = calculate_all_taxes(10000, 0)
        assert isinstance(result['gross_income'], Decimal)
        assert isinstance(result['taxable_income'], Decimal)
        assert isinstance(result['total_taxes'], Decimal)
        assert isinstance(result['net_income'], Decimal)
    
    def test_simple_income_tax_calculation(self):
        """Smoke test: Simple income tax calculation for €10,000."""
        result = calculate_income_tax(10000)
        assert isinstance(result, dict)
        assert 'total_tax' in result
        assert result['total_tax'] == Decimal('900.00')  # 9% of €10,000
    
    def test_simple_vat_calculation(self):
        """Smoke test: Simple VAT calculation."""
        result = calculate_vat(10000)
        assert isinstance(result, dict)
        assert 'vat_amount' in result
        assert result['vat_amount'] == Decimal('2400.00')  # 24% of €10,000
    
    def test_simple_efka_calculation(self):
        """Smoke test: Simple EFKA calculation."""
        result = calculate_social_security(10000)
        assert isinstance(result, dict)
        assert 'total_contribution' in result
        assert result['total_contribution'] == Decimal('2000.00')  # 20% of €10,000
    
    def test_payment_schedule_calculation(self):
        """Smoke test: Payment schedule calculation."""
        result = calculate_payment_schedule(12000, 'monthly')
        assert isinstance(result, dict)
        assert 'payment_amount' in result
        assert result['number_of_payments'] == 12
        assert result['payment_amount'] == Decimal('1000.00')


# ============================================================================
# PLACEHOLDER FOR DETAILED UNIT TESTS (Task #18)
# ============================================================================

@pytest.mark.unit
class TestTaxableIncome:
    """Unit tests for calculate_taxable_income function."""
    
    def test_normal_income_no_expenses(self):
        """Test standard case with income and no expenses."""
        result = calculate_taxable_income(50000, 0)
        assert result == Decimal('50000.00')
        assert isinstance(result, Decimal)
    
    def test_normal_income_with_expenses(self):
        """Test standard case with income and expenses."""
        result = calculate_taxable_income(50000, 10000)
        assert result == Decimal('40000.00')
    
    def test_expenses_equal_income(self):
        """Test edge case where expenses exactly equal income."""
        result = calculate_taxable_income(25000, 25000)
        assert result == Decimal('0.00')
    
    def test_expenses_exceed_income(self):
        """Test edge case where expenses exceed income (should return 0)."""
        result = calculate_taxable_income(10000, 15000)
        assert result == Decimal('0.00')
    
    def test_zero_income(self):
        """Test edge case with zero income."""
        result = calculate_taxable_income(0, 0)
        assert result == Decimal('0.00')
    
    def test_zero_income_with_expenses(self):
        """Test edge case with zero income but expenses present."""
        result = calculate_taxable_income(0, 5000)
        assert result == Decimal('0.00')
    
    def test_float_input_conversion(self):
        """Test that float inputs are properly converted to Decimal."""
        result = calculate_taxable_income(35000.50, 5000.25)
        assert result == Decimal('30000.25')
        assert isinstance(result, Decimal)
    
    def test_decimal_input_handling(self):
        """Test that Decimal inputs are handled correctly."""
        result = calculate_taxable_income(Decimal('60000'), Decimal('10000'))
        assert result == Decimal('60000.00') - Decimal('10000.00')
    
    def test_decimal_precision_rounding(self):
        """Test that results are rounded to 2 decimal places."""
        # Input with more than 2 decimal places
        result = calculate_taxable_income(Decimal('12345.678'), Decimal('2345.123'))
        assert result == Decimal('10000.56')  # Rounded with ROUND_HALF_UP
    
    def test_realistic_scenario_from_sample(self):
        """Test realistic scenario from sample_calculations.txt (Example 4)."""
        # €12,000 income with €9,000 expenses = €3,000 taxable
        result = calculate_taxable_income(12000, 9000)
        assert result == Decimal('3000.00')


@pytest.mark.unit
class TestIncomeTax:
    """Unit tests for calculate_income_tax function."""
    
    def test_zero_income(self):
        """Test income tax calculation for zero taxable income."""
        result = calculate_income_tax(0)
        assert result['total_tax'] == Decimal('0.00')
        assert result['effective_rate'] == Decimal('0.00')
        assert result['bracket_breakdown'] == []
    
    def test_negative_income(self):
        """Test that negative income is handled gracefully."""
        result = calculate_income_tax(-1000)
        assert result['total_tax'] == Decimal('0.00')
        assert result['effective_rate'] == Decimal('0.00')
        assert result['bracket_breakdown'] == []
    
    def test_first_bracket_only(self):
        """Test income entirely within first bracket (€0-€10,000 @ 9%)."""
        result = calculate_income_tax(5000)
        assert result['total_tax'] == Decimal('450.00')  # 5000 * 0.09
        assert result['effective_rate'] == Decimal('9.00')
        assert len(result['bracket_breakdown']) == 1
        assert result['bracket_breakdown'][0]['taxable_amount'] == Decimal('5000.00')
        assert result['bracket_breakdown'][0]['tax_amount'] == Decimal('450.00')
        assert result['bracket_breakdown'][0]['rate'] == Decimal('9.00')
    
    def test_boundary_10000(self):
        """Test exact boundary at €10,000 (end of first bracket)."""
        result = calculate_income_tax(10000)
        assert result['total_tax'] == Decimal('900.00')  # 10000 * 0.09
        assert result['effective_rate'] == Decimal('9.00')
        assert len(result['bracket_breakdown']) == 1
    
    def test_boundary_10001(self):
        """Test €10,001 (first euro in second bracket)."""
        result = calculate_income_tax(10001)
        # First bracket: 10000 * 0.09 = 900
        # Second bracket: 1 * 0.22 = 0.22
        expected_tax = Decimal('900.00') + Decimal('0.22')
        assert result['total_tax'] == Decimal('900.22')
        assert len(result['bracket_breakdown']) == 2
    
    def test_boundary_20000(self):
        """Test exact boundary at €20,000 (end of second bracket)."""
        result = calculate_income_tax(20000)
        # First: 10000 * 0.09 = 900
        # Second: 10000 * 0.22 = 2200
        # Total: 3100
        assert result['total_tax'] == Decimal('3100.00')
        assert result['effective_rate'] == Decimal('15.50')  # 3100/20000 * 100
        assert len(result['bracket_breakdown']) == 2
    
    def test_boundary_30000(self):
        """Test exact boundary at €30,000 (end of third bracket)."""
        result = calculate_income_tax(30000)
        # First: 10000 * 0.09 = 900
        # Second: 10000 * 0.22 = 2200
        # Third: 10000 * 0.28 = 2800
        # Total: 5900
        assert result['total_tax'] == Decimal('5900.00')
        assert result['effective_rate'] == Decimal('19.67')
        assert len(result['bracket_breakdown']) == 3
    
    def test_boundary_40000(self):
        """Test exact boundary at €40,000 (end of fourth bracket)."""
        result = calculate_income_tax(40000)
        # First: 10000 * 0.09 = 900
        # Second: 10000 * 0.22 = 2200
        # Third: 10000 * 0.28 = 2800
        # Fourth: 10000 * 0.36 = 3600
        # Total: 9500
        assert result['total_tax'] == Decimal('9500.00')
        assert result['effective_rate'] == Decimal('23.75')
        assert len(result['bracket_breakdown']) == 4
    
    def test_fifth_bracket(self):
        """Test income in fifth bracket (over €40,000 @ 44%)."""
        result = calculate_income_tax(50000)
        # First: 10000 * 0.09 = 900
        # Second: 10000 * 0.22 = 2200
        # Third: 10000 * 0.28 = 2800
        # Fourth: 10000 * 0.36 = 3600
        # Fifth: 10000 * 0.44 = 4400
        # Total: 13900
        assert result['total_tax'] == Decimal('13900.00')
        assert result['effective_rate'] == Decimal('27.80')
        assert len(result['bracket_breakdown']) == 5
    
    def test_very_high_income(self):
        """Test very high income to ensure fifth bracket calculation."""
        result = calculate_income_tax(100000)
        # First four brackets: 9500
        # Fifth: 60000 * 0.44 = 26400
        # Total: 35900
        assert result['total_tax'] == Decimal('35900.00')
        assert len(result['bracket_breakdown']) == 5
        assert result['bracket_breakdown'][4]['taxable_amount'] == Decimal('60000.00')
    
    def test_progressive_taxation_15000(self):
        """Test progressive taxation for €15,000 (crosses 2 brackets)."""
        result = calculate_income_tax(15000)
        # First: 10000 * 0.09 = 900
        # Second: 5000 * 0.22 = 1100
        # Total: 2000
        assert result['total_tax'] == Decimal('2000.00')
        assert len(result['bracket_breakdown']) == 2
    
    def test_progressive_taxation_25000(self):
        """Test progressive taxation for €25,000 (crosses 3 brackets)."""
        result = calculate_income_tax(25000)
        # First: 10000 * 0.09 = 900
        # Second: 10000 * 0.22 = 2200
        # Third: 5000 * 0.28 = 1400
        # Total: 4500
        assert result['total_tax'] == Decimal('4500.00')
        assert len(result['bracket_breakdown']) == 3
    
    def test_bracket_breakdown_structure(self):
        """Test that bracket breakdown has correct structure."""
        result = calculate_income_tax(15000)
        breakdown = result['bracket_breakdown']
        
        assert len(breakdown) == 2
        
        # First bracket
        assert 'bracket_min' in breakdown[0]
        assert 'bracket_max' in breakdown[0]
        assert 'rate' in breakdown[0]
        assert 'taxable_amount' in breakdown[0]
        assert 'tax_amount' in breakdown[0]
        
        assert breakdown[0]['bracket_min'] == Decimal('0.00')
        assert breakdown[0]['bracket_max'] == Decimal('10000.00')
        assert breakdown[0]['rate'] == Decimal('9.00')
        
        # Second bracket
        assert breakdown[1]['bracket_min'] == Decimal('10000.00')
        assert breakdown[1]['bracket_max'] == Decimal('20000.00')
        assert breakdown[1]['rate'] == Decimal('22.00')
    
    def test_decimal_precision(self):
        """Test that all returned values are rounded to 2 decimal places."""
        result = calculate_income_tax(12345.678)
        assert str(result['total_tax']).count('.') <= 1
        assert len(str(result['total_tax']).split('.')[-1]) <= 2
        assert isinstance(result['total_tax'], Decimal)
        assert isinstance(result['effective_rate'], Decimal)
    
    def test_float_input_conversion(self):
        """Test that float input is properly converted to Decimal."""
        result = calculate_income_tax(15000.0)
        assert result['total_tax'] == Decimal('2000.00')
        assert isinstance(result['total_tax'], Decimal)
    
    def test_sample_calculation_example1(self):
        """Test Example 1 from sample_calculations.txt: €15,000 income."""
        result = calculate_income_tax(15000)
        assert result['total_tax'] == Decimal('2000.00')
    
    def test_sample_calculation_example2(self):
        """Test Example 2 from sample_calculations.txt: €30,000 taxable income."""
        result = calculate_income_tax(30000)
        assert result['total_tax'] == Decimal('5900.00')
    
    def test_sample_calculation_example3(self):
        """Test Example 3 from sample_calculations.txt: €50,000 taxable income."""
        result = calculate_income_tax(50000)
        assert result['total_tax'] == Decimal('13900.00')
    
    def test_sample_calculation_example4(self):
        """Test Example 4 from sample_calculations.txt: €3,000 taxable income."""
        result = calculate_income_tax(3000)
        assert result['total_tax'] == Decimal('270.00')


@pytest.mark.unit
class TestVAT:
    """Unit tests for calculate_vat function."""
    
    def test_basic_vat_calculation(self):
        """Test basic VAT calculation at 24%."""
        result = calculate_vat(10000)
        assert result['vat_amount'] == Decimal('2400.00')  # 10000 * 0.24
        assert result['rate'] == Decimal('24.00')
        assert result['total_with_vat'] == Decimal('12400.00')
    
    def test_zero_income(self):
        """Test VAT calculation for zero income."""
        result = calculate_vat(0)
        assert result['vat_amount'] == Decimal('0.00')
        assert result['rate'] == Decimal('24.00')
        assert result['total_with_vat'] == Decimal('0.00')
    
    def test_various_income_levels(self):
        """Test VAT calculation for various income levels."""
        # Low income
        result = calculate_vat(5000)
        assert result['vat_amount'] == Decimal('1200.00')
        assert result['total_with_vat'] == Decimal('6200.00')
        
        # Medium income
        result = calculate_vat(25000)
        assert result['vat_amount'] == Decimal('6000.00')
        assert result['total_with_vat'] == Decimal('31000.00')
        
        # High income
        result = calculate_vat(60000)
        assert result['vat_amount'] == Decimal('14400.00')
        assert result['total_with_vat'] == Decimal('74400.00')
    
    def test_24_percent_rate_verification(self):
        """Verify that VAT rate is exactly 24%."""
        result = calculate_vat(100)
        assert result['vat_amount'] == Decimal('24.00')
        assert result['rate'] == Decimal('24.00')
    
    def test_decimal_input(self):
        """Test that Decimal inputs are handled correctly."""
        result = calculate_vat(Decimal('15000'))
        assert result['vat_amount'] == Decimal('3600.00')
        assert isinstance(result['vat_amount'], Decimal)
    
    def test_float_input_conversion(self):
        """Test that float inputs are properly converted to Decimal."""
        result = calculate_vat(15000.0)
        assert result['vat_amount'] == Decimal('3600.00')
        assert isinstance(result['vat_amount'], Decimal)
    
    def test_decimal_precision(self):
        """Test that results are rounded to 2 decimal places."""
        result = calculate_vat(Decimal('12345.678'))
        # 12345.678 * 0.24 = 2962.96272, rounded to 2962.96
        assert result['vat_amount'] == Decimal('2962.96')
        assert isinstance(result['vat_amount'], Decimal)
    
    def test_return_structure(self):
        """Test that return dictionary has correct structure and keys."""
        result = calculate_vat(10000)
        
        assert isinstance(result, dict)
        assert 'vat_amount' in result
        assert 'rate' in result
        assert 'total_with_vat' in result
        
        assert isinstance(result['vat_amount'], Decimal)
        assert isinstance(result['rate'], Decimal)
        assert isinstance(result['total_with_vat'], Decimal)
    
    def test_sample_calculation_example1(self):
        """Test Example 1 from sample_calculations.txt: €15,000 income."""
        result = calculate_vat(15000)
        assert result['vat_amount'] == Decimal('3600.00')
    
    def test_sample_calculation_example2(self):
        """Test Example 2 from sample_calculations.txt: €35,000 income."""
        result = calculate_vat(35000)
        assert result['vat_amount'] == Decimal('8400.00')
    
    def test_sample_calculation_example3(self):
        """Test Example 3 from sample_calculations.txt: €60,000 income."""
        result = calculate_vat(60000)
        assert result['vat_amount'] == Decimal('14400.00')
    
    def test_sample_calculation_example4(self):
        """Test Example 4 from sample_calculations.txt: €12,000 income."""
        result = calculate_vat(12000)
        assert result['vat_amount'] == Decimal('2880.00')


@pytest.mark.unit
class TestSocialSecurity:
    """Unit tests for calculate_social_security function."""
    
    def test_basic_efka_calculation(self):
        """Test basic EFKA calculation at 20%."""
        result = calculate_social_security(10000)
        assert result['total_contribution'] == Decimal('2000.00')  # 10000 * 0.20
        assert result['rate'] == Decimal('20.00')
    
    def test_main_insurance_rate(self):
        """Test main insurance contribution at 13.33%."""
        result = calculate_social_security(10000)
        assert result['main_insurance'] == Decimal('1333.00')  # 10000 * 0.1333
    
    def test_additional_contributions_rate(self):
        """Test additional contributions at 6.67%."""
        result = calculate_social_security(10000)
        assert result['additional_contributions'] == Decimal('667.00')  # 10000 * 0.0667
    
    def test_total_equals_sum_of_parts(self):
        """Test that total contribution equals main + additional."""
        result = calculate_social_security(15000)
        total = result['main_insurance'] + result['additional_contributions']
        # Allow for minor rounding differences
        assert abs(result['total_contribution'] - total) <= Decimal('0.01')
    
    def test_zero_income(self):
        """Test EFKA calculation for zero income."""
        result = calculate_social_security(0)
        assert result['total_contribution'] == Decimal('0.00')
        assert result['main_insurance'] == Decimal('0.00')
        assert result['additional_contributions'] == Decimal('0.00')
        assert result['rate'] == Decimal('20.00')
    
    def test_various_income_levels(self):
        """Test EFKA calculation for various income levels."""
        # Low income
        result = calculate_social_security(5000)
        assert result['total_contribution'] == Decimal('1000.00')
        
        # Medium income
        result = calculate_social_security(25000)
        assert result['total_contribution'] == Decimal('5000.00')
        
        # High income
        result = calculate_social_security(60000)
        assert result['total_contribution'] == Decimal('12000.00')
    
    def test_20_percent_rate_verification(self):
        """Verify that total EFKA rate is exactly 20%."""
        result = calculate_social_security(10000)
        assert result['total_contribution'] == Decimal('2000.00')
        assert result['rate'] == Decimal('20.00')
    
    def test_decimal_input(self):
        """Test that Decimal inputs are handled correctly."""
        result = calculate_social_security(Decimal('15000'))
        assert result['total_contribution'] == Decimal('3000.00')
        assert isinstance(result['total_contribution'], Decimal)
    
    def test_float_input_conversion(self):
        """Test that float inputs are properly converted to Decimal."""
        result = calculate_social_security(15000.0)
        assert result['total_contribution'] == Decimal('3000.00')
        assert isinstance(result['total_contribution'], Decimal)
    
    def test_decimal_precision(self):
        """Test that results are rounded to 2 decimal places."""
        result = calculate_social_security(Decimal('12345.678'))
        # Total should be rounded to 2 decimal places
        assert isinstance(result['total_contribution'], Decimal)
        assert len(str(result['total_contribution']).split('.')[-1]) <= 2
    
    def test_return_structure(self):
        """Test that return dictionary has correct structure and keys."""
        result = calculate_social_security(10000)
        
        assert isinstance(result, dict)
        assert 'total_contribution' in result
        assert 'main_insurance' in result
        assert 'additional_contributions' in result
        assert 'rate' in result
        
        assert isinstance(result['total_contribution'], Decimal)
        assert isinstance(result['main_insurance'], Decimal)
        assert isinstance(result['additional_contributions'], Decimal)
        assert isinstance(result['rate'], Decimal)
    
    def test_sample_calculation_example1(self):
        """Test Example 1 from sample_calculations.txt: €15,000 income."""
        result = calculate_social_security(15000)
        assert result['total_contribution'] == Decimal('3000.00')
    
    def test_sample_calculation_example2(self):
        """Test Example 2 from sample_calculations.txt: €35,000 income."""
        result = calculate_social_security(35000)
        assert result['total_contribution'] == Decimal('7000.00')
    
    def test_sample_calculation_example3(self):
        """Test Example 3 from sample_calculations.txt: €60,000 income."""
        result = calculate_social_security(60000)
        assert result['total_contribution'] == Decimal('12000.00')
    
    def test_sample_calculation_example4(self):
        """Test Example 4 from sample_calculations.txt: €12,000 income."""
        result = calculate_social_security(12000)
        assert result['total_contribution'] == Decimal('2400.00')
    
    def test_efka_calculated_on_gross_not_taxable(self):
        """Test that EFKA is calculated on gross income (important distinction)."""
        # This is a documentation test to emphasize the important point
        # that EFKA is on GROSS income, not taxable income
        gross = 12000
        result = calculate_social_security(gross)
        # EFKA should be 20% of 12000, regardless of any expenses
        assert result['total_contribution'] == Decimal('2400.00')


@pytest.mark.unit
class TestAllTaxes:
    """Unit tests for calculate_all_taxes function."""
    
    def test_basic_integration(self):
        """Test basic integration of all tax components."""
        result = calculate_all_taxes(15000, 0)
        
        # Verify all major keys exist
        assert 'gross_income' in result
        assert 'deductible_expenses' in result
        assert 'taxable_income' in result
        assert 'income_tax' in result
        assert 'vat' in result
        assert 'social_security' in result
        assert 'total_taxes' in result
        assert 'total_obligations' in result
        assert 'net_income' in result
        assert 'effective_total_rate' in result
    
    def test_return_types(self):
        """Test that all returned values are proper Decimal types."""
        result = calculate_all_taxes(15000, 0)
        
        assert isinstance(result['gross_income'], Decimal)
        assert isinstance(result['deductible_expenses'], Decimal)
        assert isinstance(result['taxable_income'], Decimal)
        assert isinstance(result['total_taxes'], Decimal)
        assert isinstance(result['net_income'], Decimal)
        assert isinstance(result['effective_total_rate'], Decimal)
    
    def test_nested_structure(self):
        """Test that nested dictionaries (income_tax, vat, social_security) are present."""
        result = calculate_all_taxes(15000, 0)
        
        # income_tax should be a dict with specific keys
        assert isinstance(result['income_tax'], dict)
        assert 'total_tax' in result['income_tax']
        assert 'effective_rate' in result['income_tax']
        assert 'bracket_breakdown' in result['income_tax']
        
        # vat should be a dict
        assert isinstance(result['vat'], dict)
        assert 'vat_amount' in result['vat']
        
        # social_security should be a dict
        assert isinstance(result['social_security'], dict)
        assert 'total_contribution' in result['social_security']
    
    def test_zero_income(self):
        """Test handling of zero income."""
        result = calculate_all_taxes(0, 0)
        
        assert result['gross_income'] == Decimal('0.00')
        assert result['taxable_income'] == Decimal('0.00')
        assert result['total_taxes'] == Decimal('0.00')
        assert result['net_income'] == Decimal('0.00')
        assert result['effective_total_rate'] == Decimal('0.00')
    
    def test_negative_income(self):
        """Test handling of negative income."""
        result = calculate_all_taxes(-1000, 0)
        
        # Should handle gracefully and return zeros
        assert result['total_taxes'] == Decimal('0.00')
        assert result['net_income'] == Decimal('0.00')
    
    def test_expenses_exceed_income(self):
        """Test when expenses exceed income."""
        result = calculate_all_taxes(10000, 15000)
        
        # Taxable income should be 0
        assert result['taxable_income'] == Decimal('0.00')
        # Income tax should be 0
        assert result['income_tax']['total_tax'] == Decimal('0.00')
        # But EFKA is still on gross income!
        assert result['social_security']['total_contribution'] == Decimal('2000.00')
    
    def test_total_taxes_calculation(self):
        """Test that total_taxes equals income_tax + social_security."""
        result = calculate_all_taxes(15000, 0)
        
        income_tax = result['income_tax']['total_tax']
        efka = result['social_security']['total_contribution']
        total = income_tax + efka
        
        assert result['total_taxes'] == total
    
    def test_total_obligations_includes_vat(self):
        """Test that total_obligations includes VAT."""
        result = calculate_all_taxes(15000, 0)
        
        total_taxes = result['total_taxes']
        vat = result['vat']['vat_amount']
        total_obligations = total_taxes + vat
        
        assert result['total_obligations'] == total_obligations
    
    def test_net_income_calculation(self):
        """Test that net_income = gross_income - total_taxes."""
        result = calculate_all_taxes(15000, 0)
        
        net = result['gross_income'] - result['total_taxes']
        assert result['net_income'] == net
    
    def test_effective_rate_calculation(self):
        """Test effective total rate calculation."""
        result = calculate_all_taxes(15000, 0)
        
        # Effective rate should be (total_taxes / gross_income) * 100
        expected_rate = (result['total_taxes'] / result['gross_income'] * 100).quantize(
            Decimal('0.01')
        )
        assert result['effective_total_rate'] == expected_rate
    
    def test_sample_example1_no_expenses(self):
        """Test Example 1 from sample_calculations.txt: €15,000 income, no expenses."""
        result = calculate_all_taxes(15000, 0)
        
        assert result['gross_income'] == Decimal('15000.00')
        assert result['taxable_income'] == Decimal('15000.00')
        assert result['income_tax']['total_tax'] == Decimal('2000.00')
        assert result['social_security']['total_contribution'] == Decimal('3000.00')
        assert result['vat']['vat_amount'] == Decimal('3600.00')
        assert result['total_taxes'] == Decimal('5000.00')
        assert result['net_income'] == Decimal('10000.00')
        assert result['effective_total_rate'] == Decimal('33.33')
    
    def test_sample_example2_with_expenses(self):
        """Test Example 2 from sample_calculations.txt: €35,000 income, €5,000 expenses."""
        result = calculate_all_taxes(35000, 5000)
        
        assert result['gross_income'] == Decimal('35000.00')
        assert result['deductible_expenses'] == Decimal('5000.00')
        assert result['taxable_income'] == Decimal('30000.00')
        assert result['income_tax']['total_tax'] == Decimal('5900.00')
        assert result['social_security']['total_contribution'] == Decimal('7000.00')
        assert result['vat']['vat_amount'] == Decimal('8400.00')
        assert result['total_taxes'] == Decimal('12900.00')
        assert result['net_income'] == Decimal('22100.00')
    
    def test_sample_example3_high_income(self):
        """Test Example 3 from sample_calculations.txt: €60,000 income, €10,000 expenses."""
        result = calculate_all_taxes(60000, 10000)
        
        assert result['gross_income'] == Decimal('60000.00')
        assert result['deductible_expenses'] == Decimal('10000.00')
        assert result['taxable_income'] == Decimal('50000.00')
        assert result['income_tax']['total_tax'] == Decimal('13900.00')
        assert result['social_security']['total_contribution'] == Decimal('12000.00')
        assert result['vat']['vat_amount'] == Decimal('14400.00')
        assert result['total_taxes'] == Decimal('25900.00')
        assert result['net_income'] == Decimal('34100.00')
    
    def test_sample_example4_high_expense_ratio(self):
        """Test Example 4 from sample_calculations.txt: €12,000 income, €9,000 expenses."""
        result = calculate_all_taxes(12000, 9000)
        
        assert result['gross_income'] == Decimal('12000.00')
        assert result['deductible_expenses'] == Decimal('9000.00')
        assert result['taxable_income'] == Decimal('3000.00')
        assert result['income_tax']['total_tax'] == Decimal('270.00')
        assert result['social_security']['total_contribution'] == Decimal('2400.00')
        assert result['vat']['vat_amount'] == Decimal('2880.00')
        assert result['total_taxes'] == Decimal('2670.00')
        assert result['net_income'] == Decimal('9330.00')
    
    def test_float_inputs(self):
        """Test that float inputs are properly converted."""
        result = calculate_all_taxes(15000.0, 0.0)
        
        assert isinstance(result['gross_income'], Decimal)
        assert result['gross_income'] == Decimal('15000.00')
    
    def test_decimal_inputs(self):
        """Test that Decimal inputs are handled correctly."""
        result = calculate_all_taxes(Decimal('15000'), Decimal('0'))
        
        assert result['gross_income'] == Decimal('15000.00')
        assert result['total_taxes'] == Decimal('5000.00')
    
    def test_realistic_freelancer_scenario(self):
        """Test realistic freelancer scenario with moderate income and expenses."""
        result = calculate_all_taxes(45000, 8000)
        
        # Taxable income: 45000 - 8000 = 37000
        assert result['taxable_income'] == Decimal('37000.00')
        
        # Income tax on 37000:
        # 10k @ 9% = 900, 10k @ 22% = 2200, 10k @ 28% = 2800, 7k @ 36% = 2520
        # Total: 8420
        assert result['income_tax']['total_tax'] == Decimal('8420.00')
        
        # EFKA on gross 45000: 9000
        assert result['social_security']['total_contribution'] == Decimal('9000.00')
        
        # Total taxes: 8420 + 9000 = 17420
        assert result['total_taxes'] == Decimal('17420.00')
        
        # Net: 45000 - 17420 = 27580
        assert result['net_income'] == Decimal('27580.00')
    
    def test_all_values_two_decimal_places(self):
        """Test that all monetary values are rounded to 2 decimal places."""
        result = calculate_all_taxes(12345.678, 2345.123)
        
        # Check main values
        for key in ['gross_income', 'deductible_expenses', 'taxable_income', 
                    'total_taxes', 'net_income', 'effective_total_rate']:
            value = str(result[key])
            if '.' in value:
                assert len(value.split('.')[-1]) <= 2, f"{key} has more than 2 decimal places"


@pytest.mark.unit
class TestPaymentSchedule:
    """Unit tests for calculate_payment_schedule function."""
    
    def test_monthly_schedule(self):
        """Test monthly payment schedule calculation."""
        result = calculate_payment_schedule(12000, 'monthly')
        
        assert result['annual_total'] == Decimal('12000.00')
        assert result['frequency'] == 'monthly'
        assert result['number_of_payments'] == 12
        assert result['payment_amount'] == Decimal('1000.00')
        assert len(result['schedule']) == 12
    
    def test_quarterly_schedule(self):
        """Test quarterly payment schedule calculation."""
        result = calculate_payment_schedule(12000, 'quarterly')
        
        assert result['annual_total'] == Decimal('12000.00')
        assert result['frequency'] == 'quarterly'
        assert result['number_of_payments'] == 4
        assert result['payment_amount'] == Decimal('3000.00')
        assert len(result['schedule']) == 4
    
    def test_annual_schedule(self):
        """Test annual payment schedule calculation."""
        result = calculate_payment_schedule(12000, 'annual')
        
        assert result['annual_total'] == Decimal('12000.00')
        assert result['frequency'] == 'annual'
        assert result['number_of_payments'] == 1
        assert result['payment_amount'] == Decimal('12000.00')
        assert len(result['schedule']) == 1
    
    def test_schedule_structure(self):
        """Test that schedule list has correct structure."""
        result = calculate_payment_schedule(12000, 'monthly')
        
        assert isinstance(result['schedule'], list)
        assert len(result['schedule']) == 12
        
        # Check first payment
        first_payment = result['schedule'][0]
        assert 'period_number' in first_payment
        assert 'payment_amount' in first_payment
        assert first_payment['period_number'] == 1
        assert isinstance(first_payment['payment_amount'], Decimal)
    
    def test_schedule_period_numbers(self):
        """Test that schedule period numbers are sequential."""
        result = calculate_payment_schedule(12000, 'quarterly')
        
        for i, payment in enumerate(result['schedule']):
            assert payment['period_number'] == i + 1
    
    def test_case_insensitive_frequency(self):
        """Test that frequency parameter is case-insensitive."""
        result1 = calculate_payment_schedule(12000, 'MONTHLY')
        result2 = calculate_payment_schedule(12000, 'Monthly')
        result3 = calculate_payment_schedule(12000, 'monthly')
        
        assert result1['frequency'] == 'monthly'
        assert result2['frequency'] == 'monthly'
        assert result3['frequency'] == 'monthly'
    
    def test_invalid_frequency_raises_error(self):
        """Test that invalid frequency raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            calculate_payment_schedule(12000, 'weekly')
        
        assert 'Invalid frequency' in str(exc_info.value)
    
    def test_rounding_in_payment_amount(self):
        """Test proper rounding when payment doesn't divide evenly."""
        result = calculate_payment_schedule(2670, 'monthly')
        
        # 2670 / 12 = 222.5
        assert result['payment_amount'] == Decimal('222.50')
        assert len(result['schedule']) == 12
        
        # Each payment should be the same
        for payment in result['schedule']:
            assert payment['payment_amount'] == Decimal('222.50')
    
    def test_rounding_complex_division(self):
        """Test rounding for complex division (e.g., 25900 / 12)."""
        result = calculate_payment_schedule(25900, 'monthly')
        
        # 25900 / 12 = 2158.333...
        assert result['payment_amount'] == Decimal('2158.33')
    
    def test_zero_tax(self):
        """Test payment schedule for zero tax."""
        result = calculate_payment_schedule(0, 'monthly')
        
        assert result['annual_total'] == Decimal('0.00')
        assert result['payment_amount'] == Decimal('0.00')
        assert len(result['schedule']) == 12
        
        for payment in result['schedule']:
            assert payment['payment_amount'] == Decimal('0.00')
    
    def test_decimal_input(self):
        """Test that Decimal inputs are handled correctly."""
        result = calculate_payment_schedule(Decimal('12000'), 'monthly')
        
        assert result['payment_amount'] == Decimal('1000.00')
        assert isinstance(result['annual_total'], Decimal)
    
    def test_float_input_conversion(self):
        """Test that float inputs are properly converted to Decimal."""
        result = calculate_payment_schedule(12000.0, 'monthly')
        
        assert result['payment_amount'] == Decimal('1000.00')
        assert isinstance(result['annual_total'], Decimal)
    
    def test_sample_example1_monthly(self):
        """Test monthly schedule for Example 1: €5,000 total tax."""
        result = calculate_payment_schedule(5000, 'monthly')
        
        assert result['payment_amount'] == Decimal('416.67')
        assert result['number_of_payments'] == 12
    
    def test_sample_example1_quarterly(self):
        """Test quarterly schedule for Example 1: €5,000 total tax."""
        result = calculate_payment_schedule(5000, 'quarterly')
        
        assert result['payment_amount'] == Decimal('1250.00')
        assert result['number_of_payments'] == 4
    
    def test_sample_example2_monthly(self):
        """Test monthly schedule for Example 2: €12,900 total tax."""
        result = calculate_payment_schedule(12900, 'monthly')
        
        assert result['payment_amount'] == Decimal('1075.00')
        assert result['number_of_payments'] == 12
    
    def test_sample_example3_monthly(self):
        """Test monthly schedule for Example 3: €25,900 total tax."""
        result = calculate_payment_schedule(25900, 'monthly')
        
        assert result['payment_amount'] == Decimal('2158.33')
        assert result['number_of_payments'] == 12
    
    def test_sample_example4_monthly(self):
        """Test monthly schedule for Example 4: €2,670 total tax."""
        result = calculate_payment_schedule(2670, 'monthly')
        
        assert result['payment_amount'] == Decimal('222.50')
        assert result['number_of_payments'] == 12
    
    def test_sample_example4_quarterly(self):
        """Test quarterly schedule for Example 4: €2,670 total tax."""
        result = calculate_payment_schedule(2670, 'quarterly')
        
        assert result['payment_amount'] == Decimal('667.50')
        assert result['number_of_payments'] == 4
    
    def test_return_structure(self):
        """Test that return dictionary has correct structure and keys."""
        result = calculate_payment_schedule(12000, 'monthly')
        
        assert isinstance(result, dict)
        assert 'annual_total' in result
        assert 'frequency' in result
        assert 'number_of_payments' in result
        assert 'payment_amount' in result
        assert 'schedule' in result
        
        assert isinstance(result['annual_total'], Decimal)
        assert isinstance(result['frequency'], str)
        assert isinstance(result['number_of_payments'], int)
        assert isinstance(result['payment_amount'], Decimal)
        assert isinstance(result['schedule'], list)
    
    def test_all_payments_two_decimal_places(self):
        """Test that all payment amounts are rounded to 2 decimal places."""
        result = calculate_payment_schedule(12345.678, 'monthly')
        
        # Check payment_amount
        value = str(result['payment_amount'])
        if '.' in value:
            assert len(value.split('.')[-1]) <= 2
        
        # Check each scheduled payment
        for payment in result['schedule']:
            value = str(payment['payment_amount'])
            if '.' in value:
                assert len(value.split('.')[-1]) <= 2
    
    def test_large_tax_amount(self):
        """Test payment schedule for large tax amount."""
        result = calculate_payment_schedule(100000, 'monthly')
        
        assert result['payment_amount'] == Decimal('8333.33')
        assert result['annual_total'] == Decimal('100000.00')
