import asyncio
import sys
import os
import pandas as pd
from scraper import InstagramScraper
from utils import is_valid_reel_url
from excel import export_to_excel

async def main():
    print("\n--- Instagram Reel Scraper (Excel Input) ---")
    
    # Check for cookies.json
    if not os.path.exists('cookies.json'):
        print("Error: 'cookies.json' not found. Please create it with your Instagram session cookies.")
        return

    # Prompt user for Excel file path
    excel_path = input("Enter the path to the Excel file (.xlsx): ").strip()
    
    if not os.path.exists(excel_path):
        print(f"Error: File '{excel_path}' not found.")
        return

    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        if 'link' not in df.columns:
            print("Error: Excel file must contain a column named 'link'.")
            return
        
        links = df['link'].dropna().tolist()
        if not links:
            print("Error: No links found in the 'link' column.")
            return

        first_link = links[0]
        last_link = links[-1]
        
        print(f"First link (oldest): {first_link}")
        print(f"Last link (latest): {last_link}")

        if not is_valid_reel_url(first_link) or not is_valid_reel_url(last_link):
            print("Error: One or more links in the Excel file are invalid Instagram Reel URLs.")
            return

        scraper = InstagramScraper(cookies_path='cookies.json')
        
        try:
            # Initialize browser
            await scraper.init_browser(headless=True)
            
            # 1. Extract reel info (username) from the first link
            print("Extracting profile info from the first link...")
            username, _ = await scraper.get_reel_info(first_link)
            print(f"Username: {username}")
            
            # 2. Visit profile and scrape reels from last_link down to first_link
            print(f"Collecting reels from @{username} between the specified links...")
            # Note: scrape_profile_reels takes (username, target_reel_url, last_reel_url)
            # target_reel_url is where it STOPS (the oldest one)
            # last_reel_url is where it STARTS collecting (the latest one)
            reels_data = await scraper.scrape_profile_reels(username, first_link, last_link)
            
            # 3. Export to Excel
            output_filename = 'reels_output_from_excel.xlsx'
            print(f"Processing {len(reels_data)} reels...")
            success = export_to_excel(reels_data, output_filename)
            
            if success:
                print(f"\nDone! Results saved to '{output_filename}'.")
                print(f"Total reels collected: {len(reels_data)}")
            else:
                print("\nFailed to export results.")
                
        except Exception as e:
            print(f"\nAn error occurred during scraping: {e}")
        finally:
            await scraper.close()

    except Exception as e:
        print(f"\nAn error occurred reading the Excel file: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(0)
