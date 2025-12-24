#!/usr/bin/env python3
"""
Greek Tax Calculator - Formatters Module

This module provides formatting logic for tax calculation results with proper
separation of concerns. It includes:
- Pure formatting functions (no I/O, easy to test)
- Output writer protocols for different destinations (console, file)
- Type-safe interfaces using Python protocols

Design Principles:
- Formatters are pure functions that return List[str]
- Writers handle I/O operations (console, file, etc.)
- Easy to extend to new output formats (JSON, CSV, PDF)
- All formatting logic centralized for DRY principle
"""

from typing import List, Protocol, Union
from decimal import Decimal
from models import (
    TaxCalculationResult,
    PaymentSchedule,
    IncomeTaxBreakdown,
    VATCalculation,
    SocialSecurityCalculation
)
from config import (
    VAT_RATE,
    EFKA_TOTAL_RATE,
    EFKA_MAIN_RATE,
    EFKA_ADDITIONAL_RATE
)

__version__ = "1.0.0"


# ============================================================================
# PURE FORMATTING FUNCTIONS
# ============================================================================

def format_currency(amount: Union[Decimal, float, int]) -> str:
    """
    Format amount as currency string with consistent €X,XXX.XX formatting.
    
    This is a pure function with no side effects, making it easy to test
    and reuse across different output formats.
    
    Args:
        amount: Amount to format (Decimal, float, or int)
    
    Returns:
        Formatted currency string (e.g., "€50,000.00")
    
    Examples:
        >>> format_currency(Decimal('50000.00'))
        '€50,000.00'
        >>> format_currency(1234.5)
        '€1,234.50'
    """
    return f"€{amount:,.2f}"


def format_input_parameters(tax_result: TaxCalculationResult, payment_frequency: str) -> List[str]:
    """
    Format input parameters section for display.
    
    Pure function that generates formatted lines showing the user's input
    parameters (gross income, expenses, payment frequency).
    
    Args:
        tax_result: Tax calculation result containing input values
        payment_frequency: Payment frequency string ('monthly', 'quarterly', 'annual')
        
    Returns:
        List of formatted lines ready for rendering
    
    Examples:
        >>> lines = format_input_parameters(result, 'monthly')
        >>> print('\\n'.join(lines))
        ----------------------------------------------------------------------
        INPUT PARAMETERS
        ----------------------------------------------------------------------
        Gross Annual Income:                                      €50,000.00
        ...
    """
    lines = []
    lines.append("-" * 70)
    lines.append("INPUT PARAMETERS")
    lines.append("-" * 70)
    lines.append(f"{'Gross Annual Income:':<35} {format_currency(tax_result.gross_income):>34}")
    lines.append(f"{'Deductible Business Expenses:':<35} {format_currency(tax_result.deductible_expenses):>34}")
    lines.append(f"{'Payment Frequency:':<35} {payment_frequency.capitalize():>34}")
    return lines


def format_income_breakdown(tax_result: TaxCalculationResult) -> List[str]:
    """
    Format income breakdown section showing gross income, expenses, and taxable income.
    
    Pure function that generates formatted lines for the income breakdown.
    
    Args:
        tax_result: Tax calculation result
        
    Returns:
        List of formatted lines ready for rendering
    """
    lines = []
    lines.append("-" * 70)
    lines.append("INCOME BREAKDOWN")
    lines.append("-" * 70)
    lines.append(f"{'Gross Income:':<35} {format_currency(tax_result.gross_income):>34}")
    lines.append(f"{'Less: Deductible Expenses:':<35} {format_currency(tax_result.deductible_expenses):>34}")
    lines.append(f"{'Taxable Income:':<35} {format_currency(tax_result.taxable_income):>34}")
    return lines


