"""
Integration tests for Greek Tax Calculator

This module contains end-to-end integration tests that verify the complete
workflow of the tax calculator, testing the interaction between multiple
components and functions.

Includes:
- Regression tests validating against sample_calculations.txt
- Full workflow tests (input → calculation → output)
- Payment frequency tests (monthly, quarterly, annual)
- Edge case integration tests
- File output consistency tests

To run only these tests:
    pytest tests/test_integration.py -v

To run only integration tests using markers:
    pytest -m integration -v
"""

import pytest
from decimal import Decimal
from unittest.mock import patch, mock_open, MagicMock
from tax_calculator import calculate_all_taxes, calculate_payment_schedule
from main import save_results_to_file, display_results, format_currency, MAX_ANNUAL_INCOME


# ============================================================================
# REGRESSION TESTS - Validate against sample_calculations.txt
# ============================================================================

@pytest.mark.integration
class TestSampleCalculationsRegression:
    """
    Regression tests validating calculations against documented examples
    from sample_calculations.txt.
    
    These tests serve as golden output validation - if these fail, either
    the calculator logic has changed or the documentation is out of sync.
    """
    
    def test_example_1_low_income_no_expenses(self):
        """
        Regression: Example 1 from sample_calculations.txt
        €15,000 income, €0 expenses, Monthly frequency
        """
        result = calculate_all_taxes(15000, 0)
        
        # Validate core calculations
        assert result['gross_income'] == Decimal('15000.00')
        assert result['deductible_expenses'] == Decimal('0.00')
        assert result['taxable_income'] == Decimal('15000.00')
        
        # Income tax: €10k @ 9% + €5k @ 22% = €900 + €1,100 = €2,000
        assert result['income_tax']['total_tax'] == Decimal('2000.00')
        assert result['income_tax']['effective_rate'] == Decimal('13.33')
        
        # EFKA: 20% of €15,000 = €3,000
        assert result['social_security']['total_contribution'] == Decimal('3000.00')
        assert result['social_security']['main_insurance'] == Decimal('1999.50')
        assert result['social_security']['additional_contributions'] == Decimal('1000.50')
        
        # VAT: 24% of €15,000 = €3,600
        assert result['vat']['vat_amount'] == Decimal('3600.00')
        
        # Total taxes and net income
        assert result['total_taxes'] == Decimal('5000.00')
        assert result['net_income'] == Decimal('10000.00')
        assert result['effective_total_rate'] == Decimal('33.33')
        
        # Payment schedule: Monthly
        schedule = calculate_payment_schedule(result['total_taxes'], 'monthly')
        assert schedule['number_of_payments'] == 12
        assert schedule['payment_amount'] == Decimal('416.67')
    
    def test_example_2_medium_income_with_expenses(self):
        """
        Regression: Example 2 from sample_calculations.txt
        €35,000 income, €5,000 expenses, Quarterly frequency
        """
        result = calculate_all_taxes(35000, 5000)
        
        # Validate core calculations
        assert result['gross_income'] == Decimal('35000.00')
        assert result['deductible_expenses'] == Decimal('5000.00')
        assert result['taxable_income'] == Decimal('30000.00')
        
        # Income tax on €30,000: €900 + €2,200 + €2,800 = €5,900
        assert result['income_tax']['total_tax'] == Decimal('5900.00')
        assert result['income_tax']['effective_rate'] == Decimal('19.67')
        
        # EFKA: 20% of €35,000 (gross, not taxable!) = €7,000
        assert result['social_security']['total_contribution'] == Decimal('7000.00')
        
        # VAT: 24% of €35,000 = €8,400
        assert result['vat']['vat_amount'] == Decimal('8400.00')
        
        # Total taxes and net income
        assert result['total_taxes'] == Decimal('12900.00')
        assert result['net_income'] == Decimal('22100.00')
        assert result['effective_total_rate'] == Decimal('36.86')
        
        # Payment schedule: Quarterly
        schedule = calculate_payment_schedule(result['total_taxes'], 'quarterly')
        assert schedule['number_of_payments'] == 4
        assert schedule['payment_amount'] == Decimal('3225.00')
    
    def test_example_3_high_income_substantial_expenses(self):
        """
        Regression: Example 3 from sample_calculations.txt
        €60,000 income, €10,000 expenses, Annual frequency
        """
        result = calculate_all_taxes(60000, 10000)
        
        # Validate core calculations
        assert result['gross_income'] == Decimal('60000.00')
        assert result['deductible_expenses'] == Decimal('10000.00')
        assert result['taxable_income'] == Decimal('50000.00')
        
        # Income tax on €50,000: all 5 brackets
        # €900 + €2,200 + €2,800 + €3,600 + €4,400 = €13,900
        assert result['income_tax']['total_tax'] == Decimal('13900.00')
        assert result['income_tax']['effective_rate'] == Decimal('27.80')
        
        # EFKA: 20% of €60,000 = €12,000
        assert result['social_security']['total_contribution'] == Decimal('12000.00')
        
        # VAT: 24% of €60,000 = €14,400
        assert result['vat']['vat_amount'] == Decimal('14400.00')
        
        # Total taxes and net income
        assert result['total_taxes'] == Decimal('25900.00')
        assert result['net_income'] == Decimal('34100.00')
        assert result['effective_total_rate'] == Decimal('43.17')
        
        # Payment schedule: Annual
        schedule = calculate_payment_schedule(result['total_taxes'], 'annual')
        assert schedule['number_of_payments'] == 1
        assert schedule['payment_amount'] == Decimal('25900.00')
    
    def test_example_4_low_income_high_expense_ratio(self):
        """
        Regression: Example 4 from sample_calculations.txt
        €12,000 income, €9,000 expenses (75% expense ratio), Monthly frequency
        """
        result = calculate_all_taxes(12000, 9000)
        
        # Validate core calculations
        assert result['gross_income'] == Decimal('12000.00')
        assert result['deductible_expenses'] == Decimal('9000.00')
        assert result['taxable_income'] == Decimal('3000.00')
        
        # Income tax: €3,000 @ 9% = €270
        assert result['income_tax']['total_tax'] == Decimal('270.00')
        assert result['income_tax']['effective_rate'] == Decimal('9.00')
        
        # EFKA: 20% of €12,000 (gross!) = €2,400
        # This is 80% of taxable income - illustrates EFKA burden on low-margin business
        assert result['social_security']['total_contribution'] == Decimal('2400.00')
        
        # VAT: 24% of €12,000 = €2,880
        assert result['vat']['vat_amount'] == Decimal('2880.00')
        
        # Total taxes and net income
        assert result['total_taxes'] == Decimal('2670.00')
        assert result['net_income'] == Decimal('9330.00')
        assert result['effective_total_rate'] == Decimal('22.25')
        
        # Payment schedule: Monthly
        schedule = calculate_payment_schedule(result['total_taxes'], 'monthly')
        assert schedule['number_of_payments'] == 12
        assert schedule['payment_amount'] == Decimal('222.50')


