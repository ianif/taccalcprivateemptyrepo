#!/usr/bin/env python3
"""
Greek Tax Calculator - Data Models Module

This module defines structured dataclasses for type-safe data passing throughout
the tax calculation pipeline. Using dataclasses instead of dictionaries provides:
- Better IDE support with autocomplete
- Type safety and validation
- Immutable results (frozen=True)
- Clear data contracts between functions
- Easier testing and debugging

All models use Python's Decimal type for financial precision and include
serialization methods for JSON/file output.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Union, Any, Optional
from datetime import datetime

__version__ = "1.0.0"


# ============================================================================
# INPUT DATA MODELS
# ============================================================================

@dataclass
class TaxInput:
    """
    Input parameters for tax calculations with validation.
    
    This class represents the initial user input and validates that:
    - Both values are non-negative
    - Deductible expenses don't exceed gross income
    
    Attributes:
        gross_income (Decimal): Total gross annual income in EUR (excluding VAT)
        deductible_expenses (Decimal): Total deductible business expenses in EUR
    
    Raises:
        ValueError: If validation fails in __post_init__
    
    Examples:
        >>> # Valid input
        >>> tax_input = TaxInput(
        ...     gross_income=Decimal('50000.00'),
        ...     deductible_expenses=Decimal('10000.00')
        ... )
        
        >>> # Invalid: expenses exceed income
        >>> TaxInput(
        ...     gross_income=Decimal('30000.00'),
        ...     deductible_expenses=Decimal('40000.00')
        ... )
        ValueError: Deductible expenses (€40,000.00) cannot exceed gross income (€30,000.00)
    """
    gross_income: Decimal
    deductible_expenses: Decimal
    
    def __post_init__(self):
        """Validate input data after initialization."""
        # Convert to Decimal if necessary
        if not isinstance(self.gross_income, Decimal):
            object.__setattr__(self, 'gross_income', Decimal(str(self.gross_income)))
        if not isinstance(self.deductible_expenses, Decimal):
            object.__setattr__(self, 'deductible_expenses', Decimal(str(self.deductible_expenses)))
        
        # Validate non-negative
        if self.gross_income < 0:
            raise ValueError(
                f"Gross income must be non-negative (got {self.gross_income})"
            )
        
        if self.deductible_expenses < 0:
            raise ValueError(
                f"Deductible expenses must be non-negative (got {self.deductible_expenses})"
            )
        
        # Validate expenses don't exceed income
        if self.deductible_expenses > self.gross_income:
            raise ValueError(
                f"Deductible expenses (€{self.deductible_expenses:,.2f}) cannot exceed "
                f"gross income (€{self.gross_income:,.2f})"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'gross_income': str(self.gross_income),
            'deductible_expenses': str(self.deductible_expenses)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxInput':
        """Create instance from dictionary."""
        return cls(
            gross_income=Decimal(str(data['gross_income'])),
            deductible_expenses=Decimal(str(data['deductible_expenses']))
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"TaxInput(gross_income=€{self.gross_income:,.2f}, "
            f"deductible_expenses=€{self.deductible_expenses:,.2f})"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"TaxInput(gross_income=Decimal('{self.gross_income}'), "
            f"deductible_expenses=Decimal('{self.deductible_expenses}'))"
        )


# ============================================================================
# TAX CALCULATION RESULT MODELS
# ============================================================================

@dataclass(frozen=True)
class BracketBreakdown:
    """
    Detailed breakdown of tax calculation for a single income tax bracket.
    
    This immutable dataclass represents how much income falls within a specific
    tax bracket and the tax calculated for that portion.
    
    Attributes:
        bracket_min (Decimal): Lower bound of this bracket (inclusive)
        bracket_max (Union[Decimal, str]): Upper bound ('unlimited' for top bracket)
        rate (Decimal): Tax rate as percentage (e.g., Decimal('9.00') for 9%)
        taxable_amount (Decimal): Amount of income in this bracket
        tax_amount (Decimal): Tax calculated for this bracket
    
    Examples:
        >>> bracket = BracketBreakdown(
        ...     bracket_min=Decimal('0.00'),
        ...     bracket_max=Decimal('10000.00'),
        ...     rate=Decimal('9.00'),
        ...     taxable_amount=Decimal('10000.00'),
        ...     tax_amount=Decimal('900.00')
        ... )
    """
    bracket_min: Decimal
    bracket_max: Union[Decimal, str]  # 'unlimited' for top bracket
    rate: Decimal  # As percentage (9.00 for 9%)
    taxable_amount: Decimal
    tax_amount: Decimal
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'bracket_min': str(self.bracket_min),
            'bracket_max': str(self.bracket_max) if isinstance(self.bracket_max, Decimal) else self.bracket_max,
            'rate': str(self.rate),
            'taxable_amount': str(self.taxable_amount),
            'tax_amount': str(self.tax_amount)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BracketBreakdown':
        """Create instance from dictionary."""
        bracket_max = data['bracket_max']
        if bracket_max != 'unlimited':
            bracket_max = Decimal(str(bracket_max))
        
        return cls(
            bracket_min=Decimal(str(data['bracket_min'])),
            bracket_max=bracket_max,
            rate=Decimal(str(data['rate'])),
            taxable_amount=Decimal(str(data['taxable_amount'])),
            tax_amount=Decimal(str(data['tax_amount']))
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        if self.bracket_max == 'unlimited':
            range_str = f"€{self.bracket_min:,.2f}+"
        else:
            range_str = f"€{self.bracket_min:,.2f} - €{self.bracket_max:,.2f}"
        return f"Bracket {range_str} @ {self.rate:.0f}%: €{self.tax_amount:,.2f}"


@dataclass(frozen=True)
class IncomeTaxBreakdown:
    """
    Complete income tax calculation results with bracket-by-bracket breakdown.
    
    This immutable dataclass contains the full progressive income tax calculation,
    including details for each tax bracket that applies to the taxpayer's income.
    
    Attributes:
        total_tax (Decimal): Total income tax amount
        effective_rate (Decimal): Effective tax rate as percentage
        bracket_breakdown (List[BracketBreakdown]): Tax details for each bracket
    
    Examples:
        >>> income_tax = IncomeTaxBreakdown(
        ...     total_tax=Decimal('2000.00'),
        ...     effective_rate=Decimal('13.33'),
        ...     bracket_breakdown=[...]
        ... )
    """
    total_tax: Decimal
    effective_rate: Decimal  # As percentage
    bracket_breakdown: List[BracketBreakdown] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'total_tax': str(self.total_tax),
            'effective_rate': str(self.effective_rate),
            'bracket_breakdown': [bracket.to_dict() for bracket in self.bracket_breakdown]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IncomeTaxBreakdown':
        """Create instance from dictionary."""
        return cls(
            total_tax=Decimal(str(data['total_tax'])),
            effective_rate=Decimal(str(data['effective_rate'])),
            bracket_breakdown=[
                BracketBreakdown.from_dict(b) for b in data.get('bracket_breakdown', [])
            ]
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Income Tax: €{self.total_tax:,.2f} "
            f"(effective rate: {self.effective_rate:.2f}%)"
        )


@dataclass(frozen=True)
class VATCalculation:
    """
    VAT (Value Added Tax) calculation results.
    
    Immutable dataclass representing VAT that should be collected from clients.
    
    Attributes:
        vat_amount (Decimal): VAT to be collected
        rate (Decimal): VAT rate as percentage (e.g., Decimal('24.00') for 24%)
    
    Examples:
        >>> vat = VATCalculation(
        ...     vat_amount=Decimal('12000.00'),
        ...     rate=Decimal('24.00')
        ... )
    """
    vat_amount: Decimal
    rate: Decimal  # As percentage
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'vat_amount': str(self.vat_amount),
            'rate': str(self.rate)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VATCalculation':
        """Create instance from dictionary."""
        return cls(
            vat_amount=Decimal(str(data['vat_amount'])),
            rate=Decimal(str(data['rate']))
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"VAT ({self.rate:.0f}%): €{self.vat_amount:,.2f}"


@dataclass(frozen=True)
class SocialSecurityCalculation:
    """
    EFKA social security contribution calculation results.
    
    Immutable dataclass representing social security contributions with breakdown
    into main insurance and additional contributions.
    
    Attributes:
        total_contribution (Decimal): Total EFKA contribution
        main_insurance (Decimal): Main insurance contribution (13.33%)
        additional_contributions (Decimal): Additional contributions (6.67%)
        rate (Decimal): Total rate as percentage (20.00%)
    
    Examples:
        >>> efka = SocialSecurityCalculation(
        ...     total_contribution=Decimal('10000.00'),
        ...     main_insurance=Decimal('6665.00'),
        ...     additional_contributions=Decimal('3335.00'),
        ...     rate=Decimal('20.00')
        ... )
    """
    total_contribution: Decimal
    main_insurance: Decimal
    additional_contributions: Decimal
    rate: Decimal  # As percentage
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'total_contribution': str(self.total_contribution),
            'main_insurance': str(self.main_insurance),
            'additional_contributions': str(self.additional_contributions),
            'rate': str(self.rate)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialSecurityCalculation':
        """Create instance from dictionary."""
        return cls(
            total_contribution=Decimal(str(data['total_contribution'])),
            main_insurance=Decimal(str(data['main_insurance'])),
            additional_contributions=Decimal(str(data['additional_contributions'])),
            rate=Decimal(str(data['rate']))
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"EFKA ({self.rate:.0f}%): €{self.total_contribution:,.2f}"


@dataclass(frozen=True)
class TaxCalculationResult:
    """
    Comprehensive tax calculation results for Greek freelancers.
    
    This immutable dataclass contains all tax calculations including income tax,
    VAT, social security, and derived metrics like net income and effective rates.
    
    Attributes:
        gross_income (Decimal): Total gross income (excluding VAT)
        deductible_expenses (Decimal): Total deductible business expenses
        taxable_income (Decimal): Income after deducting expenses
        income_tax (IncomeTaxBreakdown): Income tax calculation details
        vat (VATCalculation): VAT calculation details
        social_security (SocialSecurityCalculation): EFKA contribution details
        total_taxes (Decimal): Sum of income tax and social security
        total_obligations (Decimal): Total including VAT
        net_income (Decimal): Income after all taxes and contributions
        effective_total_rate (Decimal): Total tax burden as percentage
    
    Examples:
        >>> result = TaxCalculationResult(
        ...     gross_income=Decimal('50000.00'),
        ...     deductible_expenses=Decimal('10000.00'),
        ...     taxable_income=Decimal('40000.00'),
        ...     income_tax=income_tax_breakdown,
        ...     vat=vat_calculation,
        ...     social_security=social_security_calculation,
        ...     total_taxes=Decimal('15900.00'),
        ...     total_obligations=Decimal('27900.00'),
        ...     net_income=Decimal('34100.00'),
        ...     effective_total_rate=Decimal('31.80')
        ... )
    """
    gross_income: Decimal
    deductible_expenses: Decimal
    taxable_income: Decimal
    income_tax: IncomeTaxBreakdown
    vat: VATCalculation
    social_security: SocialSecurityCalculation
    total_taxes: Decimal
    total_obligations: Decimal
    net_income: Decimal
    effective_total_rate: Decimal
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'gross_income': str(self.gross_income),
            'deductible_expenses': str(self.deductible_expenses),
            'taxable_income': str(self.taxable_income),
            'income_tax': self.income_tax.to_dict(),
            'vat': self.vat.to_dict(),
            'social_security': self.social_security.to_dict(),
            'total_taxes': str(self.total_taxes),
            'total_obligations': str(self.total_obligations),
            'net_income': str(self.net_income),
            'effective_total_rate': str(self.effective_total_rate)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxCalculationResult':
        """Create instance from dictionary."""
        return cls(
            gross_income=Decimal(str(data['gross_income'])),
            deductible_expenses=Decimal(str(data['deductible_expenses'])),
            taxable_income=Decimal(str(data['taxable_income'])),
            income_tax=IncomeTaxBreakdown.from_dict(data['income_tax']),
            vat=VATCalculation.from_dict(data['vat']),
            social_security=SocialSecurityCalculation.from_dict(data['social_security']),
            total_taxes=Decimal(str(data['total_taxes'])),
            total_obligations=Decimal(str(data['total_obligations'])),
            net_income=Decimal(str(data['net_income'])),
            effective_total_rate=Decimal(str(data['effective_total_rate']))
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Tax Calculation Result:\n"
            f"  Gross Income: €{self.gross_income:,.2f}\n"
            f"  Taxable Income: €{self.taxable_income:,.2f}\n"
            f"  Total Taxes: €{self.total_taxes:,.2f}\n"
            f"  Net Income: €{self.net_income:,.2f}\n"
            f"  Effective Rate: {self.effective_total_rate:.2f}%"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"TaxCalculationResult(gross_income=Decimal('{self.gross_income}'), "
            f"total_taxes=Decimal('{self.total_taxes}'), "
            f"net_income=Decimal('{self.net_income}'))"
        )


# ============================================================================
# PAYMENT SCHEDULE MODELS
# ============================================================================

@dataclass(frozen=True)
class PaymentInstallment:
    """
    Single payment installment in a payment schedule.
    
    Attributes:
        period_number (int): Payment number (1, 2, 3, etc.)
        payment_amount (Decimal): Amount to pay in this installment
    
    Examples:
        >>> installment = PaymentInstallment(
        ...     period_number=1,
        ...     payment_amount=Decimal('1000.00')
        ... )
    """
    period_number: int
    payment_amount: Decimal
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'period_number': self.period_number,
            'payment_amount': str(self.payment_amount)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaymentInstallment':
        """Create instance from dictionary."""
        return cls(
            period_number=int(data['period_number']),
            payment_amount=Decimal(str(data['payment_amount']))
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Payment #{self.period_number}: €{self.payment_amount:,.2f}"


@dataclass(frozen=True)
class PaymentSchedule:
    """
    Complete payment schedule for tax payments.
    
    This immutable dataclass represents how annual tax obligations are broken down
    into installments based on payment frequency (monthly, quarterly, annual).
    
    Attributes:
        annual_total (Decimal): Total annual tax amount
        frequency (str): Payment frequency ('monthly', 'quarterly', 'annual')
        number_of_installments (int): Number of payment installments
        installment_amount (Decimal): Amount per installment
        schedule (List[PaymentInstallment]): List of individual installment details
    
    Examples:
        >>> # Monthly payment schedule for €12,000 annual tax
        >>> schedule = PaymentSchedule(
        ...     annual_total=Decimal('12000.00'),
        ...     frequency='monthly',
        ...     number_of_installments=12,
        ...     installment_amount=Decimal('1000.00'),
        ...     schedule=[PaymentInstallment(1, Decimal('1000.00')), ...]
        ... )
    """
    annual_total: Decimal
    frequency: str
    number_of_installments: int
    installment_amount: Decimal
    schedule: List[PaymentInstallment] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'annual_total': str(self.annual_total),
            'frequency': self.frequency,
            'number_of_payments': self.number_of_installments,  # Legacy key name
            'number_of_installments': self.number_of_installments,
            'payment_amount': str(self.installment_amount),  # Legacy key name
            'installment_amount': str(self.installment_amount),
            'schedule': [installment.to_dict() for installment in self.schedule]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaymentSchedule':
        """Create instance from dictionary."""
        # Support both old and new key names
        num_installments = data.get('number_of_installments', data.get('number_of_payments', 0))
        installment_amt = data.get('installment_amount', data.get('payment_amount', '0'))
        
        return cls(
            annual_total=Decimal(str(data['annual_total'])),
            frequency=data['frequency'],
            number_of_installments=int(num_installments),
            installment_amount=Decimal(str(installment_amt)),
            schedule=[
                PaymentInstallment.from_dict(inst) for inst in data.get('schedule', [])
            ]
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Payment Schedule ({self.frequency}):\n"
            f"  Annual Total: €{self.annual_total:,.2f}\n"
            f"  {self.number_of_installments} payments of €{self.installment_amount:,.2f}"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"PaymentSchedule(annual_total=Decimal('{self.annual_total}'), "
            f"frequency='{self.frequency}', "
            f"number_of_installments={self.number_of_installments}, "
            f"installment_amount=Decimal('{self.installment_amount}'))"
        )


# ============================================================================
# MODULE TESTING (only runs when module is executed directly)
# ============================================================================

if __name__ == "__main__":
    print("Greek Tax Calculator - Data Models Module - Test Run")
    print("=" * 70)
    
    # Test TaxInput
    print("\n1. Testing TaxInput:")
    print("-" * 70)
    try:
        tax_input = TaxInput(
            gross_income=Decimal('50000.00'),
            deductible_expenses=Decimal('10000.00')
        )
        print(f"✓ Created: {tax_input}")
        print(f"  to_dict(): {tax_input.to_dict()}")
        
        # Test validation
        invalid_input = TaxInput(
            gross_income=Decimal('30000.00'),
            deductible_expenses=Decimal('40000.00')
        )
    except ValueError as e:
        print(f"✓ Validation working: {e}")
    
    # Test BracketBreakdown
    print("\n2. Testing BracketBreakdown:")
    print("-" * 70)
    bracket = BracketBreakdown(
        bracket_min=Decimal('0.00'),
        bracket_max=Decimal('10000.00'),
        rate=Decimal('9.00'),
        taxable_amount=Decimal('10000.00'),
        tax_amount=Decimal('900.00')
    )
    print(f"✓ Created: {bracket}")
    
    # Test PaymentSchedule
    print("\n3. Testing PaymentSchedule:")
    print("-" * 70)
    installments = [
        PaymentInstallment(i, Decimal('1000.00'))
        for i in range(1, 13)
    ]
    schedule = PaymentSchedule(
        annual_total=Decimal('12000.00'),
        frequency='monthly',
        number_of_installments=12,
        installment_amount=Decimal('1000.00'),
        schedule=installments
    )
    print(f"✓ Created: {schedule}")
    
    # Test serialization
    print("\n4. Testing Serialization:")
    print("-" * 70)
    schedule_dict = schedule.to_dict()
    print(f"✓ to_dict() works")
    schedule_restored = PaymentSchedule.from_dict(schedule_dict)
    print(f"✓ from_dict() works: {schedule_restored.annual_total == schedule.annual_total}")
    
    print("\n" + "=" * 70)
    print("All data model tests passed!")
    print("=" * 70)
