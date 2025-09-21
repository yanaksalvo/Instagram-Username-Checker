import requests
import time
import random
import json
from typing import List, Dict, Tuple
from datetime import datetime
import logging
from urllib.parse import quote

class InstagramUsernameChecker:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.available_usernames = []
        self.unavailable_usernames = []
        self.errors = []
        
    def setup_session(self):
        """Setup session with headers to mimic a real browser"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def random_delay(self, min_seconds: float = 2.0, max_seconds: float = 5.0):
        """Add random delay between requests to avoid spam detection"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def check_username_via_profile(self, username: str) -> Tuple[bool, str]:
        """
        Check username availability by trying to access the profile page
        Returns: (is_available, status_message)
        """
        try:
            url = f"https://www.instagram.com/{username}/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 404:
                return True, "Available (404)"
            elif response.status_code == 200:
                try:
                    # Check if it's actually a valid profile or Instagram's "user not found" page
                    content = response.text.lower()
                    
                    # Strong indicators that profile exists (user data present)
                    taken_indicators = [
                        f'"username":"{username.lower()}"',
                        '"edge_followed_by":{',
                        '"edge_follow":{', 
                        '"biography":"',
                        '"profile_pic_url_hd":"',
                        '"full_name":"',
                        '"is_verified":true',
                        '"is_private":true',
                        '"is_private":false'
                    ]
                    
                    # Strong indicators that profile doesn't exist
                    not_found_indicators = [
                        "sorry, this page isn't available",
                        "the link you followed may be broken", 
                        '"user":null',
                        '"graphql":{"user":null}',
                        'window.__additionalDataLoaded'
                    ]
                    
                    has_user_data = any(indicator in content for indicator in taken_indicators)
                    has_not_found = any(indicator in content for indicator in not_found_indicators)
                    
                    # Content length heuristic - Instagram's "not found" pages are much smaller
                    content_length = len(content)
                    
                    if has_user_data:
                        return False, "Taken"
                    elif has_not_found or content_length < 50000:
                        return True, "Available"
                    else:
                        # Default to available for unclear cases with small content
                        return True, "Available (unclear)"
                        
                except UnicodeDecodeError:
                    return None, "Unicode decode error"
            else:
                return None, f"HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return None, f"Network error: {str(e)}"
    
    def check_username_via_signup_api(self, username: str) -> Tuple[bool, str]:
        """
        Check username using Instagram's signup validation API
        Returns: (is_available, status_message)  
        """
        try:
            # Use Instagram's signup API to check username availability
            url = "https://www.instagram.com/api/v1/users/check_username/"
            
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': 'missing',
                'Referer': 'https://www.instagram.com/accounts/signup/',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            data = {
                'username': username
            }
            
            response = self.session.post(url, data=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Instagram returns different responses for available/taken usernames
                    if 'available' in result:
                        if result['available']:
                            return True, "Available (API)"
                        else:
                            return False, "Taken (API)"
                    elif 'errors' in result:
                        if 'username' in result['errors']:
                            return False, "Taken (validation error)"
                        
                except json.JSONDecodeError:
                    pass
                    
            return None, f"API check failed ({response.status_code})"
                
        except requests.exceptions.RequestException as e:
            return None, f"Network error: {str(e)}"
    
    def check_single_username(self, username: str) -> Dict:
        """Check a single username using multiple methods"""
        print(f"Checking: {username}")
        
        # Clean username
        username = username.strip().lower()
        
        # Validate username format
        if not username or len(username) < 1 or len(username) > 30:
            result = {
                'username': username,
                'available': False,
                'status': 'Invalid format',
                'method': 'validation'
            }
            self.errors.append(result)
            return result
        
        # Try signup API method first (more reliable)
        is_available, status = self.check_username_via_signup_api(username)
        
        if is_available is None:
            # If API method failed, try profile method
            self.random_delay(1, 2)
            is_available, status = self.check_username_via_profile(username)
        
        result = {
            'username': username,
            'available': is_available if is_available is not None else False,
            'status': status,
            'method': 'instagram_check',
            'timestamp': datetime.now().isoformat()
        }
        
        if is_available is True:
            self.available_usernames.append(result)
            print(f"+ {username} - AVAILABLE")
        elif is_available is False:
            self.unavailable_usernames.append(result)
            print(f"- {username} - TAKEN")
        else:
            self.errors.append(result)
            print(f"? {username} - ERROR: {status}")
        
        return result
    
    def check_usernames_from_file(self, filename: str) -> List[Dict]:
        """Check usernames from a text file (one per line)"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                usernames = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []
        
        return self.check_usernames_list(usernames)
    
    def check_usernames_list(self, usernames: List[str]) -> List[Dict]:
        """Check a list of usernames"""
        results = []
        total = len(usernames)
        
        print(f"Checking {total} usernames...\n")
        
        for i, username in enumerate(usernames, 1):
            print(f"Progress: {i}/{total}")
            result = self.check_single_username(username)
            results.append(result)
            
            # Add delay between requests to avoid spam detection
            if i < total:
                self.random_delay(2, 4)
        
        return results
    
    def save_results(self, output_prefix: str = "instagram_check"):
        """Save results to separate files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save available usernames
        if self.available_usernames:
            available_file = f"{output_prefix}_available_{timestamp}.txt"
            with open(available_file, 'w', encoding='utf-8') as f:
                f.write("AVAILABLE USERNAMES\n")
                f.write("=" * 50 + "\n\n")
                for result in self.available_usernames:
                    f.write(f"{result['username']}\n")
            print(f"\n+ Available usernames saved to: {available_file}")
        
        # Save unavailable usernames
        if self.unavailable_usernames:
            unavailable_file = f"{output_prefix}_unavailable_{timestamp}.txt"
            with open(unavailable_file, 'w', encoding='utf-8') as f:
                f.write("UNAVAILABLE USERNAMES\n")
                f.write("=" * 50 + "\n\n")
                for result in self.unavailable_usernames:
                    f.write(f"{result['username']} - {result['status']}\n")
            print(f"- Unavailable usernames saved to: {unavailable_file}")
        
        # Save detailed results as JSON
        all_results = {
            'available': self.available_usernames,
            'unavailable': self.unavailable_usernames,
            'errors': self.errors,
            'summary': {
                'total_checked': len(self.available_usernames) + len(self.unavailable_usernames) + len(self.errors),
                'available_count': len(self.available_usernames),
                'unavailable_count': len(self.unavailable_usernames),
                'error_count': len(self.errors)
            }
        }
        
        json_file = f"{output_prefix}_detailed_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"* Detailed results saved to: {json_file}")
    
    def print_summary(self):
        """Print summary of results"""
        total = len(self.available_usernames) + len(self.unavailable_usernames) + len(self.errors)
        
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Total checked: {total}")
        print(f"Available: {len(self.available_usernames)}")
        print(f"Unavailable: {len(self.unavailable_usernames)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.available_usernames:
            print(f"\nAvailable usernames:")
            for result in self.available_usernames:
                print(f"  • {result['username']}")


def main():
    """Main function to run the username checker"""
    import sys
    
    print("Instagram Username Availability Checker")
    print("=" * 50)
    
    checker = InstagramUsernameChecker()
    
    # Check if running interactively
    if sys.stdin.isatty():
        print("Choose an option:")
        print("1. Check usernames from file (usernames.txt)")
        print("2. Enter usernames manually")
        
        try:
            choice = input("Enter choice (1 or 2): ").strip()
            
            if choice == "1":
                filename = input("Enter filename (default: usernames.txt): ").strip() or "usernames.txt"
                results = checker.check_usernames_from_file(filename)
            elif choice == "2":
                usernames_input = input("Enter usernames separated by commas: ")
                usernames = [u.strip() for u in usernames_input.split(",") if u.strip()]
                results = checker.check_usernames_list(usernames)
            else:
                print("Invalid choice!")
                return
        except EOFError:
            print("Running in non-interactive mode, checking usernames.txt")
            results = checker.check_usernames_from_file("usernames.txt")
    else:
        # Non-interactive mode, check from file
        results = checker.check_usernames_from_file("usernames.txt")
    
    if results:
        checker.print_summary()
        checker.save_results()
    else:
        print("No usernames were checked.")


if __name__ == "__main__":
    main()