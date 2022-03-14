# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt
import time

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": mars_hemisphere_data(browser)
    }
    
    # Stop webdriver and return data
    browser.quit()
    return data
# browser varaible as arguemnt needed to automate
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)


    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    try:
        
        slide_elem = news_soup.select_one('div.list_text')

        # slide_elem.find('div', class_='content_title')


        # Use the parent element to find the first a tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()


        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
         # handles errors that may occur froms craping      
    except AttributeError:
        return None, None

    return news_title, news_p



# ### JPL Space Images Featured Image

def featured_image(browser):  
    # Visit URL
    url =  'https://spaceimages-mars.com'
    browser.visit(url)



    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()


    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    img_soup
    try:

        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        img_url_rel
    except AttributeError:
        return None


    # Use the base url to create an absolute url
    base_url = 'https://spaceimages-mars.com/'
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url


# ### Mars Facts
def mars_facts():
    try:    
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None 
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    return df.to_html(classes="table table-striped")

# #  Scrape High-Resolution Mars’ Hemisphere Images and Titles

# ### Hemispheres
def mars_hemisphere_data(browser):

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []
   
    #Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url + 'index.html')
    for i in range(4):
        # Find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item img")[i].click()
        hemi_data = scrape_hemisphere(browser.html)
        hemi_data['img_url'] = url + hemi_data['img_url']
        # Append hemisphere object to list
        hemisphere_image_urls.append(hemi_data)
        # Finally, we navigate backwards
        browser.back()

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    #loop through scraped data
    """
    try:
     for i in list(range(len(mars_info_container))):
        header = mars_info_container[i].find('h3').get_text()
        article_partial_url = mars_info_container[i].find('a').get('href')
        article_full_url = f'{base_url}{article_partial_url}'
        browser.visit(article_full_url)
        html = browser.html
        image_parse = soup(html,'html.parser')
        image_url = image_parse.select_one('ul li  a').get('href')
        hemisphere_image_urls.append({'img_url': image_url,'title':header})
        time.sleep(.04)
    except AttributeError:
        return None
    """

    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    # parse html text
    hemi_soup = soup(html_text, "html.parser")
    # adding try/except for error handling
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")
    except AttributeError:
        # Image error will return None, for better front-end handling
        title_elem = None
        sample_elem = None
    hemispheres = {
        "title": title_elem,
        "img_url": sample_elem
    }
    return hemispheres
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())





