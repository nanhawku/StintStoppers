"""
Test CVD Risk Predictions
Tests the API with various patient profiles to verify predictions
"""

import requests
import json
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

API_URL = 'http://localhost:5000'

def load_test_cases():
    """Load test cases from JSON file"""
    with open('cvd_test_cases.json', 'r') as f:
        return json.load(f)

def test_api_health():
    """Check if API is healthy"""
    try:
        response = requests.get(f'{API_URL}/health')
        health = response.json()

        if health['status'] == 'healthy' and health['model_loaded']:
            print(f"{Fore.GREEN}✓ API is healthy and model is loaded{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}✗ API is not ready{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}✗ Cannot connect to API: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure to run: python3 api_server.py{Style.RESET_ALL}")
        return False

def test_prediction(test_case):
    """Test a single prediction case"""
    name = test_case['name']
    description = test_case['description']
    expected = test_case['expected_result']
    data = test_case['data']

    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Test: {name}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{description}{Style.RESET_ALL}")
    print(f"Expected Result: {Fore.YELLOW}{expected}{Style.RESET_ALL}")

    # Show key metrics
    print(f"\nKey Metrics:")
    print(f"  Age: {data['age']} | EF: {data['ejection_fraction']}% | Creatinine: {data['serum_creatinine']}")

    try:
        response = requests.post(f'{API_URL}/predict', json=data)
        result = response.json()

        if result.get('success'):
            actual = result['cvd_risk']
            probability = result['risk_percentage']
            risk_level = result['risk_level']

            # Check if prediction matches expectation
            if actual == expected:
                status = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}"
            else:
                status = f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"

            print(f"\n{status}")
            print(f"Actual Result: {Fore.YELLOW}{actual}{Style.RESET_ALL}")
            print(f"Risk Level: {risk_level}")
            print(f"Probability: {probability}")

            return actual == expected
        else:
            print(f"{Fore.RED}✗ API Error: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
            return False

    except Exception as e:
        print(f"{Fore.RED}✗ Request failed: {e}{Style.RESET_ALL}")
        return False

def run_all_tests():
    """Run all test cases"""
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"CVD RISK PREDICTION TEST SUITE")
    print(f"{'='*80}{Style.RESET_ALL}\n")

    # Check API health first
    if not test_api_health():
        return

    # Load test cases
    test_data = load_test_cases()

    results = {
        'high_risk': {'passed': 0, 'failed': 0},
        'low_risk': {'passed': 0, 'failed': 0}
    }

    # Test high risk cases
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"HIGH RISK TEST CASES (Expected: YES)")
    print(f"{'='*80}{Style.RESET_ALL}")

    for test_case in test_data['test_cases']['high_risk_cases']:
        if test_prediction(test_case):
            results['high_risk']['passed'] += 1
        else:
            results['high_risk']['failed'] += 1

    # Test low risk cases
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"LOW RISK TEST CASES (Expected: NO)")
    print(f"{'='*80}{Style.RESET_ALL}")

    for test_case in test_data['test_cases']['low_risk_cases']:
        if test_prediction(test_case):
            results['low_risk']['passed'] += 1
        else:
            results['low_risk']['failed'] += 1

    # Print summary
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}{Style.RESET_ALL}\n")

    total_passed = results['high_risk']['passed'] + results['low_risk']['passed']
    total_failed = results['high_risk']['failed'] + results['low_risk']['failed']
    total_tests = total_passed + total_failed

    print(f"High Risk Cases: {Fore.GREEN}{results['high_risk']['passed']} passed{Style.RESET_ALL}, "
          f"{Fore.RED}{results['high_risk']['failed']} failed{Style.RESET_ALL}")
    print(f"Low Risk Cases:  {Fore.GREEN}{results['low_risk']['passed']} passed{Style.RESET_ALL}, "
          f"{Fore.RED}{results['low_risk']['failed']} failed{Style.RESET_ALL}")
    print(f"\nTotal: {Fore.GREEN}{total_passed}/{total_tests} tests passed{Style.RESET_ALL}")

    if total_failed == 0:
        print(f"\n{Fore.GREEN}{'='*80}")
        print(f"🎉 ALL TESTS PASSED! 🎉")
        print(f"{'='*80}{Style.RESET_ALL}\n")
    else:
        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"⚠️  Some tests failed - Review results above")
        print(f"{'='*80}{Style.RESET_ALL}\n")

if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}Error: cvd_test_cases.json not found{Style.RESET_ALL}")
        print(f"Make sure you're running this from the correct directory")