def format_income_tax_breakdown(income_tax: IncomeTaxBreakdown) -> List[str]:
    """
    Format income tax breakdown by bracket with detailed calculations.
    
    Pure function that generates formatted lines showing progressive tax
    bracket calculations with amounts and rates for each bracket.
    
    Args:
        income_tax: Income tax breakdown with bracket details
        
    Returns:
        List of formatted lines ready for rendering
    """
    lines = []
    lines.append("-" * 70)
    lines.append("INCOME TAX BREAKDOWN BY BRACKET")
    lines.append("-" * 70)
    
    if income_tax.bracket_breakdown:
        for bracket in income_tax.bracket_breakdown:
            bracket_min = format_currency(bracket.bracket_min)
            if bracket.bracket_max == 'unlimited':
                bracket_range = f"{bracket_min}+"
            else:
                bracket_max = format_currency(bracket.bracket_max)
                bracket_range = f"{bracket_min} - {bracket_max}"
            
            rate_str = f"{bracket.rate:.0f}%"
            taxable_amt = format_currency(bracket.taxable_amount)
            tax_amt = format_currency(bracket.tax_amount)
            
            lines.append(f"  {bracket_range:<30} @ {rate_str:>4}")
            lines.append(f"    {'Taxable amount:':<30} {taxable_amt:>30}")
            lines.append(f"    {'Tax on this bracket:':<30} {tax_amt:>30}")
            lines.append("")
    else:
        lines.append("  No income tax (taxable income is zero)")
    
    lines.append(f"{'Total Income Tax:':<35} {format_currency(income_tax.total_tax):>34}")
    lines.append(f"{'Effective Income Tax Rate:':<35} {income_tax.effective_rate:>33.2f}%")
    return lines


def format_vat_and_social_security(vat: VATCalculation, social_security: SocialSecurityCalculation) -> List[str]:
    """
    Format VAT and social security contributions section.
    
    Pure function that generates formatted lines showing VAT to be collected
    from clients and EFKA social security contributions breakdown.
    
    Args:
        vat: VAT calculation details
        social_security: Social security calculation details
        
    Returns:
        List of formatted lines ready for rendering
    """
    lines = []
    lines.append("-" * 70)
    lines.append("VAT AND SOCIAL SECURITY")
    lines.append("-" * 70)
    
    vat_rate_pct = float(VAT_RATE * 100)
    efka_total_pct = float(EFKA_TOTAL_RATE * 100)
    efka_main_pct = float(EFKA_MAIN_RATE * 100)
    efka_additional_pct = float(EFKA_ADDITIONAL_RATE * 100)
    
    lines.append(f"{'VAT (' + f'{vat_rate_pct:.0f}%' + '):':<35} {format_currency(vat.vat_amount):>34}")
    lines.append(f"  {'(To be collected from clients)':<35}")
    lines.append("")
    lines.append(f"{'Social Security (EFKA - ' + f'{efka_total_pct:.0f}%' + '):':<35} {format_currency(social_security.total_contribution):>34}")
    lines.append(f"  {'Main Insurance (' + f'{efka_main_pct:.2f}%' + '):':<35} {format_currency(social_security.main_insurance):>34}")
    lines.append(f"  {'Additional Contributions (' + f'{efka_additional_pct:.2f}%' + '):':<35} {format_currency(social_security.additional_contributions):>34}")
    return lines


def format_payment_schedule(payment_schedule: PaymentSchedule, payment_frequency: str) -> List[str]:
    """
    Format payment schedule section with installment details.
    
    Pure function that generates formatted lines showing the payment schedule
    broken down into installments based on frequency.
    
    Args:
        payment_schedule: Payment schedule with installment details
        payment_frequency: Payment frequency string ('monthly', 'quarterly', 'annual')
        
    Returns:
        List of formatted lines ready for rendering
    """
    lines = []
    lines.append("-" * 70)
    lines.append(f"PAYMENT SCHEDULE ({payment_frequency.upper()})")
    lines.append("-" * 70)
    lines.append(f"{'Total Annual Tax (excl. VAT):':<35} {format_currency(payment_schedule.annual_total):>34}")
    lines.append(f"{'Number of Payments:':<35} {payment_schedule.number_of_installments:>34}")
    lines.append(f"{'Amount per Payment:':<35} {format_currency(payment_schedule.installment_amount):>34}")
    
    if payment_schedule.number_of_installments > 1:
        lines.append(f"\n  Payment Schedule:")
        for payment in payment_schedule.schedule:
            period_label = f"Payment #{payment.period_number}"
            lines.append(f"    {period_label:<30} {format_currency(payment.payment_amount):>34}")
    return lines


