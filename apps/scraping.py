from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt


def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }
    # Quit browser in case it's not in headless mode
    browser.quit()
    return data
    
#### Mars News
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    
    return news_title, news_p

##### Featured Images
def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()
    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
        # Use the base URL to create an absolute URL
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    except AttributeError:
        return None
    
    return img_url

##### Mars Facts
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Value']
    # Convert dataframe into HTML format
    
    return df.to_html(index=False)
    
#### Hemisphere Mars Images
def hemisphere_image():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # Parse the resulting html with soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    # Find hemisphere pages links, parse, and store them in the list
    hemi_links = soup.find_all("div", class_="item")
    # Declare list to store hemisphere pages links
    hemi_page_links = []
    for hemi_link in hemi_links:
        # Parse relative URL address
        relative_link = hemi_link.find("a")["href"]
        # Use the base URL to create an absolute URL
        absolute_link = f'https://astrogeology.usgs.gov{relative_link}'
        hemi_page_links.append(absolute_link)    
        # Declare dictionary to hold correcponding data for each image
        img_dic = {}
    # Click through four hemisphere pages and parse data
    for hemi_page_link in hemi_page_links:
        # Open the page for each hemisohere image
        browser.visit(hemi_page_link)
        # Parse the resulting html with soup
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        # Declare list lement iterator
        i = hemi_page_links.index(hemi_page_link)
        try:
            # Parse image title with soup
            img_title = soup.find("h2", class_="title").get_text()
            # Parse sample image URL with soup
            img_url = soup.find("a", text="Sample").get("href")
            # Add image URL and title to image dictionary
            img_dic.update({"Img_title"+str(i) : img_title})
            img_dic.update({"Img_url"+str(i) : img_url})
        except AttributeError:
            return None, None
    # Quit browser in case it's not in headless mode
    browser.quit()
    return img_dic


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
    print(hemisphere_image())