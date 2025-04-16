
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os
from datetime import datetime

class ClinicalTrialsScraper:
    """
    Scraper for UT Southwestern Medical Center's StudyFinder clinical trials database.
    """
    
    def __init__(self, base_url="https://clinicaltrials.utswmed.org"):
        """Initialize the scraper with the base URL."""
        self.base_url = base_url
        self.studies_url = f"{base_url}/studies"
        self.session = requests.Session()
        self.all_studies = []
        
    def get_total_pages(self):
        """Get the total number of pages to scrape."""
        response = self.session.get(self.studies_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        try:
            # Find the last page number from pagination
            pagination = soup.select('.pagination li:not(.disabled) a')
            if pagination:
                # Get the highest page number
                page_numbers = [int(a.text) for a in pagination if a.text.isdigit()]
                return max(page_numbers) if page_numbers else 1
            return 1
        except Exception as e:
            print(f"Error determining total pages: {e}")
            return 1
    
    def parse_study(self, study_element):
        """Parse a single study element and extract relevant information."""
        study_data = {}
        
        # Extract title
        title_elem = study_element.find('h4')
        if title_elem:
            study_data['title'] = title_elem.text.strip()
        
        # Extract description
        desc_elem = study_element.find('div', {'data-attribute-name': 'simple_description'})
        if desc_elem and desc_elem.find('p'):
            study_data['description'] = desc_elem.find('p').text.strip()
        
        # Extract other basic attributes
        attributes = [
            'contacts', 'principal_investigator', 'gender', 'age', 'phase',
            'healthy_volunteers', 'system_id', 'irb_number', 'interventions',
            'conditions', 'keywords', 'sites'
        ]
        
        for attr in attributes:
            elem = study_element.find('div', {'data-attribute-name': attr})
            if elem:
                # Remove the label and get only the value
                label = elem.find('label')
                if label:
                    label.extract()  # Remove the label element
                
                # Get the text from span if it exists, otherwise get all text
                span = elem.find('span')
                if span:
                    study_data[attr] = span.get_text(strip=True)
                else:
                    study_data[attr] = elem.get_text(strip=True)
        
        # Extract eligibility criteria
        eligibility_elem = study_element.find('div', {'class': 'eligibility-criteria'})
        if eligibility_elem:
            # Find inclusion criteria
            inclusion_header = eligibility_elem.find('div', string=lambda text: text and 'Inclusion Criteria' in text)
            if inclusion_header:
                inclusion_text = []
                for sibling in inclusion_header.next_siblings:
                    if sibling.name == 'hr':
                        break
                    inclusion_text.append(sibling.get_text(strip=True) if hasattr(sibling, 'get_text') else str(sibling).strip())
                study_data['inclusion_criteria'] = ' '.join([t for t in inclusion_text if t])
            
            # Find exclusion criteria
            exclusion_header = eligibility_elem.find('div', string=lambda text: text and 'Exclusion Criteria' in text)
            if exclusion_header:
                exclusion_text = []
                for sibling in exclusion_header.next_siblings:
                    if sibling.name == 'hr':
                        break
                    exclusion_text.append(sibling.get_text(strip=True) if hasattr(sibling, 'get_text') else str(sibling).strip())
                study_data['exclusion_criteria'] = ' '.join([t for t in exclusion_text if t])
                
        return study_data
    
    def scrape_page(self, page_num):
        """Scrape a single page of study listings."""
        url = f"{self.studies_url}?page={page_num}"
        print(f"Scraping page {page_num}: {url}")
        
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all study elements on the page
            study_elements = soup.select('.study')
            page_studies = []
            
            for study_elem in study_elements:
                study_data = self.parse_study(study_elem)
                if study_data:
                    page_studies.append(study_data)
                    
            return page_studies
            
        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")
            return []
    
    def scrape_all_studies(self, max_pages=None):
        """Scrape all studies across all pages."""
        total_pages = self.get_total_pages()
        print(f"Found {total_pages} pages to scrape")
        
        if max_pages and max_pages < total_pages:
            total_pages = max_pages
            print(f"Limiting to {max_pages} pages as requested")
        
        for page_num in range(1, total_pages + 1):
            page_studies = self.scrape_page(page_num)
            self.all_studies.extend(page_studies)
            
            # Be nice to the server
            time.sleep(1)
            
        print(f"Scraped a total of {len(self.all_studies)} studies")
        return self.all_studies
    
    def save_to_csv(self, filename=None):
        """Save the scraped studies to a CSV file."""
        if not self.all_studies:
            print("No studies to save. Run scrape_all_studies() first.")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clinical_trials_{timestamp}.csv"
        
        df = pd.DataFrame(self.all_studies)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Saved {len(self.all_studies)} studies to {filename}")
        
        return filename
    
    def save_to_json(self, filename=None):
        """Save the scraped studies to a JSON file."""
        if not self.all_studies:
            print("No studies to save. Run scrape_all_studies() first.")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clinical_trials_{timestamp}.json"
        
        df = pd.DataFrame(self.all_studies)
        df.to_json(filename, orient='records', indent=4)
        print(f"Saved {len(self.all_studies)} studies to {filename}")
        
        return filename

# Example usage
if __name__ == "__main__":
    scraper = ClinicalTrialsScraper()
    
    # Scrape all studies (or limit with max_pages parameter)
    scraper.scrape_all_studies(max_pages=3)  # Limit to 3 pages for testing
    
    # Save results
    scraper.save_to_csv()
    scraper.save_to_json()