def format_summary(tax_result: TaxCalculationResult) -> List[str]:
    """
    Format summary section with totals and effective rates.
    
    Pure function that generates formatted lines for the final summary
    showing gross income, total taxes, net income, and effective rates.
    
    Args:
        tax_result: Tax calculation result
        
    Returns:
        List of formatted lines ready for rendering
    """
    lines = []
    lines.append("=" * 70)
    lines.append("SUMMARY")
    lines.append("=" * 70)
    lines.append(f"{'Gross Income:':<35} {format_currency(tax_result.gross_income):>34}")
    lines.append(f"{'Total Taxes (Income Tax + EFKA):':<35} {format_currency(tax_result.total_taxes):>34}")
    lines.append(f"{'Effective Total Tax Rate:':<35} {tax_result.effective_total_rate:>33.2f}%")
    lines.append(f"{'Net Income (After Taxes):':<35} {format_currency(tax_result.net_income):>34}")
    lines.append("=" * 70)
    lines.append(f"\nNote: VAT of {format_currency(tax_result.vat.vat_amount)} should be collected from clients")
    lines.append("      and remitted to tax authorities separately.")
    lines.append("=" * 70)
    return lines


# ============================================================================
# OUTPUT WRITER PROTOCOL AND IMPLEMENTATIONS
# ============================================================================

class OutputWriter(Protocol):
    """
    Protocol defining the interface for output writers.
    
    Output writers handle the I/O operations for different destinations
    (console, file, network, etc.). This protocol ensures type safety
    and makes it easy to add new output destinations.
    
    Any class implementing this protocol must provide a write() method
    that accepts a string and handles the output appropriately.
    """
    
    def write(self, content: str) -> None:
        """
        Write content to the output destination.
        
        Args:
            content: String content to write
        """
        ...


class ConsoleWriter:
    """
    Output writer that prints content to console/stdout.
    
    This writer is used for interactive display of results in the terminal.
    It handles line-by-line printing for better readability.
    
    Examples:
        >>> writer = ConsoleWriter()
        >>> lines = ["Line 1", "Line 2", "Line 3"]
        >>> writer.write_lines(lines)
        Line 1
        Line 2
        Line 3
    """
    
    def write(self, content: str) -> None:
        """
        Write content to console via print().
        
        Args:
            content: String content to print
        """
        print(content)
    
    def write_lines(self, lines: List[str]) -> None:
        """
        Write multiple lines to console.
        
        Args:
            lines: List of strings to print
        """
        for line in lines:
            print(line)


class FileWriter:
    """
    Output writer that writes content to a file.
    
    This writer is used for saving results to text files. It provides
    methods for both writing complete content and building content from
    formatted lines.
    
    Attributes:
        file_path: Path to the file to write to
    
    Examples:
        >>> writer = FileWriter("output/results.txt")
        >>> lines = ["Line 1", "Line 2"]
        >>> content = writer.lines_to_content(lines)
        >>> # File I/O happens in calling code
    """
    
    def __init__(self, file_path: str):
        """
        Initialize file writer with target file path.
        
        Args:
            file_path: Path to the file to write to
        """
        self.file_path = file_path
    
    def write(self, content: str) -> None:
        """
        Write content to file.
        
        Note: This method is provided for protocol compatibility.
        In practice, file writing is handled by the calling code
        to allow proper error handling and security checks.
        
        Args:
            content: String content to write
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def lines_to_content(lines: List[str]) -> str:
        """
        Convert list of lines to file content string.
        
        This is a pure function that joins lines with newlines,
        making it easy to test and reuse.
        
        Args:
            lines: List of formatted lines
            
        Returns:
            String with lines joined by newlines
        """
        return '\n'.join(lines)
