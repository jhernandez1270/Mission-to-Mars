# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_images(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

   # Visit the mars nasa news site
   url = 'https://redplanetscience.com/'
   browser.visit(url)

   # Optional delay for loading the page
   browser.is_element_present_by_css('div.list_text', wait_time=1)

   # Convert the browser html to a soup object and then quit the browser
   html = browser.html
   news_soup = soup(html, 'html.parser')

   # Add try/except for error handling
   try:
       slide_elem = news_soup.select_one('div.list_text')
       # Use the parent element to find the first 'a' tag and save it as 'news_title'
       news_title = slide_elem.find('div', class_='content_title').get_text()
       # Use the parent element to find the paragraph text
       news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

   except AttributeError:
       return None, None

   return news_title, news_p



#    slide_elem = news_soup.select_one('div.list_text')
#    slide_elem.find('div', class_='content_title')

#    # Use the parent element to find the first <a> tag and save it as  `news_title`
#    news_title = slide_elem.find('div', class_='content_title').get_text()
#    news_title

#    # Use the parent element to find the paragraph text
#    news_p = slide_elem.find('div', class_='article_teaser_body').get_text()



def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes=["table", "table-bordered", "table-striped"])

def hemisphere_images(browser):
    # 1. Use browser to visit the URL
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hemi_soup = soup(html, 'html.parser')

    # find the relative image urls
    relative_links = []
    for a in hemi_soup.find_all('a', class_='itemLink product-item'):
        relative_links.append(a['href'])

    # Use the base url to create an absolute url for each image
    absolute_links = []
    for link in relative_links:
        absolute_links.append(f'https://marshemispheres.com/{link}')
        # print(absolute_links)

    for abs_link in absolute_links:
        hemispheres = {}
        # Click on the Link
        browser.visit(abs_link)

        indi_hemi_pg = browser.html
        # Parse the Individual Hemisphere page
        indi_hemi_soup = soup(indi_hemi_pg, 'html.parser')

        # Find the Full resolution image link
        try:
            full_res_rel_link = indi_hemi_soup.find('a', target='_blank', text='Sample').get('href')
            full_res_abs_link = f'https://marshemispheres.com/{full_res_rel_link}'
            # Get the title
            title = indi_hemi_soup.find('h2', class_='title').text
        except Exception as e:
            print(e)

        

        # Add the image url and title to hemisphere dict
        hemispheres["img_url"] = full_res_abs_link
        hemispheres["title"] = title

        # Check if the hemisphere is in the list, if so, skip, if not, add to the lis
        if hemispheres in hemisphere_image_urls:
            print("skipping...")
        else:
            print("adding hemisphere image and url... ")
            hemisphere_image_urls.append(hemispheres)

    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())