# ============================================================================
# PAYMENT FREQUENCY INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
class TestPaymentFrequencyIntegration:
    """
    Integration tests verifying that payment schedules work correctly
    for all frequency options with the same calculation.
    """
    
    def test_all_frequencies_same_calculation(self):
        """
        Test that monthly, quarterly, and annual schedules all correctly
        divide the same total tax amount.
        """
        # Use a realistic calculation
        result = calculate_all_taxes(45000, 7000)
        total_tax = result['total_taxes']
        
        # Monthly: 12 payments
        monthly = calculate_payment_schedule(total_tax, 'monthly')
        assert monthly['number_of_payments'] == 12
        assert monthly['annual_total'] == total_tax
        assert len(monthly['schedule']) == 12
        # Verify sum of all payments approximately equals total (within rounding)
        monthly_sum = sum(p['payment_amount'] for p in monthly['schedule'])
        assert abs(monthly_sum - total_tax) < Decimal('0.12')  # Max rounding error
        
        # Quarterly: 4 payments
        quarterly = calculate_payment_schedule(total_tax, 'quarterly')
        assert quarterly['number_of_payments'] == 4
        assert quarterly['annual_total'] == total_tax
        assert len(quarterly['schedule']) == 4
        quarterly_sum = sum(p['payment_amount'] for p in quarterly['schedule'])
        assert abs(quarterly_sum - total_tax) < Decimal('0.04')
        
        # Annual: 1 payment
        annual = calculate_payment_schedule(total_tax, 'annual')
        assert annual['number_of_payments'] == 1
        assert annual['annual_total'] == total_tax
        assert len(annual['schedule']) == 1
        assert annual['schedule'][0]['payment_amount'] == total_tax
    
    def test_monthly_schedule_detail(self):
        """Verify monthly payment schedule generates 12 equal payments."""
        result = calculate_all_taxes(36000, 6000)
        schedule = calculate_payment_schedule(result['total_taxes'], 'monthly')
        
        # All 12 payments should be equal (or within 1 cent due to rounding)
        payment_amounts = [p['payment_amount'] for p in schedule['schedule']]
        assert len(payment_amounts) == 12
        assert max(payment_amounts) - min(payment_amounts) <= Decimal('0.01')
        
        # Period numbers should be 1-12
        periods = [p['period_number'] for p in schedule['schedule']]
        assert periods == list(range(1, 13))
    
    def test_quarterly_schedule_detail(self):
        """Verify quarterly payment schedule generates 4 equal payments."""
        result = calculate_all_taxes(48000, 8000)
        schedule = calculate_payment_schedule(result['total_taxes'], 'quarterly')
        
        # All 4 payments should be equal
        payment_amounts = [p['payment_amount'] for p in schedule['schedule']]
        assert len(payment_amounts) == 4
        assert max(payment_amounts) - min(payment_amounts) <= Decimal('0.01')
        
        # Period numbers should be 1-4
        periods = [p['period_number'] for p in schedule['schedule']]
        assert periods == list(range(1, 5))
    
    def test_annual_schedule_detail(self):
        """Verify annual payment schedule generates 1 payment equal to total."""
        result = calculate_all_taxes(55000, 9000)
        schedule = calculate_payment_schedule(result['total_taxes'], 'annual')
        
        # Single payment equals total
        assert len(schedule['schedule']) == 1
        assert schedule['schedule'][0]['payment_amount'] == result['total_taxes']
        assert schedule['schedule'][0]['period_number'] == 1


