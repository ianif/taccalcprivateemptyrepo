# Greek Freelancer Tax Calculator

A comprehensive command-line tool for calculating taxes, social security contributions, and VAT obligations for freelancers operating in Greece. This calculator implements the 2024 Greek tax law and provides detailed breakdowns of all tax components with multiple payment schedule options.

## Table of Contents

- [Features](#features)
- [Target Users](#target-users)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Calculator](#running-the-calculator)
    - [Interactive Mode (Default)](#interactive-mode-default)
    - [Non-Interactive Mode (Command-Line Arguments)](#non-interactive-mode-command-line-arguments)
    - [Hybrid Mode](#hybrid-mode)
  - [Command-Line Usage Examples](#command-line-usage-examples)
  - [Interactive Mode Input Guide](#interactive-mode-input-guide)
- [Examples](#examples) *(See also: [sample_calculations.txt](sample_calculations.txt) for detailed worked examples)*
  - [Example 1: Low Income (€15,000)](#example-1-low-income-15000)
  - [Example 2: Medium Income (€35,000)](#example-2-medium-income-35000)
  - [Example 3: High Income (€60,000)](#example-3-high-income-60000)
  - [Example 4: Income with Deductible Expenses](#example-4-income-with-deductible-expenses)
- [Understanding Greek Freelancer Taxes](#understanding-greek-freelancer-taxes)
  - [Income Tax (Progressive)](#income-tax-progressive)
  - [VAT (Value Added Tax)](#vat-value-added-tax)
  - [EFKA Social Security](#efka-social-security)
- [Tax Rates and Brackets](#tax-rates-and-brackets)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)
- [Legal Disclaimer](#legal-disclaimer)
- [Contributing](#contributing)

## Features

- **Progressive Income Tax Calculation**: Accurately calculates income tax across all 5 Greek tax brackets (9%, 22%, 28%, 36%, 44%)
- **Social Security Contributions**: Computes EFKA contributions (20% total: 13.33% main + 6.67% additional)
- **VAT Computation**: Calculates 24% VAT obligations for client billing
- **Deductible Expenses**: Supports business expense deductions from taxable income
- **Multiple Payment Schedules**: Choose monthly, quarterly, or annual payment frequencies
- **Detailed Breakdowns**: Shows tax calculations per bracket with effective tax rates
- **Results Export**: Automatically saves calculations to timestamped text files
- **Input Validation**: Robust error checking with helpful guidance messages
- **Command-Line Interface**: Supports interactive, non-interactive, and hybrid modes for flexibility
- **Automation Support**: Full CLI argument support for scripting and batch processing
- **No External Dependencies**: Uses only Python standard library
- **User-Friendly Interface**: Clear prompts and formatted output for easy understanding

## Target Users

This tool is designed for:

- **Greek Freelancers**: Self-employed professionals, consultants, and contractors operating in Greece
- **Tax Planning**: Individuals estimating annual tax obligations for budgeting purposes
- **Scenario Analysis**: Comparing different income levels and expense deduction impacts
- **Accountants**: Quick estimates for client consultations (not a replacement for official calculations)

## Requirements

- **Python 3.6 or higher** (uses f-string formatting)
- No external libraries or dependencies required
- Works on Windows, macOS, and Linux

To check your Python version:

```bash
python3 --version
```

## Installation

1. **Clone or download this repository**:

```bash
git clone <repository-url>
cd greek-freelancer-tax-calculator
```

2. **No additional installation needed** - the calculator uses only Python's standard library.

## Usage

### Running the Calculator

The calculator supports three usage modes:

1. **Interactive Mode** (default): Guided prompts for all inputs
2. **Non-Interactive Mode**: All parameters via command-line arguments
3. **Hybrid Mode**: Mix of command-line arguments and prompts

#### Interactive Mode (Default)

Open a terminal or command prompt, navigate to the project directory, and run:

```bash
python3 main.py
```

On Windows, you might need to use:

```bash
python main.py
```

The calculator will interactively guide you through all required inputs.

#### Non-Interactive Mode (Command-Line Arguments)

For automation, scripting, or quick calculations, provide all parameters via command-line arguments:

```bash
# Basic non-interactive calculation
python main.py --income 50000 --expenses 10000 --frequency monthly

# With custom output file
python main.py --income 35000 --expenses 5000 --frequency quarterly --output my_taxes.txt

# Quiet mode (minimal output, only results)
python main.py --income 60000 --expenses 0 --frequency annual --quiet

# Strict non-interactive (fails if any required arg is missing)
python main.py --income 50000 --expenses 10000 --frequency monthly --no-interactive
```

**Available Command-Line Arguments:**

| Argument | Description | Example |
|----------|-------------|---------|
| `--income AMOUNT` | Gross annual income in euros | `--income 50000` |
| `--expenses AMOUNT` | Deductible business expenses in euros | `--expenses 10000` |
| `--frequency FREQ` | Payment frequency: `monthly`, `quarterly`, or `annual` | `--frequency quarterly` |
| `--output PATH` | Custom output file path | `--output my_calculation.txt` |
| `--no-interactive` | Fail if required args missing (strict mode) | `--no-interactive` |
| `--version` | Show version and exit | `--version` |
| `-v, --verbose` | Enable verbose logging (DEBUG level) | `--verbose` |
| `-q, --quiet` | Quiet mode (only warnings/errors) | `--quiet` |
| `--log-file PATH` | Custom log file path | `--log-file /tmp/tax.log` |
| `--no-log-file` | Disable file logging for privacy | `--no-log-file` |
| `-h, --help` | Show help message and exit | `--help` |

**Exit Codes:**
- `0`: Success
- `1`: Validation error or calculation failure
- `2`: Missing required arguments in `--no-interactive` mode

#### Hybrid Mode

Provide some arguments and get prompted for the rest:

```bash
# Provide income, get prompted for expenses and frequency
python main.py --income 50000

# Provide income and frequency, get prompted for expenses
python main.py --income 50000 --frequency quarterly
```

This is useful for scripting scenarios where some values are known and others need user input.

### Command-Line Usage Examples

**Example 1: Quick calculation for medium income**
```bash
python main.py --income 35000 --expenses 5000 --frequency monthly
```

**Example 2: High income with verbose logging**
```bash
python main.py --income 75000 --expenses 15000 --frequency quarterly --verbose
```

**Example 3: Low income, quiet output, custom file**
```bash
python main.py --income 18000 --expenses 0 --frequency annual --quiet --output tax_2024.txt
```

**Example 4: Automation-friendly (strict mode)**
```bash
python main.py --income 50000 --expenses 10000 --frequency monthly --no-interactive --quiet
```
This fails immediately if any required argument is missing, perfect for scripts.

**Example 5: Privacy mode (no file logging)**
```bash
python main.py --income 40000 --expenses 8000 --frequency quarterly --no-log-file
```

**Example 6: Check version**
```bash
python main.py --version
# Output: Greek Freelancer Tax Calculator v1.0.0
```

### Interactive Mode Input Guide

The calculator will guide you through the following steps:

1. **Gross Annual Income**: Enter your total annual income excluding VAT (e.g., 50000 for €50,000)
2. **Deductible Business Expenses**: Enter your total deductible expenses (e.g., 10000 for €10,000)
   - Enter 0 if you have no expenses to deduct
   - Must not exceed gross income
3. **Payment Frequency**: Choose how you'd like to view payment schedules:
   - Monthly (12 payments)
   - Quarterly (4 payments)
   - Annual (1 payment)
4. **Review and Confirm**: Verify your inputs before calculation

The calculator will then display:
- Detailed tax breakdown by bracket
- VAT obligations
- Social security contributions
- Payment schedule
- Net income after taxes

Results are automatically saved to a timestamped file in the same directory.

## Examples

For a **complete guide with detailed step-by-step calculations**, see [`sample_calculations.txt`](sample_calculations.txt). This file includes:
- Four comprehensive worked examples covering different income scenarios
- Detailed breakdown of progressive tax bracket calculations
- Monthly, quarterly, and annual payment schedules for each scenario
- Tax savings analysis showing the impact of deductible expenses
- Edge cases (low income with high expenses)
- Comparison table and key takeaways

**Quick Examples Overview:**

### Example 1: Low Income (€15,000)

**Scenario**: Freelancer with €15,000 gross annual income and no deductible expenses.

**Input**:
- Gross Annual Income: €15,000
- Deductible Expenses: €0
- Payment Frequency: Monthly

**Expected Results**:
- **Taxable Income**: €15,000
- **Income Tax**: €2,000
  - First €10,000 @ 9% = €900
  - Next €5,000 @ 22% = €1,100
- **Effective Income Tax Rate**: 13.33%
- **EFKA Social Security**: €3,000 (20%)
- **Total Taxes**: €5,000
- **Net Income**: €10,000
- **Effective Total Tax Rate**: 33.33%
- **VAT to Collect**: €3,600 (24%)
- **Monthly Tax Payment**: €416.67

### Example 2: Medium Income (€35,000)

**Scenario**: Freelancer with €35,000 gross annual income and no deductible expenses.

**Input**:
- Gross Annual Income: €35,000
- Deductible Expenses: €0
- Payment Frequency: Quarterly

**Expected Results**:
- **Taxable Income**: €35,000
- **Income Tax**: €8,200
  - First €10,000 @ 9% = €900
  - Next €10,000 @ 22% = €2,200
  - Next €10,000 @ 28% = €2,800
  - Next €5,000 @ 36% = €1,800
  - Remaining €0 @ 44% = €0
- **Effective Income Tax Rate**: 23.43%
- **EFKA Social Security**: €7,000 (20%)
- **Total Taxes**: €15,200
- **Net Income**: €19,800
- **Effective Total Tax Rate**: 43.43%
- **VAT to Collect**: €8,400 (24%)
- **Quarterly Tax Payment**: €3,800

### Example 3: High Income (€60,000)

**Scenario**: High-earning freelancer with €60,000 gross annual income and no deductible expenses.

**Input**:
- Gross Annual Income: €60,000
- Deductible Expenses: €0
- Payment Frequency: Annual

**Expected Results**:
- **Taxable Income**: €60,000
- **Income Tax**: €17,000
  - First €10,000 @ 9% = €900
  - Next €10,000 @ 22% = €2,200
  - Next €10,000 @ 28% = €2,800
  - Next €10,000 @ 36% = €3,600
  - Remaining €20,000 @ 44% = €8,800
- **Effective Income Tax Rate**: 28.33%
- **EFKA Social Security**: €12,000 (20%)
- **Total Taxes**: €29,000
- **Net Income**: €31,000
- **Effective Total Tax Rate**: 48.33%
- **VAT to Collect**: €14,400 (24%)
- **Annual Tax Payment**: €29,000

### Example 4: Income with Deductible Expenses

**Scenario**: Freelancer with €50,000 gross income and €12,000 in deductible business expenses (office rent, equipment, software subscriptions).

**Input**:
- Gross Annual Income: €50,000
- Deductible Expenses: €12,000
- Payment Frequency: Monthly

**Expected Results**:
- **Gross Income**: €50,000
- **Less Deductible Expenses**: -€12,000
- **Taxable Income**: €38,000
- **Income Tax**: €9,680
  - First €10,000 @ 9% = €900
  - Next €10,000 @ 22% = €2,200
  - Next €10,000 @ 28% = €2,800
  - Next €8,000 @ 36% = €2,880
- **Effective Income Tax Rate**: 25.47%
- **EFKA Social Security**: €10,000 (20% of gross income)
- **Total Taxes**: €19,680
- **Net Income**: €30,320
- **Effective Total Tax Rate**: 39.36%
- **VAT to Collect**: €12,000 (24%)
- **Monthly Tax Payment**: €1,640

**Tax Savings from Expenses**: By deducting €12,000 in expenses, this freelancer saves approximately €3,360 in income tax compared to not deducting any expenses.

## Understanding Greek Freelancer Taxes

Greek freelancers are subject to three main types of obligations:

### Income Tax (Progressive)

Income tax in Greece uses a progressive bracket system, meaning different portions of your income are taxed at different rates. Only the income within each bracket is taxed at that bracket's rate.

**How it works**:
1. Deductible business expenses are subtracted from gross income to determine taxable income
2. Taxable income is then split across the appropriate tax brackets
3. Each portion is taxed at its bracket's rate
4. All bracket taxes are summed for total income tax

**Key Points**:
- Higher income doesn't mean all income is taxed at the highest rate
- Deductible expenses can significantly reduce tax burden
- Effective tax rate is usually lower than the highest bracket rate

### VAT (Value Added Tax)

VAT is a 24% tax collected from clients and remitted to tax authorities.

**Important Notes**:
- VAT is **added to** your invoice amounts (not deducted from your income)
- You collect VAT from clients and pay it to the tax authority
- VAT is not part of your personal tax burden
- Example: For €10,000 in services, you invoice €12,400 (€10,000 + €2,400 VAT)
- The €10,000 is your income; the €2,400 is held in trust for the government

### EFKA Social Security

EFKA (Unified Social Security Entity) contributions provide social benefits including healthcare, pension, unemployment protection, and other social insurance.

**Structure**:
- **Main Insurance (13.33%)**: Primary social security contribution
- **Additional Contributions (6.67%)**: Healthcare, auxiliary pension, and other benefits
- **Total: 20%** of gross income

**Key Points**:
- Calculated on gross income (before expense deductions)
- Mandatory for all Greek freelancers
- Provides access to public healthcare system
- Counts toward state pension eligibility
- Cannot be reduced through expense deductions

## Tax Rates and Brackets

### Tax Rate Verification and Sources

**Last Verified**: January 15, 2024  
**Tax Year**: 2024

All tax rates in this calculator have been verified against official Greek tax authority sources:

#### Official Sources

1. **Income Tax Brackets**
   - **Source**: Law 4172/2013 (Greek Income Tax Code), Articles 9 and 15
   - **Authority**: AADE (Independent Authority for Public Revenue)
   - **URL**: [https://www.aade.gr](https://www.aade.gr)
   - **Applies to**: All individual income, including self-employed/freelancers

2. **EFKA Social Security Contributions**
   - **Source**: Law 4387/2016 (Unified Social Security System)
   - **Authority**: EFKA (e-EFKA - Unified Social Security Fund)
   - **URL**: [https://www.efka.gov.gr](https://www.efka.gov.gr)
   - **Rates**: 13.33% main insurance + 6.67% additional = 20% total
   - **Note**: Minimum monthly contributions (~€230-250/month) and income caps (~€81,000/year) exist but are not enforced by this calculator

3. **VAT (Value Added Tax)**
   - **Source**: Greek VAT Law 2859/2000, Article 21
   - **EU Directive**: 2006/112/EC
   - **Authority**: AADE (Independent Authority for Public Revenue)
   - **URL**: [https://www.aade.gr](https://www.aade.gr)
   - **Rate**: 24% (standard rate for professional services)

### Income Tax Brackets (2024)

| Taxable Income Range | Tax Rate | Tax on Bracket |
|----------------------|----------|----------------|
| €0 - €10,000 | 9% | Up to €900 |
| €10,001 - €20,000 | 22% | Up to €2,200 |
| €20,001 - €30,000 | 28% | Up to €2,800 |
| €30,001 - €40,000 | 36% | Up to €3,600 |
| €40,001 and above | 44% | Variable |

**Example Calculation for €35,000 taxable income**:
- First €10,000 × 9% = €900
- Next €10,000 × 22% = €2,200
- Next €10,000 × 28% = €2,800
- Next €5,000 × 36% = €1,800
- **Total Income Tax**: €7,700
- **Effective Rate**: 22.00%

### Other Tax Rates

| Tax Type | Rate | Applied To | Notes |
|----------|------|------------|-------|
| VAT | 24% | Gross Income | Collected from clients, remitted to authorities |
| EFKA Main | 13.33% | Gross Income | Primary social security |
| EFKA Additional | 6.67% | Gross Income | Healthcare and auxiliary benefits |
| **EFKA Total** | **20%** | **Gross Income** | **Total social security** |

### Important Rate Limitations

This calculator implements **standard rates only** and does not account for:

- **EFKA Minimum Contributions**: Low earners may owe more than calculated (~€230-250/month minimum)
- **EFKA Maximum Income Cap**: High earners may owe less than calculated (~€81,000/year cap)
- **Solidarity Contribution**: Special contribution (2.2%-10%) on income >€12,000 (suspended for 2024)
- **New Professional Rates**: Reduced EFKA rates for first 5 years of operation
- **Special Professional Categories**: Different rates for engineers, doctors, lawyers, etc.
- **Tax Credits**: Personal allowances, dependent deductions, insurance premium credits
- **Advance Tax Payments**: Προκαταβολή φόρου (prepayment obligations)
- **Professional Chamber Fees**: Mandatory fees for registered professionals

## Output Files

### File Location

Calculation results are automatically saved to text files in the **same directory** as the calculator script.

### File Naming Format

```
tax_calculation_YYYY-MM-DD_HHMMSS.txt
```

**Example**: `tax_calculation_2024-03-15_143022.txt`

### File Contents

Each output file contains:

1. **Header**: Calculation date and time
2. **Input Parameters**: Gross income, expenses, payment frequency
3. **Income Breakdown**: Gross income minus expenses
4. **Income Tax Details**: Breakdown by bracket with amounts
5. **VAT and Social Security**: Detailed contribution breakdown
6. **Payment Schedule**: Installment amounts based on chosen frequency
7. **Summary**: Total taxes, effective rates, net income
8. **Notes**: Important reminders about VAT

### File Format

Files are saved as plain text (`.txt`) with formatted columns for easy reading. You can:
- Open them with any text editor
- Print them for records
- Import into spreadsheets for further analysis
- Share with accountants or financial advisors

## Troubleshooting

### Common Issues and Solutions

#### "Python not found" or "Command not recognized"

**Problem**: Python is not installed or not in system PATH.

**Solutions**:
1. Install Python 3.6+ from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Try using `python3` instead of `python` command
4. On Windows, try `py main.py` instead

#### "Permission denied" when saving files

**Problem**: The calculator cannot write files to the current directory.

**Solutions**:
1. Run the calculator from a directory where you have write permissions
2. On Linux/Mac, check directory permissions: `ls -la`
3. Move the calculator to your home directory or Documents folder
4. On Windows, avoid running from Program Files; use Desktop or Documents instead

#### "ModuleNotFoundError: No module named 'tax_calculator'"

**Problem**: The calculator files are not in the same directory or Python can't find them.

**Solutions**:
1. Ensure both `main.py` and `tax_calculator.py` are in the same folder
2. Run the calculator from the directory containing both files
3. Use `cd` command to navigate to the correct directory before running

#### Incorrect decimal separator

**Problem**: In some locales, comma is used as decimal separator instead of period.

**Solutions**:
1. Always use period (`.`) as decimal separator: `10000.50` not `10000,50`
2. You can omit decimals for whole numbers: `10000` instead of `10000.00`
3. Don't use thousand separators when entering: `50000` not `50,000`

#### Results seem incorrect

**Problem**: Calculated amounts don't match expectations.

**Solutions**:
1. Double-check your input values
2. Remember: EFKA is calculated on **gross income** (before expenses)
3. Remember: Income tax is calculated on **taxable income** (after expenses)
4. Review the bracket breakdown to understand how progressive taxation works
5. VAT is added to invoices, not deducted from income
6. Compare your results with the examples in this README

#### Calculator crashes or freezes

**Problem**: Application stops responding.

**Solutions**:
1. Press `Ctrl+C` to exit and restart
2. Ensure you're entering numeric values only (no currency symbols)
3. Check Python version meets minimum requirement (3.6+)
4. Try running with: `python3 -u main.py` for unbuffered output

### Getting Help

If you encounter issues not covered here:

1. Check that you're using Python 3.6 or higher
2. Verify both script files are present and unmodified
3. Review error messages carefully - they often indicate the problem
4. Try running the `tax_calculator.py` module directly to test calculations:
   ```bash
   python3 tax_calculator.py
   ```

## Running Tests

This project includes a comprehensive test suite to ensure calculation accuracy and reliability. The test suite achieves **80%+ code coverage** and includes both unit tests and integration tests.

### Test Organization

The test suite is organized into three main categories:

1. **Unit Tests** (`tests/test_tax_calculator.py`, `tests/test_validators.py`)
   - Test individual functions in isolation
   - Cover edge cases and boundary conditions
   - Validate input validation and error handling
   - Test tax calculation functions with known inputs/outputs

2. **Integration Tests** (`tests/test_integration.py`)
   - Test complete workflows from input to output
   - Validate against documented examples in `sample_calculations.txt`
   - Test cross-module interactions
   - Verify file output consistency
   - Test all payment frequency options

3. **Regression Tests** (within integration tests)
   - Validate calculations against the 4 examples in `sample_calculations.txt`
   - Ensure changes don't break documented behavior
   - Serve as "golden output" verification

### Running Tests

#### Run All Tests

To run the complete test suite:

```bash
pytest
```

Or with verbose output:

```bash
pytest -v
```

#### Run Specific Test Files

Run only integration tests:

```bash
pytest tests/test_integration.py -v
```

Run only tax calculator unit tests:

```bash
pytest tests/test_tax_calculator.py -v
```

Run only validation function tests:

```bash
pytest tests/test_validators.py -v
```

#### Run Tests by Marker

Run only unit tests:

```bash
pytest -m unit -v
```

Run only integration tests:

```bash
pytest -m integration -v
```

#### Run with Coverage

To run tests with coverage reporting:

```bash
pytest --cov --cov-report=term-missing
```

This will:
- Run all tests
- Calculate code coverage percentage
- Show which lines are not covered by tests

#### Generate HTML Coverage Report

To generate a detailed HTML coverage report:

```bash
pytest --cov --cov-report=html
```

This creates a `htmlcov/` directory containing an interactive HTML report. To view it:

```bash
# On macOS/Linux
open htmlcov/index.html

# On Windows
start htmlcov/index.html
```

The HTML report shows:
- Overall coverage percentage
- Coverage by file
- Line-by-line highlighting of covered/uncovered code
- Branch coverage information

### Coverage Threshold

The project is configured to **require 80% minimum code coverage**. Test runs will fail if coverage drops below this threshold. This ensures:
- New code includes appropriate tests
- Changes don't reduce overall test quality
- Critical calculations are thoroughly validated

### Interpreting Coverage Results

**Good coverage** (current target: 80%+):
- All calculation functions have multiple test cases
- Edge cases are tested (zero, negative, boundary values)
- Error paths are validated
- File I/O operations use mocks (don't create real files)

**What's NOT covered** (and why that's OK):
- Interactive input loops in `main.py` (requires user interaction)
- `if __name__ == "__main__"` blocks (entry points)
- Some error handling branches for rare conditions
- Display formatting (visual output, hard to test meaningfully)

**Coverage gaps to investigate**:
- Functions with < 70% coverage
- Business logic (calculations) with missing test cases
- Validation functions without negative test cases
- File operations without error handling tests

### Test Configuration

Test settings are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Unit tests for individual functions",
    "integration: Integration tests for workflows"
]
addopts = [
    "--verbose",
    "--cov=.",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80"
]
```

### Continuous Testing

When developing:

1. **Before making changes**: Run tests to ensure starting point is working
   ```bash
   pytest
   ```

2. **After making changes**: Run tests to verify nothing broke
   ```bash
   pytest -v
   ```

3. **Before committing**: Check coverage is maintained
   ```bash
   pytest --cov --cov-report=term-missing
   ```

4. **Review HTML report**: Identify any uncovered code paths
   ```bash
   pytest --cov --cov-report=html
   open htmlcov/index.html
   ```

### Regression Test Examples

The integration tests validate against these documented examples from `sample_calculations.txt`:

| Example | Income | Expenses | Expected Tax | Expected Net |
|---------|--------|----------|--------------|--------------|
| 1 | €15,000 | €0 | €5,000 | €10,000 |
| 2 | €35,000 | €5,000 | €12,900 | €22,100 |
| 3 | €60,000 | €10,000 | €25,900 | €34,100 |
| 4 | €12,000 | €9,000 | €2,670 | €9,330 |

If any of these calculations produce different results, the regression tests will fail, indicating either:
- A bug was introduced in the calculation logic
- The documentation needs to be updated
- Tax rates/brackets have changed and need verification

## Legal Disclaimer

**IMPORTANT**: This calculator is provided for **estimation and planning purposes only**.

### Verification and Currency

- **Last Rate Verification**: January 15, 2024
- **Tax Year**: 2024
- **Next Recommended Review**: January 2025 or upon any tax law changes

Greek tax law changes frequently. Users should verify all rates are current before relying on calculations.

### Limitations and Exclusions

This tool implements **simplified standard rates only** and does NOT include:

#### Not Calculated:
- ❌ **EFKA minimum monthly contributions** (~€230-250/month in 2024)
- ❌ **EFKA maximum insurable income caps** (~€81,000/year in 2024)
- ❌ **Solidarity Contribution** (2.2%-10% on income >€12,000, suspended for 2024)
- ❌ **Advance tax payments** (προκαταβολή φόρου - typically 55% of previous year's tax)
- ❌ **Personal tax-free threshold adjustments**
- ❌ **Dependent allowances** (children, disabled family members)
- ❌ **Tax credits** (insurance premiums, mortgage interest, donations)
- ❌ **Professional expense percentages** (category-specific deduction rates)
- ❌ **Special professional regimes** (reduced rates for new professionals, etc.)
- ❌ **Professional chamber mandatory fees** (engineers, lawyers, doctors, etc.)
- ❌ **Municipal taxes** (ENFIA - real estate tax)
- ❌ **Withholding tax considerations**
- ❌ **VAT input deductions** (only calculates output VAT)
- ❌ **Special VAT regimes** (exempt activities, reduced rates)

#### Important Notes:
- Individual circumstances, professional categories, and special regimes may **significantly affect** actual tax obligations
- This calculator uses the **standard progressive tax system** - simplified/presumptive regimes are not included
- EFKA calculations are **simplified**: actual contributions depend on income level, years of service, and professional category

### Not a Substitute for Professional Advice

This calculator:
- ❌ Is **NOT** a substitute for professional tax advice
- ❌ Does **NOT** constitute official tax calculations
- ❌ Should **NOT** be used for official tax filing
- ❌ Does **NOT** replace consultation with certified accountants
- ❌ Is **NOT** endorsed by Greek tax authorities

### Accuracy and Liability

While we strive for accuracy based on publicly available information:
- The authors and contributors assume **NO LIABILITY** for financial decisions based on this tool
- Users are **solely responsible** for verifying all calculations
- **NO WARRANTY** of accuracy, completeness, or fitness for any particular purpose is provided
- Tax law is complex and changes frequently - **always verify current rates**
- Individual tax situations vary - **calculations are estimates only**
- Use **ENTIRELY AT YOUR OWN RISK**

### Critical Recommendations

**Before making any financial or tax decisions:**

1. ✅ **Consult a certified Greek tax accountant (λογιστής/λογίστρια)**
   - Required for official tax filing
   - Can identify deductions and credits specific to your situation
   - Stays current with tax law changes

2. ✅ **Verify current rates with official sources**
   - Tax rates and brackets can change mid-year
   - Special legislation may introduce temporary changes
   - Professional category rules may apply

3. ✅ **Use official platforms for tax filing**
   - Taxisnet: [www.gsis.gr](https://www.gsis.gr)
   - AADE myDATA: Digital submission system
   - Only official platforms are legally valid

4. ✅ **Keep detailed records**
   - Maintain all receipts for deductible expenses
   - Document all income and VAT collected
   - Prepare for potential audits

### Official Resources

For **authoritative and current** information, consult:

- **Greek Tax Authority (AADE)**  
  Website: [www.aade.gr](https://www.aade.gr)  
  Information: Tax rates, brackets, filing requirements

- **Taxisnet Portal (Official Tax Filing)**  
  Website: [www.gsis.gr](https://www.gsis.gr)  
  Use: Official tax return submission

- **EFKA (Social Security)**  
  Website: [www.efka.gov.gr](https://www.efka.gov.gr)  
  Information: Contribution rates, minimum payments, coverage

- **Greek Government Gazette (ΦΕΚ)**  
  Website: [www.et.gr](https://www.et.gr)  
  Use: Official publication of all tax laws and amendments

### Updates and Corrections

If you identify any discrepancies between this calculator and official Greek tax sources:
- Tax rates in this calculator were last verified on **January 15, 2024**
- Tax law changes after this date are **not reflected**
- Please verify all information against current official sources
- Consider contributing corrections with official source citations

## Contributing

Contributions are welcome! If you find bugs, have suggestions, or want to improve the calculator:

1. Test the calculator thoroughly
2. Document any issues with specific examples
3. Suggest improvements with clear rationale
4. Provide updated tax rates with official sources

### Reporting Issues

When reporting problems, please include:
- Python version (`python3 --version`)
- Operating system
- Complete error message
- Steps to reproduce
- Input values used

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Tax Rates Last Verified**: January 15, 2024  
**Tax Year**: 2024  
**License**: Open source

*This calculator is an educational tool and community resource for Greek freelancers. Tax rates have been verified against official sources as of January 15, 2024. For official tax compliance, always consult qualified professionals and verify current rates with official government resources (AADE, EFKA, Taxisnet).*
