import pandas as pd
from selenium import webdriver
import time

class LinkedInConnections:
    def __init__(self, username, password):
        self.driver_path = './chromedriver'
        self.target_website = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome(self.driver_path)
        self.first_degree_df = None
        self.second_degree_df = None

    def _login(self):
        """
        Login LinkedIn using provided username and password and navigate to connection page

        :return:
        """
        self.driver.get(self.target_website)
        self.driver.find_element_by_xpath("//input[@id='username']").send_keys(self.username)
        self.driver.find_element_by_xpath("//input[@id='password']").send_keys(self.password)
        self.driver.find_element_by_xpath("//button[@type='submit']").click()
        self.driver.find_element_by_xpath("//div[@data-control-name='identity_welcome_message']").click()
        time.sleep(5)
        self.driver.find_element_by_xpath("//a[@data-control-name='topcard_view_all_connections']").click()

    def _scroll_down(self, speed=2):
        """
        Scroll down the the end of the page with a speed, default 4

        :param speed: speed to scroll down
        :return:
        """
        current_scroll_position, new_height = 0, 1
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            self.driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = self.driver.execute_script("return document.body.scrollHeight")

    def _next_clickable(self):
        """
        Check if the next button is clickable or not

        :return: bool
        """
        try:
            return self.driver.find_element_by_xpath("//button[@aria-label='Next']").is_enabled()
        except:
            return False

    def _go_next_page(self):
        """
        Go to next page

        :return:
        """
        self.driver.find_element_by_xpath("//button[@aria-label='Next']").click()

    def _extract_connection_info(self, get_mutual=True):
        """
        Extract name, profile page url
        and mutual friends url for every connection in the connection page

        :param get_mutual: flag to determine whether to extract mutual connection urls
        :return: list of lists
        """
        res = list()

        while True:
            self._scroll_down()

            search_results = self.driver.find_elements_by_class_name("search-result__wrapper")
            for wrapper in search_results:
                wrapper_info = list()
                wrapper_info.append(wrapper.find_element_by_xpath(".//span[@class='name actor-name']").text)
                wrapper_info.append(wrapper.find_element_by_xpath(".//a[@data-control-name='search_srp_result']").get_attribute('href'))

                if get_mutual:
                    try:
                        wrapper_info.append(wrapper.find_element_by_xpath(".//a[@data-control-name='view_mutual_connections']").get_attribute('href'))
                    except:
                        try:
                            wrapper_info.append([[i.text, i.get_attribute('href')]
                                                 for i in wrapper.find_elements_by_xpath(".//a[@data-control-name='view_mutual_connection_profile']")])
                        except:
                            wrapper_info.append(None)

                res.append(wrapper_info)

            if not self._next_clickable():
                break
            else:
                time.sleep(2)
                self._go_next_page()
                time.sleep(2)

        return res

    def _extract_mutual_connection(self, url):
        """
        Extract mutual connections from a url in connection_url column

        :param url: 1 connection url
        :return: list of list
        """
        self.driver.get(url)
        return self._extract_connection_info(get_mutual=False)

    def _extract_first_degree(self):
        """
        Extract first degree connections and their connection urls

        :return:
        """
        self.first_degree_df = pd.DataFrame(self._extract_connection_info(),
                                            columns=['name', 'url', 'connection_url'])

    def _extract_second_degree(self):
        """
        Extract second degree connections if the connection url is a str

        :return:
        """
        second_degree_df = self.first_degree_df.copy()
        second_degree_df['connection_url'] = second_degree_df['connection_url'].apply(lambda x: x if isinstance(x, list) else self._extract_mutual_connection(x))
        self.second_degree_df = second_degree_df

    def _generate_final_df(self):
        """
        process the second degree df and get ready to output the results

        :return:
        """

        #TODO

    def crawl(self):
        """
        Main crawl function

        :return:
        """
        self._login()
        self._extract_first_degree()
        # self._extract_second_degree()
        # self.driver.quit()