# ============================================================================
# EDGE CASE INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
class TestEdgeCaseIntegration:
    """
    Integration tests for edge cases that exercise boundary conditions
    and unusual but valid input combinations.
    """
    
    def test_zero_income_complete_workflow(self):
        """
        Full workflow test with zero income.
        Should produce all-zero results gracefully.
        """
        result = calculate_all_taxes(0, 0)
        
        # All values should be zero
        assert result['gross_income'] == Decimal('0.00')
        assert result['deductible_expenses'] == Decimal('0.00')
        assert result['taxable_income'] == Decimal('0.00')
        assert result['income_tax']['total_tax'] == Decimal('0.00')
        assert result['income_tax']['effective_rate'] == Decimal('0.00')
        assert result['social_security']['total_contribution'] == Decimal('0.00')
        assert result['vat']['vat_amount'] == Decimal('0.00')
        assert result['total_taxes'] == Decimal('0.00')
        assert result['net_income'] == Decimal('0.00')
        
        # Payment schedule should work with zero
        for frequency in ['monthly', 'quarterly', 'annual']:
            schedule = calculate_payment_schedule(result['total_taxes'], frequency)
            assert schedule['payment_amount'] == Decimal('0.00')
            assert schedule['annual_total'] == Decimal('0.00')
    
    def test_maximum_income_boundary(self):
        """
        Test with maximum realistic income (MAX_ANNUAL_INCOME).
        Should calculate correctly without errors.
        """
        max_income = MAX_ANNUAL_INCOME  # €10,000,000
        expenses = Decimal('1000000')  # €1M expenses
        
        result = calculate_all_taxes(max_income, expenses)
        
        # Should complete without errors
        assert result['gross_income'] == Decimal(str(max_income))
        assert result['deductible_expenses'] == expenses
        assert result['taxable_income'] > 0
        assert result['total_taxes'] > 0
        assert result['net_income'] > 0
        
        # EFKA should be 20% of gross
        expected_efka = Decimal(str(max_income)) * Decimal('0.20')
        assert result['social_security']['total_contribution'] == expected_efka.quantize(Decimal('0.01'))
        
        # Should be in highest tax bracket (44%)
        assert result['income_tax']['bracket_breakdown'][-1]['rate'] == Decimal('44.00')
    
    def test_expenses_equal_income_complete_workflow(self):
        """
        Full workflow test where expenses exactly equal income.
        Should produce zero taxable income but still calculate EFKA on gross.
        """
        income = Decimal('25000.00')
        expenses = Decimal('25000.00')
        
        result = calculate_all_taxes(income, expenses)
        
        # Taxable income should be zero
        assert result['taxable_income'] == Decimal('0.00')
        
        # Income tax should be zero (no taxable income)
        assert result['income_tax']['total_tax'] == Decimal('0.00')
        assert result['income_tax']['effective_rate'] == Decimal('0.00')
        assert result['income_tax']['bracket_breakdown'] == []
        
        # EFKA still applies to GROSS income (€25,000 * 20% = €5,000)
        assert result['social_security']['total_contribution'] == Decimal('5000.00')
        
        # VAT still applies to gross income
        assert result['vat']['vat_amount'] == Decimal('6000.00')  # 24% of €25,000
        
        # Total taxes = EFKA only (no income tax)
        assert result['total_taxes'] == Decimal('5000.00')
        
        # Net income = gross - EFKA
        assert result['net_income'] == Decimal('20000.00')
    
    def test_expenses_exceed_income_complete_workflow(self):
        """
        Full workflow test where expenses exceed income.
        Should handle gracefully with zero taxable income.
        """
        income = Decimal('20000.00')
        expenses = Decimal('30000.00')
        
        result = calculate_all_taxes(income, expenses)
        
        # Taxable income should be zero (not negative)
        assert result['taxable_income'] == Decimal('0.00')
        
        # Income tax should be zero
        assert result['income_tax']['total_tax'] == Decimal('0.00')
        
        # EFKA applies to gross income
        assert result['social_security']['total_contribution'] == Decimal('4000.00')  # 20% of €20k
        
        # Total taxes = EFKA only
        assert result['total_taxes'] == Decimal('4000.00')
        
        # Net income still calculated from gross
        assert result['net_income'] == Decimal('16000.00')
    
    def test_very_small_income(self):
        """
        Test with very small but non-zero income (€100).
        Should calculate correctly with minimal amounts.
        """
        result = calculate_all_taxes(100, 0)
        
        # Should all be calculated proportionally
        assert result['gross_income'] == Decimal('100.00')
        assert result['taxable_income'] == Decimal('100.00')
        
        # Income tax: €100 @ 9% = €9.00
        assert result['income_tax']['total_tax'] == Decimal('9.00')
        
        # EFKA: €100 * 20% = €20.00
        assert result['social_security']['total_contribution'] == Decimal('20.00')
        
        # VAT: €100 * 24% = €24.00
        assert result['vat']['vat_amount'] == Decimal('24.00')
        
        # Total: €29.00
        assert result['total_taxes'] == Decimal('29.00')
        
        # Net: €71.00
        assert result['net_income'] == Decimal('71.00')


# ============================================================================
# FILE OUTPUT CONSISTENCY TESTS
# ============================================================================

@pytest.mark.integration
class TestFileOutputConsistency:
    """
    Integration tests verifying that file output contains the same
    calculation results as displayed output.
    """
    
    def test_file_output_matches_calculation(self, sample_calculation_result):
        """
        Verify that save_results_to_file produces output consistent
        with calculation results.
        """
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('main.datetime') as mock_datetime:
                # Mock datetime to get predictable filename
                mock_datetime.now.return_value.strftime.side_effect = [
                    '2024-01-15_120000',  # For filename
                    '2024-01-15 12:00:00'  # For display
                ]
                
                filename = save_results_to_file(sample_calculation_result, 'monthly')
                
                # Verify file was opened for writing
                assert filename == 'tax_calculation_2024-01-15_120000.txt'
                mock_file.assert_called_once_with(filename, 'w', encoding='utf-8')
                
                # Get the content that was written
                handle = mock_file()
                write_calls = handle.write.call_args_list
                written_content = ''.join(call[0][0] for call in write_calls)
                
                # Verify key values are present in output
                assert 'GREEK FREELANCER TAX CALCULATION RESULTS' in written_content
                assert '€35,000.00' in written_content  # Gross income
                assert '€5,000.00' in written_content   # Expenses
                assert '€30,000.00' in written_content  # Taxable income
                assert '€12,900.00' in written_content  # Total taxes
                assert '€22,100.00' in written_content  # Net income
    
    def test_file_output_includes_all_sections(self, sample_calculation_result):
        """
        Verify that file output includes all expected sections.
        """
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('main.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = '2024-01-15_120000'
                
                save_results_to_file(sample_calculation_result, 'quarterly')
                
                handle = mock_file()
                write_calls = handle.write.call_args_list
                written_content = ''.join(call[0][0] for call in write_calls)
                
                # Verify all major sections are present
                assert 'INPUT PARAMETERS' in written_content
                assert 'INCOME BREAKDOWN' in written_content
                assert 'INCOME TAX BREAKDOWN BY BRACKET' in written_content
                assert 'VAT AND SOCIAL SECURITY' in written_content
                assert 'PAYMENT SCHEDULE' in written_content
                assert 'SUMMARY' in written_content
    
    def test_file_output_handles_io_error(self, sample_calculation_result):
        """
        Verify that save_results_to_file handles IOError gracefully.
        """
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with patch('builtins.print') as mock_print:
                result = save_results_to_file(sample_calculation_result, 'annual')
                
                # Should return None on error
                assert result is None
                
                # Should print warning message
                mock_print.assert_any_call("\n⚠️  Warning: Could not save results to file.")
    
    def test_file_output_handles_generic_exception(self, sample_calculation_result):
        """
        Verify that save_results_to_file handles unexpected exceptions.
        """
        with patch('builtins.open', side_effect=Exception("Unexpected error")):
            with patch('builtins.print') as mock_print:
                result = save_results_to_file(sample_calculation_result, 'monthly')
                
                # Should return None on error
                assert result is None
                
                # Should print generic warning
                mock_print.assert_any_call("\n⚠️  Warning: An unexpected error occurred while saving file.")
    
    def test_different_frequencies_produce_different_schedules(self):
        """
        Verify that the same calculation with different frequencies
        produces different payment schedules in file output.
        """
        calc_result = calculate_all_taxes(50000, 8000)
        
        for frequency, expected_payments in [('monthly', 12), ('quarterly', 4), ('annual', 1)]:
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('main.datetime') as mock_datetime:
                    mock_datetime.now.return_value.strftime.return_value = '2024-01-15_120000'
                    
                    save_results_to_file(calc_result, frequency)
                    
                    handle = mock_file()
                    write_calls = handle.write.call_args_list
                    written_content = ''.join(call[0][0] for call in write_calls)
                    
                    # Verify frequency is mentioned
                    assert frequency.upper() in written_content
                    
                    # Verify number of payments is mentioned
                    assert str(expected_payments) in written_content


# ============================================================================
# COMPLETE WORKFLOW INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
class TestCompleteCalculationWorkflows:
    """
    End-to-end integration tests that simulate complete user workflows
    from input through calculation to output.
    """
    
    def test_typical_freelancer_scenario(self):
        """
        Simulate typical freelancer: moderate income with some expenses.
        Tests complete workflow including display and file output.
        """
        # User inputs
        gross_income = Decimal('42000.00')
        expenses = Decimal('7000.00')
        frequency = 'monthly'
        
        # Perform calculation
        result = calculate_all_taxes(gross_income, expenses)
        
        # Verify calculation components
        assert result['taxable_income'] == Decimal('35000.00')
        assert result['total_taxes'] > 0
        assert result['net_income'] > 0
        assert result['net_income'] == result['gross_income'] - result['total_taxes']
        
        # Generate payment schedule
        schedule = calculate_payment_schedule(result['total_taxes'], frequency)
        assert schedule['number_of_payments'] == 12
        
        # Verify file output can be generated
        with patch('builtins.open', mock_open()):
            with patch('main.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = '2024-01-15_120000'
                filename = save_results_to_file(result, frequency)
                assert filename is not None
    
    def test_startup_phase_freelancer_scenario(self):
        """
        Simulate startup freelancer: low income, high expenses.
        Tests edge case of high expense ratio.
        """
        gross_income = Decimal('18000.00')
        expenses = Decimal('14000.00')
        frequency = 'quarterly'
        
        result = calculate_all_taxes(gross_income, expenses)
        
        # Very low taxable income
        assert result['taxable_income'] == Decimal('4000.00')
        
        # Income tax should be low (first bracket only)
        assert result['income_tax']['total_tax'] == Decimal('360.00')  # €4,000 @ 9%
        
        # EFKA still significant relative to taxable income
        assert result['social_security']['total_contribution'] == Decimal('3600.00')  # 20% of gross
        
        # Total taxes higher than income tax alone
        assert result['total_taxes'] == Decimal('3960.00')
        
        # Net income
        assert result['net_income'] == Decimal('14040.00')
    
    def test_high_earner_scenario(self):
        """
        Simulate high-earning freelancer: high income, substantial expenses.
        Tests all tax brackets.
        """
        gross_income = Decimal('85000.00')
        expenses = Decimal('15000.00')
        frequency = 'annual'
        
        result = calculate_all_taxes(gross_income, expenses)
        
        # Taxable income in highest bracket
        assert result['taxable_income'] == Decimal('70000.00')
        
        # Should use all 5 tax brackets
        assert len(result['income_tax']['bracket_breakdown']) == 5
        assert result['income_tax']['bracket_breakdown'][-1]['rate'] == Decimal('44.00')
        
        # Significant tax burden
        assert result['income_tax']['total_tax'] > Decimal('20000.00')
        
        # EFKA on large gross income
        assert result['social_security']['total_contribution'] == Decimal('17000.00')  # 20% of €85k
        
        # High total taxes
        assert result['total_taxes'] > Decimal('35000.00')
    
    def test_cross_module_integration(self):
        """
        Test integration between tax_calculator.py and main.py modules.
        Verifies that functions from both modules work together correctly.
        """
        # Use tax_calculator functions
        calc_result = calculate_all_taxes(40000, 6000)
        schedule = calculate_payment_schedule(calc_result['total_taxes'], 'monthly')
        
        # Use main.py functions
        formatted = format_currency(calc_result['total_taxes'])
        assert '€' in formatted
        assert ',' in formatted  # Thousand separator
        
        # Verify file save integration
        with patch('builtins.open', mock_open()):
            with patch('main.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = '2024-01-15_120000'
                filename = save_results_to_file(calc_result, 'monthly')
                assert filename is not None
                assert 'tax_calculation' in filename
                assert '.txt' in filename
